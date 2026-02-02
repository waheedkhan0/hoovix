/**
 * Copyright (c) 2023-present Plane Software, Inc. and contributors
 * SPDX-License-Identifier: AGPL-3.0-only
 * See the LICENSE file for details.
 */

import useSWR from "swr";
import { billingService } from "@plane/services";
import type { ISubscriptionDetails, IUsageInfo } from "@plane/services";

const SUBSCRIPTION_KEY = (workspaceSlug: string) => ["subscription", workspaceSlug];
const USAGE_KEY = (workspaceSlug: string) => ["usage", workspaceSlug];

export interface UseSubscriptionProps {
  workspaceSlug: string;
}

export const useSubscription = ({ workspaceSlug }: UseSubscriptionProps) => {
  const {
    data: subscription,
    error: subscriptionError,
    isLoading: isSubscriptionLoading,
    mutate: mutateSubscription,
  } = useSWR<ISubscriptionDetails, Error>(
    SUBSCRIPTION_KEY(workspaceSlug),
    () => billingService.getSubscription(workspaceSlug),
    {
      revalidateOnFocus: false,
      dedupingInterval: 30000,
    }
  );

  const cancelSubscription = async (atPeriodEnd: boolean = true) => {
    try {
      const result = await billingService.cancelSubscription(workspaceSlug, atPeriodEnd);
      mutateSubscription(result.subscription, false);
      return result;
    } catch (error) {
      console.error("Error cancelling subscription:", error);
      throw error;
    }
  };

  return {
    subscription,
    isLoading: isSubscriptionLoading,
    error: subscriptionError,
    cancelSubscription,
    mutateSubscription,
  };
};

export const useUsage = ({ workspaceSlug }: UseSubscriptionProps) => {
  const {
    data: usage,
    error: usageError,
    isLoading: isUsageLoading,
    mutate: mutateUsage,
  } = useSWR<IUsageInfo, Error>(
    USAGE_KEY(workspaceSlug),
    () => billingService.getUsage(workspaceSlug),
    {
      revalidateOnFocus: false,
      dedupingInterval: 30000,
    }
  );

  return {
    usage,
    isLoading: isUsageLoading,
    error: usageError,
    mutateUsage,
  };
};

export const useBilling = ({ workspaceSlug }: UseSubscriptionProps) => {
  const { subscription, isLoading: subLoading, error: subError, cancelSubscription } = useSubscription({ workspaceSlug });
  const { usage, isLoading: usageLoading, error: usageError } = useUsage({ workspaceSlug });

  const getPlans = async () => {
    try {
      const result = await billingService.getPlans();
      return result.plans;
    } catch (error) {
      console.error("Error fetching plans:", error);
      throw error;
    }
  };

  const getCustomerPortalUrl = async (): Promise<string | null> => {
    try {
      const url = await billingService.getCustomerPortalUrl(workspaceSlug);
      if (url) {
        billingService.redirectToCustomerPortal(url);
      }
      return url;
    } catch (error) {
      console.error("Error getting customer portal URL:", error);
      throw error;
    }
  };

  const createLemonSqueezyCheckout = async ({
    productId,
    billingFrequency,
  }: {
    productId: string;
    billingFrequency: string;
  }): Promise<string | null> => {
    try {
      const result = await billingService.createCheckout(workspaceSlug, productId as any, billingFrequency as any);
      if (result.checkout_url) {
        billingService.redirectToCheckout(result.checkout_url);
      }
      return result.checkout_url;
    } catch (error) {
      console.error("Error creating checkout:", error);
      throw error;
    }
  };

  return {
    subscription,
    usage,
    isLoading: subLoading || usageLoading,
    error: subError || usageError,
    cancelSubscription,
    getPlans,
    getCustomerPortalUrl,
    createLemonSqueezyCheckout,
    // Helper methods for feature gate checks
    isFreePlan: subscription?.is_free_plan ?? true,
    isActive: subscription?.is_active ?? false,
    plan: subscription?.plan ?? null,
  };
};
