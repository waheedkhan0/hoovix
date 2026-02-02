/**
 * Copyright (c) 2023-present Plane Software, Inc. and contributors
 * SPDX-License-Identifier: AGPL-3.0-only
 * See the LICENSE file for details.
 */

import { type ReactNode } from "react";
import { useBilling } from "@plane/hooks";
import { UpgradePrompt } from "./upgrade-prompt";

interface FeatureGateProps {
  children: ReactNode;
  fallback?: ReactNode;
  workspaceSlug: string;
  feature: string;
  amount?: number;
  message?: string;
  showPrompt?: boolean;
}

/**
 * FeatureGate component that conditionally renders content based on feature limits.
 *
 * Usage:
 * ```tsx
 * <FeatureGate workspaceSlug="my-workspace" feature="projects">
 *   <CreateProjectButton />
 * </FeatureGate>
 * ```
 */
export function FeatureGate({
  children,
  fallback = null,
  workspaceSlug,
  feature,
  amount = 1,
  message,
  showPrompt = true,
}: FeatureGateProps) {
  const { canUseFeature, isLoading } = useBilling({ workspaceSlug });

  if (isLoading) {
    return null;
  }

  const canUse = canUseFeature(feature, amount);

  if (canUse) {
    return <>{children}</>;
  }

  if (showPrompt) {
    return <UpgradePrompt feature={feature} message={message} />;
  }

  return <>{fallback}</>;
}

interface PlanGateProps {
  children: ReactNode;
  workspaceSlug: string;
  plans: ("free" | "starter" | "pro" | "enterprise")[];
  fallback?: ReactNode;
  showPrompt?: boolean;
}

/**
 * PlanGate component that conditionally renders content based on subscription plan.
 *
 * Usage:
 * ```tsx
 * <PlanGate workspaceSlug="my-workspace" plans={["pro", "enterprise"]}>
 *   <AIFeatures />
 * </PlanGate>
 * ```
 */
export function PlanGate({ children, workspaceSlug, plans, fallback = null, showPrompt = true }: PlanGateProps) {
  const { subscription, isLoading } = useBilling({ workspaceSlug });

  if (isLoading || !subscription) {
    return null;
  }

  const hasAccess = plans.includes(subscription.plan as (typeof plans)[number]);

  if (hasAccess) {
    return <>{children}</>;
  }

  if (showPrompt) {
    const lowestPlan = plans[0];
    const featureMessages: Record<string, string> = {
      free: "This feature is available on all paid plans.",
      starter: "Upgrade to Starter to access this feature.",
      pro: "Upgrade to Pro to access this feature.",
      enterprise: "Upgrade to Enterprise to access this feature.",
    };

    return <UpgradePrompt feature={lowestPlan} message={featureMessages[lowestPlan]} />;
  }

  return <>{fallback}</>;
}

interface UsageGateProps {
  children: ReactNode;
  workspaceSlug: string;
  feature: string;
  percentage?: number;
  fallback?: ReactNode;
}

/**
 * UsageGate component that shows a warning when usage approaches the limit.
 *
 * Usage:
 * ```tsx
 * <UsageGate workspaceSlug="my-workspace" feature="api_calls_per_month" percentage={80}>
 *   <APIUsageWarning />
 * </UsageGate>
 * ```
 */
export function UsageGate({ children, workspaceSlug, feature, percentage = 80, fallback }: UsageGateProps) {
  const { usage, isLoading } = useBilling({ workspaceSlug });

  if (isLoading || !usage) {
    return null;
  }

  const featureUsage = usage.usage[feature];

  if (!featureUsage) {
    return <>{children}</>;
  }

  const isNearLimit = featureUsage.percentage >= percentage;
  const isAtLimit = featureUsage.is_at_limit;

  // If at limit, show fallback
  if (isAtLimit) {
    return <>{fallback}</>;
  }

  // If near limit, pass a prop to show warning
  // The children should handle the warning display
  return (
    <>{typeof children === "function" ? children({ isNearLimit, percentage: featureUsage.percentage }) : children}</>
  );
}

// Type for UsageGate children callback
export type UsageGateChildrenProps = {
  isNearLimit: boolean;
  percentage: number;
};

export type { FeatureGateProps, PlanGateProps, UsageGateProps };
