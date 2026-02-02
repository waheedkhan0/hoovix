/**
 * Copyright (c) 2023-present Plane Software, Inc. and contributors
 * SPDX-License-Identifier: AGPL-3.0-only
 * See the LICENSE file for details.
 */

import { useState } from "react";
import { observer } from "mobx-react";
import { useRouter } from "next/navigation";
// plane imports
import { useTranslation } from "@plane/i18n";
import { Popover2 } from "@plane/ui";
// hooks
import { useBilling, useWorkspace } from "@/hooks/store";
// local imports
import { BillingDashboard } from "./billing-dashboard";

export const UsageIndicator = observer(function UsageIndicator() {
  const router = useRouter();
  const { t } = useTranslation();
  const { currentWorkspace } = useWorkspace();
  const { usage, isLoading } = useBilling();

  const [isOpen, setIsOpen] = useState(false);

  if (isLoading || !usage) {
    return null;
  }

  // Calculate overall usage percentage
  const usageItems = [
    { key: "projects", label: t("billing.projects"), used: usage.projects, limit: usage.projects_limit },
    { key: "issues", label: t("billing.issues"), used: usage.issues, limit: usage.issues_limit },
    { key: "storage", label: t("billing.storage"), used: usage.storage, limit: usage.storage_limit, unit: "GB" },
    { key: "members", label: t("billing.teamMembers"), used: usage.team_members, limit: usage.team_members_limit },
  ];

  // Find the item closest to its limit
  const closestToLimit = usageItems.reduce(
    (closest, item) => {
      if (item.limit === -1 || item.limit === 0) return closest;
      const percentage = (item.used / item.limit) * 100;
      const closestPercentage = (closest.used / closest.limit) * 100;
      return percentage > closestPercentage ? item : closest;
    },
    { ...usageItems[0], used: 0, limit: 1 } // Initialize with a safe default
  );

  const percentage = closestToLimit.limit > 0 ? Math.min((closestToLimit.used / closestToLimit.limit) * 100, 100) : 0;

  const isNearLimit = percentage >= 80;

  const handleViewBilling = () => {
    setIsOpen(false);
    router.push(`/${currentWorkspace?.slug}/settings/billing`);
  };

  return (
    <Popover2
      isOpen={isOpen}
      onChange={setIsOpen}
      content={
        <div className="w-80 p-4">
          <div className="flex items-center justify-between mb-3">
            <h3 className="font-semibold text-custom-text-primary">{t("billing.usage")}</h3>
            <button onClick={handleViewBilling} className="text-sm text-custom-primary hover:underline">
              {t("billing.viewDetails")}
            </button>
          </div>
          <BillingDashboard />
        </div>
      }
      placement="bottom-end"
      overlayClassName="z-50"
    >
      <button
        onClick={() => setIsOpen(!isOpen)}
        className={`flex items-center gap-2 px-3 py-2 rounded-lg transition-colors ${
          isNearLimit
            ? "bg-yellow-50 text-yellow-700 hover:bg-yellow-100"
            : "bg-custom-background-80 text-custom-text-secondary hover:bg-custom-background"
        }`}
      >
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 2a2 012-2h2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
          />
        </svg>
        <span className="text-sm font-medium">{Math.round(percentage)}%</span>
        {isNearLimit && (
          <svg className="w-4 h-4 text-yellow-500" fill="currentColor" viewBox="0 0 20 20">
            <path
              fillRule="evenodd"
              d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z"
              clipRule="evenodd"
            />
          </svg>
        )}
      </button>
    </Popover2>
  );
});
