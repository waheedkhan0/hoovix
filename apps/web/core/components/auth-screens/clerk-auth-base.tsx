/**
 * Copyright (c) 2023-present Plane Software, Inc. and contributors
 * SPDX-License-Identifier: AGPL-3.0-only
 * See the LICENSE file for details.
 */

import { SignIn, SignUp } from "@clerk/clerk-react";
import { useTheme } from "next-themes";
import { dark } from "@clerk/themes";
import type { EAuthModes } from "@/helpers/authentication.helper";
import { EAuthModes as AuthModes } from "@/helpers/authentication.helper";
import { AuthFooter } from "./footer";
import { AuthHeader } from "./header";

type ClerkAuthBaseProps = {
  authType: EAuthModes;
};

/**
 * ClerkAuthBase component renders Clerk's SignIn or SignUp components
 * based on the authType prop. This is used when Clerk authentication is enabled.
 */
export function ClerkAuthBase({ authType }: ClerkAuthBaseProps) {
  const { resolvedTheme } = useTheme();
  const isDarkMode = resolvedTheme === "dark" || resolvedTheme === "dark-contrast";

  const clerkAppearance = {
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
      rootBox: "w-full max-w-md mx-auto",
      card: "shadow-lg border border-custom-border-200 bg-custom-background-100",
      headerTitle: "text-xl font-semibold text-custom-text-100",
      headerSubtitle: "text-custom-text-200",
      socialButtonsBlockButton: "border border-custom-border-200 hover:bg-custom-background-80 text-custom-text-100",
      socialButtonsBlockButtonText: "text-custom-text-100",
      formButtonPrimary: "bg-primary-100 hover:bg-primary-200 text-white font-medium",
      formFieldInput:
        "border border-custom-border-200 focus:border-primary-100 bg-custom-background-100 text-custom-text-100",
      formFieldLabel: "text-custom-text-200",
      footerActionLink: "text-primary-100 hover:text-primary-200",
      identityPreviewText: "text-custom-text-100",
      identityPreviewEditButton: "text-primary-100 hover:text-primary-200",
      formFieldInputShowPasswordButton: "text-custom-text-300",
      dividerLine: "bg-custom-border-200",
      dividerText: "text-custom-text-300",
      formFieldSuccessText: "text-green-500",
      formFieldErrorText: "text-red-500",
      alertText: "text-custom-text-100",
      footer: "hidden", // Hide Clerk's default footer
    },
  };

  return (
    <div className="relative z-10 flex flex-col items-center w-screen h-screen overflow-hidden overflow-y-auto pt-6 pb-10 px-8">
      <AuthHeader type={authType} />
      <div className="flex-grow flex items-center justify-center w-full">
        {authType === AuthModes.SIGN_IN ? (
          <SignIn appearance={clerkAppearance} routing="path" path="/sign-in" signUpUrl="/sign-up" afterSignInUrl="/" />
        ) : (
          <SignUp
            appearance={clerkAppearance}
            routing="path"
            path="/sign-up"
            signInUrl="/"
            afterSignUpUrl="/onboarding"
          />
        )}
      </div>
      <AuthFooter />
    </div>
  );
}
