# Copyright (c) 2023-present Plane Software, Inc. and contributors
# SPDX-License-Identifier: AGPL-3.0-only
# See the LICENSE file for details.

"""
Clerk JWT Authentication Middleware

This middleware validates JWT tokens issued by Clerk and authenticates users
based on the token claims. It supports both session-based and token-based
authentication, allowing for a gradual migration from the existing auth system.
"""

import json
import logging
import time
from functools import lru_cache
from typing import Optional, Tuple

import jwt
import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger(__name__)

User = get_user_model()


class ClerkJWKSClient:
    """
    Client for fetching and caching Clerk's JWKS (JSON Web Key Set).
    The JWKS is used to verify JWT signatures.
    """

    def __init__(self, clerk_domain: str, cache_ttl: int = 3600):
        self.clerk_domain = clerk_domain.rstrip("/")
        self.cache_ttl = cache_ttl
        self._jwks_cache = None
        self._cache_timestamp = 0

    def get_jwks(self) -> dict:
        """Fetch JWKS from Clerk, with caching."""
        current_time = time.time()

        # Return cached JWKS if still valid
        if self._jwks_cache and (current_time - self._cache_timestamp) < self.cache_ttl:
            return self._jwks_cache

        try:
            jwks_url = f"{self.clerk_domain}/.well-known/jwks.json"
            response = requests.get(jwks_url, timeout=10)
            response.raise_for_status()
            self._jwks_cache = response.json()
            self._cache_timestamp = current_time
            return self._jwks_cache
        except requests.RequestException as e:
            logger.error(f"Failed to fetch JWKS from Clerk: {e}")
            # Return cached version if available, even if expired
            if self._jwks_cache:
                return self._jwks_cache
            raise

    def get_signing_key(self, kid: str) -> Optional[dict]:
        """Get the signing key for a specific key ID."""
        jwks = self.get_jwks()
        for key in jwks.get("keys", []):
            if key.get("kid") == kid:
                return key
        return None


@lru_cache(maxsize=1)
def get_jwks_client() -> Optional[ClerkJWKSClient]:
    """Get or create the JWKS client singleton."""
    clerk_domain = getattr(settings, "CLERK_DOMAIN", None)
    if not clerk_domain:
        return None
    return ClerkJWKSClient(clerk_domain)


def verify_clerk_token(token: str) -> Tuple[bool, Optional[dict], Optional[str]]:
    """
    Verify a Clerk JWT token.

    Returns:
        Tuple of (is_valid, claims, error_message)
    """
    jwks_client = get_jwks_client()
    if not jwks_client:
        return False, None, "Clerk is not configured"

    try:
        # Decode header to get key ID
        unverified_header = jwt.get_unverified_header(token)
        kid = unverified_header.get("kid")

        if not kid:
            return False, None, "Token missing key ID"

        # Get the signing key
        signing_key = jwks_client.get_signing_key(kid)
        if not signing_key:
            return False, None, "Signing key not found"

        # Build the public key from JWKS
        public_key = jwt.algorithms.RSAAlgorithm.from_jwk(json.dumps(signing_key))

        # Verify and decode the token
        claims = jwt.decode(
            token,
            public_key,
            algorithms=["RS256"],
            options={
                "verify_signature": True,
                "verify_exp": True,
                "verify_nbf": True,
                "verify_iat": True,
            },
        )

        return True, claims, None

    except jwt.ExpiredSignatureError:
        return False, None, "Token has expired"
    except jwt.InvalidTokenError as e:
        return False, None, f"Invalid token: {str(e)}"
    except Exception as e:
        logger.exception(f"Error verifying Clerk token: {e}")
        return False, None, f"Token verification failed: {str(e)}"


class ClerkJWTAuthenticationMiddleware(MiddlewareMixin):
    """
    Middleware that authenticates requests using Clerk JWT tokens.

    This middleware:
    1. Checks for a Bearer token in the Authorization header
    2. Verifies the token using Clerk's JWKS
    3. Looks up or creates the user based on the token claims
    4. Sets request.user to the authenticated user

    If no token is present or Clerk is disabled, the middleware passes
    through to allow other authentication methods (like session auth).
    """

    def __init__(self, get_response):
        super().__init__(get_response)
        self.enable_clerk = getattr(settings, "ENABLE_CLERK_AUTH", False)

    def process_request(self, request):
        """Process the request and authenticate if a Clerk token is present."""
        # Skip if Clerk auth is not enabled
        if not self.enable_clerk:
            return None

        # Get the Authorization header
        auth_header = request.META.get("HTTP_AUTHORIZATION", "")

        # Check for Bearer token
        if not auth_header.startswith("Bearer "):
            return None

        token = auth_header[7:]  # Remove "Bearer " prefix

        # Verify the token
        is_valid, claims, error = verify_clerk_token(token)

        if not is_valid:
            logger.warning(f"Clerk token verification failed: {error}")
            return None  # Let other auth methods handle it

        # Get user from claims
        clerk_user_id = claims.get("sub")
        if not clerk_user_id:
            logger.warning("Clerk token missing subject claim")
            return None

        try:
            # Try to find user by clerk_user_id
            user = User.objects.filter(clerk_user_id=clerk_user_id).first()

            if user:
                request.user = user
                request.clerk_claims = claims
                logger.debug(f"Authenticated user {user.id} via Clerk token")
            else:
                # User not found - they need to sync first
                logger.info(f"User with clerk_user_id {clerk_user_id} not found")

        except Exception as e:
            logger.exception(f"Error looking up user from Clerk token: {e}")

        return None


class ClerkTokenAuthenticationBackend:
    """
    Django authentication backend for Clerk tokens.

    This can be used with Django's authentication system to authenticate
    users based on Clerk JWT tokens.
    """

    def authenticate(self, request, token=None):
        """Authenticate a user based on a Clerk JWT token."""
        if not token:
            return None

        if not getattr(settings, "ENABLE_CLERK_AUTH", False):
            return None

        is_valid, claims, error = verify_clerk_token(token)

        if not is_valid:
            return None

        clerk_user_id = claims.get("sub")
        if not clerk_user_id:
            return None

        try:
            user = User.objects.filter(clerk_user_id=clerk_user_id).first()
            return user
        except Exception:
            return None

    def get_user(self, user_id):
        """Get a user by ID."""
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
