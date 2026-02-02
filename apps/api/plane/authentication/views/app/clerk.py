# Copyright (c) 2023-present Plane Software, Inc. and contributors
# SPDX-License-Identifier: AGPL-3.0-only
# See the LICENSE file for details.

"""
Clerk Authentication Views

This module provides endpoints for:
1. User sync - Syncing Clerk user data with the local database
2. Webhooks - Handling Clerk webhook events (user.created, user.updated, user.deleted)
"""

import hashlib
import hmac
import json
import logging
from datetime import datetime

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import transaction
from django.http import JsonResponse
from django.utils import timezone
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from plane.authentication.middleware.clerk_jwt import verify_clerk_token

logger = logging.getLogger(__name__)

User = get_user_model()


@method_decorator(csrf_exempt, name="dispatch")
class ClerkUserSyncEndpoint(View):
    """
    Endpoint to sync Clerk user data with the local database.

    This endpoint is called by the frontend after a user signs in with Clerk.
    It creates or updates the local user record with data from Clerk.

    POST /api/auth/clerk/sync/
    Headers:
        Authorization: Bearer <clerk_jwt_token>
    Body:
        {
            "clerk_user_id": "user_xxx",
            "email": "user@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "avatar_url": "https://..."
        }
    """

    def post(self, request):
        # Check if Clerk auth is enabled
        if not getattr(settings, "ENABLE_CLERK_AUTH", False):
            return JsonResponse(
                {"error": "Clerk authentication is not enabled"},
                status=400,
            )

        # Get and verify the token
        auth_header = request.META.get("HTTP_AUTHORIZATION", "")
        if not auth_header.startswith("Bearer "):
            return JsonResponse(
                {"error": "Missing or invalid authorization header"},
                status=401,
            )

        token = auth_header[7:]
        is_valid, claims, error = verify_clerk_token(token)

        if not is_valid:
            return JsonResponse(
                {"error": f"Invalid token: {error}"},
                status=401,
            )

        # Parse request body
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse(
                {"error": "Invalid JSON body"},
                status=400,
            )

        # Validate required fields
        clerk_user_id = data.get("clerk_user_id")
        email = data.get("email")

        if not clerk_user_id or not email:
            return JsonResponse(
                {"error": "clerk_user_id and email are required"},
                status=400,
            )

        # Verify the clerk_user_id matches the token
        if claims.get("sub") != clerk_user_id:
            return JsonResponse(
                {"error": "Token subject does not match clerk_user_id"},
                status=403,
            )

        try:
            with transaction.atomic():
                # Try to find existing user by clerk_user_id or email
                user = User.objects.filter(clerk_user_id=clerk_user_id).first()

                if not user:
                    # Try to find by email (for migration from existing auth)
                    user = User.objects.filter(email=email).first()

                if user:
                    # Update existing user
                    user.clerk_user_id = clerk_user_id
                    if data.get("first_name"):
                        user.first_name = data["first_name"]
                    if data.get("last_name"):
                        user.last_name = data["last_name"]
                    if data.get("avatar_url"):
                        user.avatar = data["avatar_url"]
                    user.last_login = timezone.now()
                    user.save()
                    logger.info(f"Updated user {user.id} from Clerk sync")
                else:
                    # Create new user
                    user = User.objects.create(
                        email=email,
                        clerk_user_id=clerk_user_id,
                        first_name=data.get("first_name", ""),
                        last_name=data.get("last_name", ""),
                        avatar=data.get("avatar_url", ""),
                        username=email,  # Use email as username
                        is_active=True,
                        is_email_verified=True,  # Clerk handles email verification
                        last_login=timezone.now(),
                    )
                    logger.info(f"Created new user {user.id} from Clerk sync")

                return JsonResponse(
                    {
                        "id": str(user.id),
                        "email": user.email,
                        "first_name": user.first_name,
                        "last_name": user.last_name,
                        "is_onboarded": user.is_onboarded,
                    },
                    status=200,
                )

        except Exception as e:
            logger.exception(f"Error syncing Clerk user: {e}")
            return JsonResponse(
                {"error": "Failed to sync user"},
                status=500,
            )


@method_decorator(csrf_exempt, name="dispatch")
class ClerkWebhookEndpoint(View):
    """
    Endpoint to handle Clerk webhook events.

    Clerk sends webhooks for various events like:
    - user.created: A new user signed up
    - user.updated: User profile was updated
    - user.deleted: User was deleted

    POST /api/auth/clerk/webhook/
    Headers:
        svix-id: <webhook_id>
        svix-timestamp: <timestamp>
        svix-signature: <signature>
    Body:
        {
            "type": "user.created",
            "data": { ... }
        }
    """

    def post(self, request):
        # Check if Clerk auth is enabled
        if not getattr(settings, "ENABLE_CLERK_AUTH", False):
            return JsonResponse(
                {"error": "Clerk authentication is not enabled"},
                status=400,
            )

        # Verify webhook signature
        webhook_secret = getattr(settings, "CLERK_WEBHOOK_SECRET", None)
        if not webhook_secret:
            logger.error("CLERK_WEBHOOK_SECRET not configured")
            return JsonResponse(
                {"error": "Webhook secret not configured"},
                status=500,
            )

        # Get Svix headers
        svix_id = request.META.get("HTTP_SVIX_ID")
        svix_timestamp = request.META.get("HTTP_SVIX_TIMESTAMP")
        svix_signature = request.META.get("HTTP_SVIX_SIGNATURE")

        if not all([svix_id, svix_timestamp, svix_signature]):
            return JsonResponse(
                {"error": "Missing webhook signature headers"},
                status=400,
            )

        # Verify signature
        try:
            body = request.body.decode("utf-8")
            signed_content = f"{svix_id}.{svix_timestamp}.{body}"

            # Parse the signature (format: v1,<base64_signature>)
            signatures = svix_signature.split(" ")
            expected_signatures = []

            for sig in signatures:
                parts = sig.split(",")
                if len(parts) == 2 and parts[0] == "v1":
                    expected_signatures.append(parts[1])

            if not expected_signatures:
                return JsonResponse(
                    {"error": "Invalid signature format"},
                    status=400,
                )

            # Compute expected signature
            secret_bytes = webhook_secret.encode("utf-8")
            if webhook_secret.startswith("whsec_"):
                import base64

                secret_bytes = base64.b64decode(webhook_secret[6:])

            computed_signature = hmac.new(
                secret_bytes,
                signed_content.encode("utf-8"),
                hashlib.sha256,
            ).digest()

            import base64

            computed_signature_b64 = base64.b64encode(computed_signature).decode("utf-8")

            # Check if any signature matches
            signature_valid = any(
                hmac.compare_digest(computed_signature_b64, sig)
                for sig in expected_signatures
            )

            if not signature_valid:
                logger.warning("Clerk webhook signature verification failed")
                return JsonResponse(
                    {"error": "Invalid signature"},
                    status=401,
                )

        except Exception as e:
            logger.exception(f"Error verifying webhook signature: {e}")
            return JsonResponse(
                {"error": "Signature verification failed"},
                status=400,
            )

        # Parse webhook payload
        try:
            payload = json.loads(body)
        except json.JSONDecodeError:
            return JsonResponse(
                {"error": "Invalid JSON body"},
                status=400,
            )

        event_type = payload.get("type")
        event_data = payload.get("data", {})

        logger.info(f"Received Clerk webhook: {event_type}")

        # Handle different event types
        try:
            if event_type == "user.created":
                self._handle_user_created(event_data)
            elif event_type == "user.updated":
                self._handle_user_updated(event_data)
            elif event_type == "user.deleted":
                self._handle_user_deleted(event_data)
            else:
                logger.info(f"Unhandled Clerk webhook event: {event_type}")

            return JsonResponse({"status": "ok"}, status=200)

        except Exception as e:
            logger.exception(f"Error handling Clerk webhook: {e}")
            return JsonResponse(
                {"error": "Failed to process webhook"},
                status=500,
            )

    def _handle_user_created(self, data: dict):
        """Handle user.created webhook event."""
        clerk_user_id = data.get("id")
        email_addresses = data.get("email_addresses", [])
        primary_email = next(
            (e["email_address"] for e in email_addresses if e.get("id") == data.get("primary_email_address_id")),
            email_addresses[0]["email_address"] if email_addresses else None,
        )

        if not clerk_user_id or not primary_email:
            logger.warning("user.created webhook missing required data")
            return

        # Check if user already exists
        existing_user = User.objects.filter(clerk_user_id=clerk_user_id).first()
        if existing_user:
            logger.info(f"User {clerk_user_id} already exists, skipping creation")
            return

        # Check if user exists by email (migration case)
        existing_user = User.objects.filter(email=primary_email).first()
        if existing_user:
            # Link existing user to Clerk
            existing_user.clerk_user_id = clerk_user_id
            existing_user.save()
            logger.info(f"Linked existing user {existing_user.id} to Clerk user {clerk_user_id}")
            return

        # Create new user
        user = User.objects.create(
            email=primary_email,
            clerk_user_id=clerk_user_id,
            first_name=data.get("first_name", ""),
            last_name=data.get("last_name", ""),
            avatar=data.get("image_url", ""),
            username=primary_email,
            is_active=True,
            is_email_verified=True,
        )
        logger.info(f"Created user {user.id} from Clerk webhook")

    def _handle_user_updated(self, data: dict):
        """Handle user.updated webhook event."""
        clerk_user_id = data.get("id")
        if not clerk_user_id:
            return

        user = User.objects.filter(clerk_user_id=clerk_user_id).first()
        if not user:
            logger.warning(f"User {clerk_user_id} not found for update")
            return

        # Update user fields
        email_addresses = data.get("email_addresses", [])
        primary_email = next(
            (e["email_address"] for e in email_addresses if e.get("id") == data.get("primary_email_address_id")),
            None,
        )

        if primary_email and primary_email != user.email:
            user.email = primary_email
            user.username = primary_email

        if data.get("first_name"):
            user.first_name = data["first_name"]
        if data.get("last_name"):
            user.last_name = data["last_name"]
        if data.get("image_url"):
            user.avatar = data["image_url"]

        user.save()
        logger.info(f"Updated user {user.id} from Clerk webhook")

    def _handle_user_deleted(self, data: dict):
        """Handle user.deleted webhook event."""
        clerk_user_id = data.get("id")
        if not clerk_user_id:
            return

        user = User.objects.filter(clerk_user_id=clerk_user_id).first()
        if not user:
            logger.warning(f"User {clerk_user_id} not found for deletion")
            return

        # Soft delete - deactivate the user instead of deleting
        user.is_active = False
        user.save()
        logger.info(f"Deactivated user {user.id} from Clerk webhook")
