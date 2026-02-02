/**
 * Copyright (c) 2023-present Plane Software, Inc. and contributors
 * SPDX-License-Identifier: AGPL-3.0-only
 * See the LICENSE file for details.
 */

import { API_ENDPOINT } from "@plane/constants";
import axios from "axios";
import type { ESubscriptionPlan, EBillingInterval } from "@plane/constants";

// Types for subscription data
export interface ISubscriptionDetails {
  id: string;
  plan: ESubscriptionPlan;
  status: string;
  billing_interval: EBillingInterval | null;
  is_active: boolean;
  is_on_trial: boolean;
  is_cancelled: boolean;
  is_free_plan: boolean;
  trial_ends_at: string | null;
  renews_at: string | null;
  ends_at: string | null;
  days_until_renewal: number | null;
  card_brand: string | null;
  card_last_four: string | null;
  customer_portal_url: string | null;
  update_payment_method_url: string | null;
}

export interface IUsageInfo {
  plan: ESubscriptionPlan;
  usage: Record<
    string,
    {
      current: number;
      limit: number | null;
      remaining: number | null;
      percentage: number;
      is_at_limit: boolean;
    }
  >;
}

export interface IPlanInfo {
  key: ESubscriptionPlan;
  name: string;
  limits: Record<string, number | null>;
  pricing: {
    monthly: number;
    yearly: number;
    yearly_savings: number;
  };
}

export interface ICheckoutResponse {
  checkout_url: string;
  checkout_id: string;
}

// Billing Service
class BillingService {
  private baseUrl: string;

  constructor() {
    this.baseUrl = API_ENDPOINT;
  }

  private get endpoint(): string {
    return `${this.baseUrl}/api/v1`;
  }

  /**
   * Get subscription details for a workspace
   */
  async getSubscription(workspaceSlug: string): Promise<ISubscriptionDetails> {
    const response = await axios.get(`${this.endpoint}/workspaces/${workspaceSlug}/billing/subscription/`);
    return response.data;
  }

  /**
   * Create a checkout session for upgrading a subscription
   */
  async createCheckout(
    workspaceSlug: string,
    plan: ESubscriptionPlan,
    billingInterval: EBillingInterval = EBillingInterval.MONTHLY,
    successUrl?: string,
    cancelUrl?: string
  ): Promise<ICheckoutResponse> {
    const response = await axios.post(`${this.endpoint}/workspaces/${workspaceSlug}/billing/checkout/`, {
      plan,
      billing_interval: billingInterval,
      success_url: successUrl,
      cancel_url: cancelUrl,
    });
    return response.data;
  }

  /**
   * Get the customer portal URL for managing subscription
   */
  async getCustomerPortalUrl(workspaceSlug: string): Promise<string | null> {
    const response = await axios.post(`${this.endpoint}/workspaces/${workspaceSlug}/billing/portal/`);
    return response.data.portal_url;
  }

  /**
   * Cancel a subscription
   */
  async cancelSubscription(
    workspaceSlug: string,
    atPeriodEnd: boolean = true
  ): Promise<{ message: string; subscription: ISubscriptionDetails }> {
    const response = await axios.delete(`${this.endpoint}/workspaces/${workspaceSlug}/billing/subscription/`, {
      data: { at_period_end: atPeriodEnd },
    });
    return response.data;
  }

  /**
   * Get usage information for a workspace
   */
  async getUsage(workspaceSlug: string): Promise<IUsageInfo> {
    const response = await axios.get(`${this.endpoint}/workspaces/${workspaceSlug}/billing/usage/`);
    return response.data;
  }

  /**
   * Get available plans
   */
  async getPlans(): Promise<{ plans: IPlanInfo[] }> {
    const response = await axios.get(`${this.endpoint}/billing/plans/`);
    return response.data;
  }

  /**
   * Redirect to checkout URL
   */
  redirectToCheckout(checkoutUrl: string): void {
    window.location.href = checkoutUrl;
  }

  /**
   * Redirect to customer portal
   */
  redirectToCustomerPortal(portalUrl: string): void {
    window.location.href = portalUrl;
  }
}

export const billingService = new BillingService();
