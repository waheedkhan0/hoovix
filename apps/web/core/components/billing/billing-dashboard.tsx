/**
 * Copyright (c) 2023-present Plane Software, Inc. and contributors
 * SPDX-License-Identifier: AGPL-3.0-only
 * See the LICENSE file for details.
 */

import { observer } from "mobx-react";
import { useRouter } from "next/navigation";
// plane imports
import { useTranslation } from "@plane/i18n";
import { Button, ProgressBar } from "@plane/ui";
// hooks
import { useBilling, useWorkspace } from "@/hooks/store";
// local imports
import { SubscriptionPlan } from "../../../../../../packages/constants/src/subscription";

export const BillingDashboard = observer(function BillingDashboard() {
  const router = useRouter();
  const { t } = useTranslation();
  const { currentWorkspace } = useWorkspace();
  const { subscription, usage, isLoading, cancelSubscription, createLemonSqueezyCustomerPortal } = useBilling();

  const handleManageSubscription = async () => {
    try {
      const portalUrl = await createLemonSqueezyCustomerPortal();
      if (portalUrl) {
        window.location.href = portalUrl;
      }
    } catch (error) {
      console.error("Failed to create customer portal:", error);
    }
  };

  const handleUpgrade = () => {
    router.push(`/${currentWorkspace?.slug}/settings/billing`);
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-custom-primary" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Current Plan Card */}
      <div className="bg-custom-background rounded-xl border border-custom-border-200 p-6">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <div>
            <h3 className="text-lg font-semibold text-custom-text-primary">{t("billing.currentPlan")}</h3>
            <p className="text-sm text-custom-text-secondary mt-1">
              {subscription
                ? t("billing.planRenewal", {
                    date: new Date(subscription.current_period_end * 1000).toLocaleDateString(),
                  })
                : t("billing.freePlan")}
            </p>
          </div>
          <div className="flex items-center gap-3">
            <span
              className={`px-3 py-1 rounded-full text-sm font-medium ${
                subscription?.status === "active" ? "bg-green-100 text-green-700" : "bg-yellow-100 text-yellow-700"
              }`}
            >
              {subscription?.status === "active" ? t("billing.active") : subscription?.status || t("billing.inactive")}
            </span>
            {subscription ? (
              <Button variant="outline" onClick={handleManageSubscription}>
                {t("billing.manageSubscription")}
              </Button>
            ) : (
              <Button variant="primary" onClick={handleUpgrade}>
                {t("billing.upgrade")}
              </Button>
            )}
          </div>
        </div>
      </div>

      {/* Usage Overview */}
      {usage && (
        <div className="bg-custom-background rounded-xl border border-custom-border-200 p-6">
          <h3 className="text-lg font-semibold text-custom-text-primary mb-4">{t("billing.usageOverview")}</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <UsageCard label={t("billing.projects")} used={usage.projects} limit={usage.projects_limit} />
            <UsageCard label={t("billing.issues")} used={usage.issues} limit={usage.issues_limit} />
            <UsageCard label={t("billing.storage")} used={usage.storage} limit={usage.storage_limit} unit="GB" />
            <UsageCard label={t("billing.teamMembers")} used={usage.team_members} limit={usage.team_members_limit} />
            <UsageCard label={t("billing.cycles")} used={usage.cycles} limit={usage.cycles_limit} />
            <UsageCard label={t("billing.modules")} used={usage.modules} limit={usage.modules_limit} />
          </div>
        </div>
      )}

      {/* Upgrade Callout */}
      {!subscription && (
        <div className="bg-custom-primary/5 rounded-xl border border-custom-primary/20 p-6">
          <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
            <div>
              <h3 className="text-lg font-semibold text-custom-text-primary">{t("billing.unlockAllFeatures")}</h3>
              <p className="text-sm text-custom-text-secondary mt-1">{t("billing.upgradeDescription")}</p>
            </div>
            <Button variant="primary" onClick={handleUpgrade}>
              {t("billing.upgradeNow")}
            </Button>
          </div>
        </div>
      )}

      {/* Plan Comparison */}
      {subscription && subscription.plan !== SubscriptionPlan.ENTERPRISE && (
        <div className="bg-custom-background rounded-xl border border-custom-border-200 p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-custom-text-primary">{t("billing.lookingForMore")}</h3>
          </div>
          <p className="text-sm text-custom-text-secondary mb-4">{t("billing.upgradeDescription")}</p>
          <Button variant="outline" onClick={handleUpgrade}>
            {t("billing.viewPlans")}
          </Button>
        </div>
      )}
    </div>
  );
});

interface UsageCardProps {
  label: string;
  used: number;
  limit: number;
  unit?: string;
}

const UsageCard = observer(function UsageCard({ label, used, limit, unit }: UsageCardProps) {
  const percentage = limit > 0 ? Math.min((used / limit) * 100, 100) : 0;
  const isNearLimit = percentage >= 80;

  return (
    <div className="p-4 bg-custom-background-80 rounded-lg">
      <div className="flex items-center justify-between mb-2">
        <span className="text-sm font-medium text-custom-text-secondary">{label}</span>
        <span className={`text-xs font-medium ${isNearLimit ? "text-yellow-500" : "text-custom-text-secondary"}`}>
          {used} / {limit === -1 ? "∞" : `${limit}${unit ? ` ${unit}` : ""}`}
        </span>
      </div>
      <ProgressBar
        value={percentage}
        max={100}
        className={`h-2 ${isNearLimit ? "bg-yellow-100" : "bg-custom-background-200"}`}
        barClassName={isNearLimit ? "bg-yellow-500" : "bg-custom-primary"}
      />
      {isNearLimit && limit !== -1 && <p className="text-xs text-yellow-500 mt-1">{"billing.nearLimit"}</p>}
    </div>
  );
});
