/**
 * Copyright (c) 2023-present Plane Software, Inc. and contributors
 * SPDX-License-Identifier: AGPL-3.0-only
 * See the LICENSE file for details.
 */

import React from "react";
import { AuthRoot } from "@/components/account/auth-forms/auth-root";
import type { EAuthModes } from "@/helpers/authentication.helper";
import { useClerkEnabled } from "@/app/providers/clerk-provider";
import { AuthFooter } from "./footer";
import { AuthHeader } from "./header";
import { ClerkAuthBase } from "./clerk-auth-base";

type AuthBaseProps = {
  authType: EAuthModes;
};

export function AuthBase({ authType }: AuthBaseProps) {
  const isClerkEnabled = useClerkEnabled();

  // If Clerk is enabled, use Clerk's authentication UI
  if (isClerkEnabled) {
    return <ClerkAuthBase authType={authType} />;
  }

  // Otherwise, use the existing authentication UI
  return (
    <div className="relative z-10 flex flex-col items-center w-screen h-screen overflow-hidden overflow-y-auto pt-6 pb-10 px-8">
      <AuthHeader type={authType} />
      <AuthRoot authMode={authType} />
      <AuthFooter />
    </div>
  );
}
