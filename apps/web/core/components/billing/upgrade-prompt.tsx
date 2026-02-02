/**
 * Copyright (c) 2023-present Plane Software, Inc. and contributors
 * SPDX-License-Identifier: AGPL-3.0-only
 * See the LICENSE file for details.
 */

import { useState } from "react";
import { useBilling } from "@plane/hooks";
import { Modal } from "@plane/ui";
import { useRouter } from "react-router";
import { CircleAlert } from "lucide-react";

interface UpgradePromptProps {
  feature?: string;
  message?: string;
  plan?: "starter" | "pro" | "enterprise";
  buttonText?: string;
  onClose?: () => void;
}

export function UpgradePrompt({
  feature,
  message,
  plan = "pro",
  buttonText = "Upgrade now",
  onClose,
}: UpgradePromptProps) {
  const [showModal, setShowModal] = useState(true);
  const router = useRouter();
  const { startCheckout } = useBilling({
    workspaceSlug: "", // Will be set by the component
  });

  const handleUpgrade = async () => {
    // The workspaceSlug should be obtained from context
    // For now, we'll redirect to the billing page
    router.push("/settings/billing");
  };

  const featureMessages: Record<string, string> = {
    projects: "You've reached the maximum number of projects for your plan.",
    members: "You've reached the maximum number of team members for your plan.",
    storage: "You've reached the storage limit for your plan.",
    automations: "You've reached the maximum number of automations for your plan.",
    ai_features: "You've reached your AI features limit for this month.",
    integrations: "You've reached the maximum number of integrations for your plan.",
    custom_fields: "You've reached the maximum number of custom fields for your plan.",
  };

  const defaultMessage = feature
    ? featureMessages[feature] || `This feature requires a ${plan} plan or higher.`
    : "Upgrade your plan to access this feature.";

  return (
    <>
      <div className="flex flex-col items-center justify-center p-6 text-center">
        <div className="flex items-center justify-center w-12 h-12 rounded-full bg-primary-100/10 mb-4">
          <CircleAlert className="w-6 h-6 text-primary-100" />
        </div>

        <h3 className="text-lg font-semibold text-custom-text-100 mb-2">
          {feature ? `Unlock ${feature}` : "Upgrade to unlock"}
        </h3>

        <p className="text-sm text-custom-text-200 mb-4 max-w-md">{message || defaultMessage}</p>

        <button
          onClick={handleUpgrade}
          className="px-4 py-2 bg-primary-100 text-white rounded-lg font-medium hover:bg-primary-200 transition-colors"
        >
          {buttonText}
        </button>
      </div>
    </>
  );
}

interface PlanLimitWarningProps {
  workspaceSlug: string;
  feature: string;
  current: number;
  limit: number;
  percentage?: number;
}

export function PlanLimitWarning({ workspaceSlug, feature, current, limit, percentage = 80 }: PlanLimitWarningProps) {
  const usagePercentage = Math.round((current / limit) * 100);
  const isNearLimit = usagePercentage >= percentage;

  if (!isNearLimit) return null;

  return (
    <div className="flex items-center gap-2 p-3 bg-amber-50 border border-amber-200 rounded-lg">
      <CircleAlert className="w-5 h-5 text-amber-500 flex-shrink-0" />
      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium text-amber-800">You're running low on {feature}</p>
        <p className="text-xs text-amber-600">
          {current} of {limit} used ({usagePercentage}%)
        </p>
      </div>
      <button
        onClick={() => {
          window.location.href = `/${workspaceSlug}/settings/billing`;
        }}
        className="text-sm font-medium text-amber-700 hover:text-amber-800"
      >
        Upgrade
      </button>
    </div>
  );
}

interface PlanBadgeProps {
  plan: "free" | "starter" | "pro" | "enterprise";
  showLabel?: boolean;
}

export function PlanBadge({ plan, showLabel = true }: PlanBadgeProps) {
  const planConfig = {
    free: {
      label: "Free",
      className: "bg-gray-100 text-gray-700",
    },
    starter: {
      label: "Starter",
      className: "bg-blue-100 text-blue-700",
    },
    pro: {
      label: "Pro",
      className: "bg-purple-100 text-purple-700",
    },
    enterprise: {
      label: "Enterprise",
      className: "bg-orange-100 text-orange-700",
    },
  };

  const config = planConfig[plan] || planConfig.free;

  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${config.className}`}>
      {showLabel && <span className="mr-1">✨</span>}
      {config.label}
    </span>
  );
}
