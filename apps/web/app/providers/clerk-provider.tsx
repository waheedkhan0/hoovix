/**
 * Copyright (c) 2023-present Plane Software, Inc. and contributors
 * SPDX-License-Identifier: AGPL-3.0-only
 * See the LICENSE file for details.
 */

import { ClerkProvider, useAuth, useUser } from "@clerk/clerk-react";
import { dark } from "@clerk/themes";
import { useTheme } from "next-themes";
import { useCallback, useEffect, type ReactNode } from "react";
// plane imports
import { API_BASE_URL } from "@plane/constants";

const CLERK_PUBLISHABLE_KEY = import.meta.env.VITE_CLERK_PUBLISHABLE_KEY;
const ENABLE_CLERK_AUTH = import.meta.env.VITE_ENABLE_CLERK_AUTH === "true";

interface ClerkAuthProviderProps {
  children: ReactNode;
}

/**
 * Syncs Clerk user data with the backend
 */
function ClerkUserSync({ children }: { children: ReactNode }) {
  const { isSignedIn, getToken } = useAuth();
  const { user, isLoaded: isUserLoaded } = useUser();

  const syncUser = useCallback(async () => {
    if (!isSignedIn || !isUserLoaded || !user) return;

    try {
      const token = await getToken();
      if (!token) return;

      // Sync user with backend
      const response = await fetch(`${API_BASE_URL}/api/auth/clerk/sync/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          clerk_user_id: user.id,
          email: user.primaryEmailAddress?.emailAddress,
          first_name: user.firstName,
          last_name: user.lastName,
          avatar_url: user.imageUrl,
        }),
      });

      if (!response.ok) {
        console.error("Failed to sync user with backend:", response.statusText);
      }
    } catch (error) {
      console.error("Error syncing user:", error);
    }
  }, [isSignedIn, isUserLoaded, user, getToken]);

  useEffect(() => {
    syncUser();
  }, [syncUser]);

  return <>{children}</>;
}

/**
 * ClerkAuthProvider wraps the application with Clerk authentication
 * Only active when VITE_ENABLE_CLERK_AUTH is set to "true"
 */
export function ClerkAuthProvider({ children }: ClerkAuthProviderProps) {
  const { resolvedTheme } = useTheme();

  // If Clerk auth is not enabled, just render children
  if (!ENABLE_CLERK_AUTH || !CLERK_PUBLISHABLE_KEY) {
    return <>{children}</>;
  }

  const isDarkMode = resolvedTheme === "dark" || resolvedTheme === "dark-contrast";

  return (
    <ClerkProvider
      publishableKey={CLERK_PUBLISHABLE_KEY}
      appearance={{
        baseTheme: isDarkMode ? dark : undefined,
        variables: {
          colorPrimary: "#3f76ff",
          colorBackground: isDarkMode ? "#1f2937" : "#ffffff",
          colorText: isDarkMode ? "#f9fafb" : "#111827",
          colorInputBackground: isDarkMode ? "#374151" : "#f9fafb",
          colorInputText: isDarkMode ? "#f9fafb" : "#111827",
          borderRadius: "0.5rem",
        },
        elements: {
          formButtonPrimary: "bg-primary-100 hover:bg-primary-200 text-white",
          card: "shadow-lg",
          headerTitle: "text-xl font-semibold",
          headerSubtitle: "text-custom-text-200",
          socialButtonsBlockButton: "border border-custom-border-200 hover:bg-custom-background-80",
          formFieldInput: "border border-custom-border-200 focus:border-primary-100",
          footerActionLink: "text-primary-100 hover:text-primary-200",
        },
      }}
      signInUrl="/sign-in"
      signUpUrl="/sign-up"
      afterSignInUrl="/"
      afterSignUpUrl="/onboarding"
    >
      <ClerkUserSync>{children}</ClerkUserSync>
    </ClerkProvider>
  );
}

/**
 * Hook to check if Clerk authentication is enabled
 */
export function useClerkEnabled(): boolean {
  return ENABLE_CLERK_AUTH && !!CLERK_PUBLISHABLE_KEY;
}

/**
 * Re-export Clerk hooks for convenience
 */
export { useAuth, useUser, useClerk, useSignIn, useSignUp } from "@clerk/clerk-react";
