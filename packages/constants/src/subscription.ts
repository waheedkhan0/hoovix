/**
 * Copyright (c) 2023-present Plane Software, Inc. and contributors
 * SPDX-License-Identifier: AGPL-3.0-only
 * See the LICENSE file for details.
 */

// ============================================================================
// SaaS Subscription Plans
// ============================================================================

export enum ESubscriptionPlan {
  FREE = "free",
  STARTER = "starter",
  PRO = "pro",
  ENTERPRISE = "enterprise",
}

export enum EBillingInterval {
  MONTHLY = "month",
  YEARLY = "year",
}

// Plan limits for feature gating
export const PLAN_LIMITS: Record<ESubscriptionPlan, Record<string, number | null>> = {
  [ESubscriptionPlan.FREE]: {
    projects: 3,
    members: 5,
    storage_mb: 100,
    api_calls_per_month: 1000,
    file_uploads_per_month: 50,
    integrations: 1,
    custom_fields: 0,
    automations: 0,
    ai_features: 0,
  },
  [ESubscriptionPlan.STARTER]: {
    projects: 10,
    members: 20,
    storage_mb: 1000,
    api_calls_per_month: 10000,
    file_uploads_per_month: 500,
    integrations: 5,
    custom_fields: 10,
    automations: 5,
    ai_features: 100,
  },
  [ESubscriptionPlan.PRO]: {
    projects: null, // unlimited
    members: null,
    storage_mb: 10000,
    api_calls_per_month: 100000,
    file_uploads_per_month: null,
    integrations: null,
    custom_fields: null,
    automations: null,
    ai_features: 1000,
  },
  [ESubscriptionPlan.ENTERPRISE]: {
    projects: null,
    members: null,
    storage_mb: null,
    api_calls_per_month: null,
    file_uploads_per_month: null,
    integrations: null,
    custom_fields: null,
    automations: null,
    ai_features: null,
  },
};

// Plan pricing (in USD)
export const PLAN_PRICING: Record<ESubscriptionPlan, { monthly: number; yearly: number }> = {
  [ESubscriptionPlan.FREE]: {
    monthly: 0,
    yearly: 0,
  },
  [ESubscriptionPlan.STARTER]: {
    monthly: 10,
    yearly: 100,
  },
  [ESubscriptionPlan.PRO]: {
    monthly: 25,
    yearly: 250,
  },
  [ESubscriptionPlan.ENTERPRISE]: {
    monthly: 100,
    yearly: 1000,
  },
};

// Plan feature descriptions
export const PLAN_FEATURES: Record<ESubscriptionPlan, string[]> = {
  [ESubscriptionPlan.FREE]: [
    "Up to 3 projects",
    "Up to 5 team members",
    "100MB storage",
    "1,000 API calls/month",
    "Basic integrations",
    "Community support",
  ],
  [ESubscriptionPlan.STARTER]: [
    "Up to 10 projects",
    "Up to 20 team members",
    "1GB storage",
    "10,000 API calls/month",
    "5 integrations",
    "10 custom fields",
    "5 automations",
    "100 AI features/month",
    "Email support",
  ],
  [ESubscriptionPlan.PRO]: [
    "Unlimited projects",
    "Unlimited team members",
    "10GB storage",
    "100,000 API calls/month",
    "All integrations",
    "Unlimited custom fields",
    "Unlimited automations",
    "1,000 AI features/month",
    "Priority support",
  ],
  [ESubscriptionPlan.ENTERPRISE]: [
    "Everything in Pro",
    "Unlimited storage",
    "Unlimited API calls",
    "SSO (SAML, OIDC)",
    "Advanced security",
    "Dedicated support",
    "Custom SLA",
    "Unlimited AI features",
  ],
};

// ============================================================================
// Legacy Plans (for backwards compatibility)
// ============================================================================

export const ENTERPRISE_PLAN_FEATURES = [
  "Private + managed deployments",
  "GAC",
  "LDAP support",
  "Databases + Formulas",
  "Unlimited and full Automation Flows",
  "Full-suite professional services",
];

export const BUSINESS_PLAN_FEATURES = [
  "Project Templates",
  "Workflows + Approvals",
  "Decision + Loops Automation",
  "Custom Reports",
  "Nested Pages",
  "Intake Forms",
];

export const PRO_PLAN_FEATURES = [
  "Dashboards + Reports",
  "Full Time Tracking + Bulk Ops",
  "Teamspaces",
  "Trigger And Action",
  "Wikis",
  "Popular integrations",
];

export const ONE_PLAN_FEATURES = [
  "OIDC + SAML for SSO",
  "Active Cycles",
  "Real-time collab + public views and page",
  "Link pages in issues and vice-versa",
  "Time-tracking + limited bulk ops",
  "Docker, Kubernetes and more",
];

export const FREE_PLAN_UPGRADE_FEATURES = [
  "OIDC + SAML for SSO",
  "Time Tracking and Bulk Ops",
  "Integrations",
  "Public Views and Pages",
];
