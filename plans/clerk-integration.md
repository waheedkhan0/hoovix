# Clerk Authentication Integration Architecture

## Overview

This document provides a comprehensive guide for integrating Clerk authentication into the Hoovix project management platform. Clerk will replace the existing custom authentication system (email/password, magic codes, OAuth) with a modern, secure, and feature-rich authentication solution.

## Current Authentication Architecture

### Existing Auth Flow
```
┌─────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   Client    │────▶│  Django Session  │────▶│  User Record    │
│  (React)    │     │  Auth Middleware │     │  (PostgreSQL)   │
└─────────────┘     └──────────────────┘     └─────────────────┘
```

### Current Auth Components

**Frontend (`apps/web`):**
- [`AuthBase`](apps/web/core/components/auth-screens/auth-base.tsx:1) - Main auth screen wrapper
- [`AuthenticationWrapper`](apps/web/core/lib/wrappers/authentication-wrapper.tsx:32) - Route protection wrapper
- [`AuthService`](apps/web/core/services/auth.service.ts:1) - Auth API service
- [`EAuthModes`](apps/web/helpers/authentication.helper.tsx:20) - Auth mode enums
- [`EPageTypes`](apps/web/helpers/authentication.helper.tsx:13) - Page type enums for auth state

**Backend (`apps/api`):**
- [`EmailProvider`](apps/api/plane/authentication/provider/credentials/email.py:1) - Email/password auth
- [`MagicCodeProvider`](apps/api/plane/authentication/provider/credentials/magic_code.py:1) - Magic link auth
- [`SessionMiddleware`](apps/api/plane/authentication/middleware/session.py:16) - Session management
- [`User`](apps/api/plane/db/models/user.py:56) - User model

## Proposed Clerk Integration Architecture

### High-Level Flow
```
┌─────────────┐     ┌──────────────┐     ┌──────────────────┐
│   Client    │────▶│    Clerk     │────▶│   Clerk Cloud    │
│  (React)    │     │   Provider   │     │   (Auth Service) │
└─────────────┘     └──────────────┘     └──────────────────┘
                              │                    │
                              ▼                    ▼
                       ┌──────────────┐     ┌──────────────────┐
                       │  JWT Token   │────▶│   Hoovix API     │
                       └──────────────┘     │  (Validate JWT)  │
                                            └──────────────────┘
```

## Implementation Plan

### Phase 1: Frontend Integration

#### 1.1 Install Dependencies

```bash
# In apps/web
pnpm add @clerk/clerk-react @clerk/themes

# For backend (Python)
pip install clerk-backend-api
```

#### 1.2 Create Clerk Provider Wrapper

Create [`apps/web/app/providers/clerk-provider.tsx`](apps/web/app/providers/clerk-provider.tsx:1):

```typescript
import { ClerkProvider } from "@clerk/clerk-react";
import { dark } from "@clerk/themes";
import { useTheme } from "next-themes";

const CLERK_PUBLISHABLE_KEY = process.env.VITE_CLERK_PUBLISHABLE_KEY;

interface ClerkAuthProviderProps {
  children: React.ReactNode;
}

export function ClerkAuthProvider({ children }: ClerkAuthProviderProps) {
  const { resolvedTheme } = useTheme();
  
  return (
    <ClerkProvider
      publishableKey={CLERK_PUBLISHABLE_KEY}
      appearance={{
        baseTheme: resolvedTheme === "dark" ? dark : undefined,
        variables: {
          colorPrimary: "#3F76FF",
          colorBackground: resolvedTheme === "dark" ? "#0F0F0F" : "#FFFFFF",
          colorText: resolvedTheme === "dark" ? "#FFFFFF" : "#1F1F1F",
        },
      }}
      signInUrl="/sign-in"
      signUpUrl="/sign-up"
      afterSignInUrl="/"
      afterSignUpUrl="/onboarding"
    >
      {children}
    </ClerkProvider>
  );
}
```

#### 1.3 Update Root Provider

Modify [`apps/web/app/provider.tsx`](apps/web/app/provider.tsx:42):

```typescript
import { ClerkAuthProvider } from "./providers/clerk-provider";

export function AppProvider(props: IAppProvider) {
  const { children } = props;
  const { resolvedTheme } = useTheme();

  return (
    <ClerkAuthProvider>
      <StoreProvider>
        <>
          <AppProgressBar />
          <TranslationProvider>
            <Toast theme={resolveGeneralTheme(resolvedTheme)} />
            <StoreWrapper>
              <InstanceWrapper>
                <Suspense>
                  <ChatSupportModal />
                  <SWRConfig value={WEB_SWR_CONFIG}>{children}</SWRConfig>
                </Suspense>
              </InstanceWrapper>
            </StoreWrapper>
          </TranslationProvider>
        </>
      </StoreProvider>
    </ClerkAuthProvider>
  );
}
```

#### 1.4 Create Sign-In Page

Create [`apps/web/app/(home)/sign-in/page.tsx`](apps/web/app/(home)/sign-in/page.tsx:1):

```typescript
import { SignIn } from "@clerk/clerk-react";
import { AuthenticationWrapper } from "@/lib/wrappers/authentication-wrapper";
import { EPageTypes } from "@/helpers/authentication.helper";
import DefaultLayout from "@/layouts/default-layout";

export default function SignInPage() {
  return (
    <DefaultLayout>
      <AuthenticationWrapper pageType={EPageTypes.NON_AUTHENTICATED}>
        <div className="flex min-h-screen items-center justify-center">
          <SignIn 
            routing="path"
            path="/sign-in"
            appearance={{
              elements: {
                formButtonPrimary: "bg-blue-500 hover:bg-blue-600",
                footerActionLink: "text-blue-500 hover:text-blue-600",
              }
            }}
          />
        </div>
      </AuthenticationWrapper>
    </DefaultLayout>
  );
}
```

#### 1.5 Create Sign-Up Page

Create [`apps/web/app/(all)/sign-up/page.tsx`](apps/web/app/(all)/sign-up/page.tsx:1):

```typescript
import { SignUp } from "@clerk/clerk-react";
import { AuthenticationWrapper } from "@/lib/wrappers/authentication-wrapper";
import { EPageTypes } from "@/helpers/authentication.helper";
import DefaultLayout from "@/layouts/default-layout";

export default function SignUpPage() {
  return (
    <DefaultLayout>
      <AuthenticationWrapper pageType={EPageTypes.NON_AUTHENTICATED}>
        <div className="flex min-h-screen items-center justify-center">
          <SignUp 
            routing="path"
            path="/sign-up"
            afterSignUpUrl="/onboarding"
          />
        </div>
      </AuthenticationWrapper>
    </DefaultLayout>
  );
}
```

#### 1.6 Update Authentication Wrapper

Modify [`apps/web/core/lib/wrappers/authentication-wrapper.tsx`](apps/web/core/lib/wrappers/authentication-wrapper.tsx:32):

```typescript
import { useAuth, useUser, useSession } from "@clerk/clerk-react";
import { useEffect } from "react";

export const AuthenticationWrapper = observer(function AuthenticationWrapper(
  props: TAuthenticationWrapper
) {
  const { children, pageType = EPageTypes.AUTHENTICATED } = props;
  
  // Clerk hooks
  const { isLoaded, isSignedIn } = useAuth();
  const { user: clerkUser } = useUser();
  const { session } = useSession();
  
  // Existing Hoovix hooks
  const { isLoading: isUserLoading, data: currentUser, fetchCurrentUser } = useUser();
  const { data: currentUserProfile } = useUserProfile();
  
  // Sync Clerk user with Hoovix backend
  useEffect(() => {
    if (isLoaded && isSignedIn && clerkUser && !currentUser?.id) {
      // Sync user with Hoovix backend
      syncClerkUserWithHoovix(clerkUser, session);
    }
  }, [isLoaded, isSignedIn, clerkUser, currentUser?.id, session]);

  // Handle loading state
  if (!isLoaded || isUserLoading) {
    return (
      <div className="relative flex h-screen w-full items-center justify-center">
        <LogoSpinner />
      </div>
    );
  }

  // Route protection logic
  if (pageType === EPageTypes.NON_AUTHENTICATED) {
    if (!isSignedIn) return <>{children}</>;
    // Redirect authenticated users
    return <Navigate to={getWorkspaceRedirectionUrl()} />;
  }

  if (pageType === EPageTypes.AUTHENTICATED) {
    if (isSignedIn) {
      if (currentUserProfile?.id && isUserOnboard) {
        return <>{children}</>;
      }
      return <Navigate to="/onboarding" />;
    }
    return <Navigate to="/sign-in" />;
  }

  return <>{children}</>;
});

// Helper function to sync Clerk user with Hoovix
async function syncClerkUserWithHoovix(clerkUser: UserResource, session: SessionResource | null) {
  if (!session) return;
  
  const token = await session.getToken();
  
  await fetch(`${API_BASE_URL}/api/auth/clerk/sync`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${token}`,
    },
    body: JSON.stringify({
      clerkUserId: clerkUser.id,
      email: clerkUser.primaryEmailAddress?.emailAddress,
      firstName: clerkUser.firstName,
      lastName: clerkUser.lastName,
      avatarUrl: clerkUser.imageUrl,
    }),
  });
}
```

### Phase 2: Backend Integration

#### 2.1 Install Clerk Python SDK

Add to [`apps/api/requirements.txt`](apps/api/requirements.txt:1):

```
clerk-backend-api>=1.0.0
PyJWT>=2.8.0
cryptography>=41.0.0
```

#### 2.2 Create Clerk JWT Middleware

Create [`apps/api/plane/authentication/middleware/clerk_jwt.py`](apps/api/plane/authentication/middleware/clerk_jwt.py:1):

```python
# Copyright (c) 2023-present Plane Software, Inc. and contributors
# SPDX-License-Identifier: AGPL-3.0-only

import jwt
import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin

User = get_user_model()

CLERK_JWT_ISSUER = f"https://{settings.CLERK_DOMAIN}"
CLERK_JWT_AUDIENCE = settings.CLERK_AUDIENCE


class ClerkJWTAuthenticationMiddleware(MiddlewareMixin):
    """
    Middleware to validate Clerk JWT tokens and authenticate users.
    """
    
    def __init__(self, get_response):
        super().__init__(get_response)
        self.jwks_client = None
        self._load_jwks()
    
    def _load_jwks(self):
        """Load Clerk JWKS for token verification."""
        try:
            jwks_url = f"{CLERK_JWT_ISSUER}/.well-known/jwks.json"
            response = requests.get(jwks_url, timeout=10)
            response.raise_for_status()
            self.jwks_client = response.json()
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to load Clerk JWKS: {e}")
    
    def process_request(self, request):
        # Skip authentication for exempt paths
        exempt_paths = [
            "/api/auth/clerk/",
            "/api/auth/sign-in/",
            "/api/auth/sign-up/",
            "/api/auth/magic-sign-in/",
            "/api/auth/magic-sign-up/",
            "/api/instances/",
            "/health/",
        ]
        
        if any(request.path.startswith(path) for path in exempt_paths):
            return None
        
        # Check for Authorization header
        auth_header = request.META.get("HTTP_AUTHORIZATION", "")
        if not auth_header.startswith("Bearer "):
            request.user = AnonymousUser()
            return None
        
        token = auth_header.split(" ")[1]
        
        try:
            # Decode and verify JWT
            payload = self._verify_token(token)
            
            # Get or create user
            clerk_user_id = payload.get("sub")
            user = self._get_or_create_user(clerk_user_id, payload)
            request.user = user
            request.clerk_user_id = clerk_user_id
            
        except jwt.ExpiredSignatureError:
            return JsonResponse(
                {"error": "Token expired"},
                status=401
            )
        except jwt.InvalidTokenError as e:
            return JsonResponse(
                {"error": f"Invalid token: {str(e)}"},
                status=401
            )
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Authentication error: {e}")
            request.user = AnonymousUser()
        
        return None
    
    def _verify_token(self, token: str) -> dict:
        """Verify Clerk JWT token."""
        # Get the signing key from JWKS
        unverified_header = jwt.get_unverified_header(token)
        kid = unverified_header.get("kid")
        
        if not self.jwks_client:
            raise jwt.InvalidTokenError("JWKS not loaded")
        
        signing_key = None
        for key in self.jwks_client.get("keys", []):
            if key.get("kid") == kid:
                signing_key = key
                break
        
        if not signing_key:
            raise jwt.InvalidTokenError("Signing key not found")
        
        # Construct RSA public key
        from jwt.algorithms import RSAAlgorithm
        public_key = RSAAlgorithm.from_jwk(signing_key)
        
        # Verify token
        payload = jwt.decode(
            token,
            public_key,
            algorithms=["RS256"],
            issuer=CLERK_JWT_ISSUER,
            audience=CLERK_JWT_AUDIENCE,
        )
        
        return payload
    
    def _get_or_create_user(self, clerk_user_id: str, payload: dict) -> User:
        """Get or create Hoovix user from Clerk data."""
        try:
            user = User.objects.get(clerk_user_id=clerk_user_id)
            return user
        except User.DoesNotExist:
            # Create new user
            email = payload.get("email")
            username = email.split("@")[0] if email else clerk_user_id[:20]
            
            # Ensure unique username
            base_username = username
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{base_username}{counter}"
                counter += 1
            
            user = User.objects.create(
                clerk_user_id=clerk_user_id,
                email=email,
                username=username,
                first_name=payload.get("first_name", ""),
                last_name=payload.get("last_name", ""),
                is_email_verified=payload.get("email_verified", False),
                auth_provider="clerk",
            )
            return user
```

#### 2.3 Update User Model

Add fields to [`apps/api/plane/db/models/user.py`](apps/api/plane/db/models/user.py:56):

```python
class User(AbstractBaseUser, PermissionsMixin):
    # ... existing fields ...
    
    # Clerk integration fields
    clerk_user_id = models.CharField(
        max_length=255,
        unique=True,
        null=True,
        blank=True,
        db_index=True,
        help_text="Clerk user ID for authentication"
    )
    auth_provider = models.CharField(
        max_length=50,
        default="email",
        choices=[
            ("email", "Email/Password"),
            ("clerk", "Clerk"),
            ("google", "Google OAuth"),
            ("github", "GitHub OAuth"),
            ("gitlab", "GitLab OAuth"),
        ],
        help_text="Authentication provider"
    )
    
    # ... rest of the model ...
```

#### 2.4 Create Clerk Sync Endpoint

Create [`apps/api/plane/authentication/views/app/clerk.py`](apps/api/plane/authentication/views/app/clerk.py:1):

```python
# Copyright (c) 2023-present Plane Software, Inc. and contributors
# SPDX-License-Identifier: AGPL-3.0-only

import json
from django.http import JsonResponse
from django.views import View
from django.contrib.auth import get_user_model
from django.db import transaction

from plane.authentication.middleware.clerk_jwt import ClerkJWTAuthenticationMiddleware

User = get_user_model()


class ClerkUserSyncView(View):
    """
    Sync Clerk user data with Hoovix database.
    Called by frontend after Clerk authentication.
    """
    
    def post(self, request):
        # Verify the request has valid Clerk token
        middleware = ClerkJWTAuthenticationMiddleware(None)
        result = middleware.process_request(request)
        
        if result:
            return result
        
        if not request.user or not request.user.is_authenticated:
            return JsonResponse(
                {"error": "Authentication required"},
                status=401
            )
        
        try:
            body = json.loads(request.body)
            
            # Update user information from Clerk
            user = request.user
            
            # Update email if changed
            email = body.get("email")
            if email and email != user.email:
                # Check for email conflicts
                if User.objects.filter(email=email).exclude(id=user.id).exists():
                    return JsonResponse(
                        {"error": "Email already in use"},
                        status=409
                    )
                user.email = email
            
            # Update profile information
            first_name = body.get("firstName")
            if first_name:
                user.first_name = first_name
            
            last_name = body.get("lastName")
            if last_name:
                user.last_name = last_name
            
            # Update avatar URL
            avatar_url = body.get("avatarUrl")
            if avatar_url:
                user.avatar = avatar_url
            
            user.save()
            
            # Return user data
            return JsonResponse({
                "id": str(user.id),
                "email": user.email,
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "avatar": user.avatar,
                "is_onboarded": user.profile.is_onboarded if hasattr(user, 'profile') else False,
            })
            
        except json.JSONDecodeError:
            return JsonResponse(
                {"error": "Invalid JSON"},
                status=400
            )
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error syncing Clerk user: {e}")
            return JsonResponse(
                {"error": "Internal server error"},
                status=500
            )


class ClerkWebhookView(View):
    """
    Handle Clerk webhooks for user lifecycle events.
    """
    
    def post(self, request):
        # Verify webhook signature
        signature = request.META.get("HTTP_CLERK_SIGNATURE", "")
        if not self._verify_webhook_signature(request.body, signature):
            return JsonResponse(
                {"error": "Invalid signature"},
                status=401
            )
        
        try:
            payload = json.loads(request.body)
            event_type = payload.get("type")
            data = payload.get("data", {})
            
            if event_type == "user.created":
                self._handle_user_created(data)
            elif event_type == "user.updated":
                self._handle_user_updated(data)
            elif event_type == "user.deleted":
                self._handle_user_deleted(data)
            elif event_type == "session.created":
                self._handle_session_created(data)
            elif event_type == "session.ended":
                self._handle_session_ended(data)
            
            return JsonResponse({"status": "ok"})
            
        except json.JSONDecodeError:
            return JsonResponse(
                {"error": "Invalid JSON"},
                status=400
            )
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error processing Clerk webhook: {e}")
            return JsonResponse(
                {"error": "Internal server error"},
                status=500
            )
    
    def _verify_webhook_signature(self, body: bytes, signature: str) -> bool:
        """Verify Clerk webhook signature."""
        import hmac
        import hashlib
        
        webhook_secret = settings.CLERK_WEBHOOK_SECRET
        if not webhook_secret:
            return False
        
        expected_signature = hmac.new(
            webhook_secret.encode(),
            body,
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(signature, expected_signature)
    
    def _handle_user_created(self, data: dict):
        """Handle user.created webhook."""
        clerk_user_id = data.get("id")
        email = data.get("email_addresses", [{}])[0].get("email_address")
        
        # User will be created on first sync
        logger = logging.getLogger(__name__)
        logger.info(f"Clerk user created: {clerk_user_id}")
    
    def _handle_user_updated(self, data: dict):
        """Handle user.updated webhook."""
        clerk_user_id = data.get("id")
        
        try:
            user = User.objects.get(clerk_user_id=clerk_user_id)
            
            # Update email if changed
            email = data.get("email_addresses", [{}])[0].get("email_address")
            if email and email != user.email:
                user.email = email
            
            # Update profile
            user.first_name = data.get("first_name", user.first_name)
            user.last_name = data.get("last_name", user.last_name)
            
            user.save()
            
        except User.DoesNotExist:
            pass
    
    def _handle_user_deleted(self, data: dict):
        """Handle user.deleted webhook."""
        clerk_user_id = data.get("id")
        
        try:
            user = User.objects.get(clerk_user_id=clerk_user_id)
            # Soft delete or deactivate user
            user.is_active = False
            user.save()
        except User.DoesNotExist:
            pass
    
    def _handle_session_created(self, data: dict):
        """Handle session.created webhook."""
        # Log session creation for analytics
        pass
    
    def _handle_session_ended(self, data: dict):
        """Handle session.ended webhook."""
        # Log session end for analytics
        pass
```

#### 2.5 Update URL Configuration

Add to [`apps/api/plane/authentication/urls.py`](apps/api/plane/authentication/urls.py:1):

```python
from django.urls import path
from plane.authentication.views.app.clerk import ClerkUserSyncView, ClerkWebhookView

urlpatterns = [
    # ... existing URLs ...
    
    # Clerk integration
    path("auth/clerk/sync/", ClerkUserSyncView.as_view(), name="clerk-sync"),
    path("auth/clerk/webhook/", ClerkWebhookView.as_view(), name="clerk-webhook"),
]
```

#### 2.6 Update Settings

Add to [`apps/api/plane/settings/common.py`](apps/api/plane/settings/common.py:1):

```python
# Clerk Configuration
CLERK_PUBLISHABLE_KEY = os.environ.get("CLERK_PUBLISHABLE_KEY", "")
CLERK_SECRET_KEY = os.environ.get("CLERK_SECRET_KEY", "")
CLERK_DOMAIN = os.environ.get("CLERK_DOMAIN", "")
CLERK_AUDIENCE = os.environ.get("CLERK_AUDIENCE", "")
CLERK_WEBHOOK_SECRET = os.environ.get("CLERK_WEBHOOK_SECRET", "")

# Add Clerk middleware
MIDDLEWARE = [
    # ... existing middleware ...
    "plane.authentication.middleware.clerk_jwt.ClerkJWTAuthenticationMiddleware",
]
```

### Phase 3: Migration Strategy

#### 3.1 Database Migration

Create migration for new fields:

```python
# Generated migration
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("db", "0118_workspaceuserproperties_navigation_control_preference_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="clerk_user_id",
            field=models.CharField(
                max_length=255,
                unique=True,
                null=True,
                blank=True,
                db_index=True,
            ),
        ),
        migrations.AddField(
            model_name="user",
            name="auth_provider",
            field=models.CharField(
                max_length=50,
                default="email",
                choices=[
                    ("email", "Email/Password"),
                    ("clerk", "Clerk"),
                    ("google", "Google OAuth"),
                    ("github", "GitHub OAuth"),
                    ("gitlab", "GitLab OAuth"),
                ],
            ),
        ),
        migrations.RunSQL(
            """
            CREATE INDEX CONCURRENTLY IF NOT EXISTS users_clerk_user_id_idx 
            ON users(clerk_user_id) WHERE clerk_user_id IS NOT NULL;
            """,
            reverse_sql="DROP INDEX IF EXISTS users_clerk_user_id_idx;",
        ),
    ]
```

#### 3.2 User Migration Script

Create [`apps/api/plane/db/management/commands/migrate_to_clerk.py`](apps/api/plane/db/management/commands/migrate_to_clerk.py:1):

```python
# Copyright (c) 2023-present Plane Software, Inc. and contributors
# SPDX-License-Identifier: AGPL-3.0-only

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction

User = get_user_model()


class Command(BaseCommand):
    help = "Migrate existing users to Clerk"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be done without making changes",
        )
        parser.add_argument(
            "--batch-size",
            type=int,
            default=100,
            help="Number of users to process per batch",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        batch_size = options["batch_size"]
        
        # Get users that need migration
        users_to_migrate = User.objects.filter(
            clerk_user_id__isnull=True,
            is_active=True,
        )
        
        total_users = users_to_migrate.count()
        self.stdout.write(f"Found {total_users} users to migrate")
        
        if dry_run:
            self.stdout.write(self.style.WARNING("DRY RUN - No changes will be made"))
            for user in users_to_migrate[:10]:
                self.stdout.write(f"Would migrate: {user.email} ({user.username})")
            return
        
        # Process in batches
        migrated = 0
        failed = 0
        
        for i in range(0, total_users, batch_size):
            batch = users_to_migrate[i:i + batch_size]
            
            for user in batch:
                try:
                    with transaction.atomic():
                        # Mark user for Clerk migration
                        # Actual migration happens when user logs in via Clerk
                        user.auth_provider = "email"  # Keep existing provider
                        user.save(update_fields=["auth_provider"])
                        migrated += 1
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f"Failed to migrate {user.email}: {e}")
                    )
                    failed += 1
            
            self.stdout.write(f"Processed {min(i + batch_size, total_users)}/{total_users}")
        
        self.stdout.write(
            self.style.SUCCESS(f"Migration complete: {migrated} migrated, {failed} failed")
        )
```

### Phase 4: Environment Configuration

#### 4.1 Environment Variables

Add to `.env.example`:

```bash
# Clerk Configuration
VITE_CLERK_PUBLISHABLE_KEY=pk_test_...
CLERK_SECRET_KEY=sk_test_...
CLERK_DOMAIN=https://clerk.your-domain.com
CLERK_AUDIENCE=your-audience
CLERK_WEBHOOK_SECRET=whsec_...

# Feature Flags
ENABLE_CLERK_AUTH=false
ENABLE_LEGACY_AUTH=true
```

#### 4.2 Frontend Environment Types

Update [`apps/web/app/env.d.ts`](apps/web/app/env.d.ts:1):

```typescript
/// <reference types="@react-router/dev" />
/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_CLERK_PUBLISHABLE_KEY: string;
  readonly VITE_ENABLE_CLERK_AUTH: string;
  readonly VITE_API_BASE_URL: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
```

## Testing Strategy

### Unit Tests

Create [`apps/web/core/lib/wrappers/__tests__/authentication-wrapper.test.tsx`](apps/web/core/lib/wrappers/__tests__/authentication-wrapper.test.tsx:1):

```typescript
import { render, screen } from "@testing-library/react";
import { ClerkAuthProvider } from "@/app/providers/clerk-provider";
import { AuthenticationWrapper } from "../authentication-wrapper";
import { EPageTypes } from "@/helpers/authentication.helper";

describe("AuthenticationWrapper", () => {
  it("should show loading spinner when Clerk is not loaded", () => {
    render(
      <ClerkAuthProvider>
        <AuthenticationWrapper pageType={EPageTypes.AUTHENTICATED}>
          <div>Protected Content</div>
        </AuthenticationWrapper>
      </ClerkAuthProvider>
    );
    
    expect(screen.getByTestId("logo-spinner")).toBeInTheDocument();
  });
  
  it("should redirect unauthenticated users to sign-in", () => {
    // Mock useAuth to return unauthenticated state
    jest.mock("@clerk/clerk-react", () => ({
      useAuth: () => ({ isLoaded: true, isSignedIn: false }),
      useUser: () => ({ user: null }),
    }));
    
    const { container } = render(
      <AuthenticationWrapper pageType={EPageTypes.AUTHENTICATED}>
        <div>Protected Content</div>
      </AuthenticationWrapper>
    );
    
    expect(container).toBeEmptyDOMElement();
  });
});
```

### Integration Tests

Create [`apps/api/plane/tests/authentication/test_clerk_integration.py`](apps/api/plane/tests/authentication/test_clerk_integration.py:1):

```python
import pytest
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from unittest.mock import patch, MagicMock

User = get_user_model()


class ClerkIntegrationTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.clerk_user_id = "user_123"
        
    @patch("plane.authentication.middleware.clerk_jwt.jwt.decode")
    def test_valid_clerk_token_authenticates_user(self, mock_decode):
        # Arrange
        mock_decode.return_value = {
            "sub": self.clerk_user_id,
            "email": "test@example.com",
            "first_name": "Test",
            "last_name": "User",
        }
        
        # Act
        response = self.client.post(
            "/api/auth/clerk/sync/",
            HTTP_AUTHORIZATION="Bearer valid_token",
            content_type="application/json",
        )
        
        # Assert
        self.assertEqual(response.status_code, 200)
        
    def test_invalid_clerk_token_returns_401(self):
        response = self.client.post(
            "/api/auth/clerk/sync/",
            HTTP_AUTHORIZATION="Bearer invalid_token",
            content_type="application/json",
        )
        
        self.assertEqual(response.status_code, 401)
```

## Rollback Plan

In case of issues, the following rollback steps should be taken:

1. **Revert Environment Variables**: Set `ENABLE_CLERK_AUTH=false` and `ENABLE_LEGACY_AUTH=true`
2. **Revert Frontend**: Remove Clerk provider wrapper from [`app/provider.tsx`](apps/web/app/provider.tsx:42)
3. **Revert Backend**: Remove Clerk middleware from settings
4. **Database**: The `clerk_user_id` and `auth_provider` fields can remain; they won't affect legacy auth

## Security Considerations

1. **JWT Validation**: Always verify Clerk JWT tokens using JWKS
2. **Webhook Security**: Verify Clerk webhook signatures using the webhook secret
3. **Token Expiration**: Handle token expiration gracefully with refresh logic
4. **User Data**: Only sync necessary user data from Clerk
5. **Session Management**: Maintain session state securely

## Performance Considerations

1. **JWKS Caching**: Cache Clerk JWKS to avoid repeated requests
2. **Token Caching**: Cache validated tokens for short periods
3. **Lazy Loading**: Load Clerk components lazily to reduce initial bundle size
4. **Database Indexes**: Ensure `clerk_user_id` is indexed for fast lookups

## Monitoring and Analytics

1. **Auth Events**: Track sign-in, sign-up, and sign-out events
2. **Error Tracking**: Monitor Clerk authentication failures
3. **Performance**: Track token validation latency
4. **User Migration**: Monitor migration progress and success rates
