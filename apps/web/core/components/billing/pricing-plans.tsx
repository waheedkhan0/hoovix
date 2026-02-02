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
import { EProductSubscriptionEnum } from "@plane/types";
import { Button } from "@plane/ui";
// hooks
import { useBilling } from "@/hooks/store";
// local imports
import { FeatureGate } from "../billing/feature-gate";

export type TBillingFrequency = "month" | "year";

interface PricingPlan {
  id: string;
  name: string;
  description: string;
  price: number;
  billingFrequency: TBillingFrequency;
  productId: string;
  features: string[];
  highlighted?: boolean;
}

export const PricingPlans = observer(function PricingPlans() {
  const router = useRouter();
  const { t } = useTranslation();
  const { createLemonSqueezyCheckout, isLoading } = useBilling();
  const [billingFrequency, setBillingFrequency] = useState<TBillingFrequency>("month");

  const plans: PricingPlan[] = [
    {
      id: "free",
      name: t("pricing.free.name"),
      description: t("pricing.free.description"),
      price: 0,
      billingFrequency: "month",
      productId: "",
      features: [
        t("pricing.features.unlimitedProjects"),
        t("pricing.features.unlimitedMembers"),
        t("pricing.features.issueTracking"),
        t("pricing.features.basicSupport"),
      ],
    },
    {
      id: "starter",
      name: t("pricing.starter.name"),
      description: t("pricing.starter.description"),
      price: billingFrequency === "month" ? 5 : 50,
      billingFrequency,
      productId: process.env.NEXT_PUBLIC_LEMON_SQUEEZY_STARTER_PRICE_ID || "",
      features: [
        t("pricing.features.everythingInFree"),
        t("pricing.features.automation"),
        t("pricing.features.analytics"),
        t("pricing.features.customViews"),
        t("pricing.features.prioritizedSupport"),
      ],
    },
    {
      id: "pro",
      name: t("pricing.pro.name"),
      description: t("pricing.pro.description"),
      price: billingFrequency === "month" ? 10 : 100,
      billingFrequency,
      productId: process.env.NEXT_PUBLIC_LEMON_SQUEEZY_PRO_PRICE_ID || "",
      highlighted: true,
      features: [
        t("pricing.features.everythingInStarter"),
        t("pricing.features.aiFeatures"),
        t("pricing.features.advancedSecurity"),
        t("pricing.features.dedicatedSupport"),
        t("pricing.features.customBranding"),
      ],
    },
    {
      id: "enterprise",
      name: t("pricing.enterprise.name"),
      description: t("pricing.enterprise.description"),
      price: 0,
      billingFrequency: "month",
      productId: "",
      features: [
        t("pricing.features.everythingInPro"),
        t("pricing.features.ssoSaml"),
        t("pricing.features.auditLogs"),
        t("pricing.features.dedicatedSuccessManager"),
        t("pricing.features.customContract"),
      ],
    },
  ];

  const handleSubscribe = async (plan: PricingPlan) => {
    if (plan.id === "free" || plan.id === "enterprise") {
      // For free plan, redirect to workspace
      // For enterprise, show contact sales modal
      return;
    }

    try {
      const checkoutUrl = await createLemonSqueezyCheckout({
        productId: plan.productId,
        billingFrequency: plan.billingFrequency,
      });

      if (checkoutUrl) {
        window.location.href = checkoutUrl;
      }
    } catch (error) {
      console.error("Failed to create checkout:", error);
    }
  };

  return (
    <section className="py-12">
      {/* Billing Frequency Toggle */}
      <div className="flex justify-center mb-12">
        <div className="inline-flex items-center p-1 bg-custom-background-80 rounded-lg">
          <button
            onClick={() => setBillingFrequency("month")}
            className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              billingFrequency === "month"
                ? "bg-custom-primary text-white"
                : "text-custom-text-secondary hover:text-custom-text-primary"
            }`}
          >
            {t("pricing.monthly")}
          </button>
          <button
            onClick={() => setBillingFrequency("year")}
            className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              billingFrequency === "year"
                ? "bg-custom-primary text-white"
                : "text-custom-text-secondary hover:text-custom-text-primary"
            }`}
          >
            {t("pricing.yearly")}{" "}
            <span className="text-xs text-green-500 ml-1">{t("pricing.savePercent", { percent: 17 })}</span>
          </button>
        </div>
      </div>

      {/* Plans Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 max-w-7xl mx-auto px-4">
        {plans.map((plan) => (
          <div
            key={plan.id}
            className={`relative flex flex-col p-6 rounded-xl border ${
              plan.highlighted
                ? "border-custom-primary bg-custom-primary/5 shadow-lg shadow-custom-primary/10"
                : "border-custom-border-200 bg-custom-background"
            }`}
          >
            {plan.highlighted && (
              <div className="absolute -top-3 left-1/2 -translate-x-1/2 px-3 py-1 bg-custom-primary text-white text-xs font-medium rounded-full">
                {t("pricing.mostPopular")}
              </div>
            )}

            <div className="mb-4">
              <h3 className="text-lg font-semibold text-custom-text-primary">{plan.name}</h3>
              <p className="text-sm text-custom-text-secondary mt-1">{plan.description}</p>
            </div>

            <div className="mb-6">
              {plan.price === 0 ? (
                <div className="text-3xl font-bold text-custom-text-primary">
                  {plan.id === "enterprise" ? t("pricing.contactSales") : t("pricing.free")}
                </div>
              ) : (
                <div className="flex items-baseline">
                  <span className="text-4xl font-bold text-custom-text-primary">${plan.price}</span>
                  <span className="text-custom-text-secondary ml-1">
                    /{plan.billingFrequency === "month" ? t("pricing.month") : t("pricing.year")}
                  </span>
                </div>
              )}
            </div>

            <ul className="flex-1 space-y-3 mb-6">
              {plan.features.map((feature, index) => (
                <li key={index} className="flex items-start gap-2">
                  <svg
                    className="w-5 h-5 text-green-500 flex-shrink-0 mt-0.5"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  <span className="text-sm text-custom-text-secondary">{feature}</span>
                </li>
              ))}
            </ul>

            <Button
              variant={plan.highlighted ? "primary" : "outline"}
              size="lg"
              className="w-full"
              onClick={() => handleSubscribe(plan)}
              disabled={isLoading || plan.price === 0}
              loading={isLoading}
            >
              {plan.id === "free"
                ? t("pricing.getStarted")
                : plan.id === "enterprise"
                  ? t("pricing.contactSales")
                  : t("pricing.subscribe")}
            </Button>
          </div>
        ))}
      </div>

      {/* FAQ Section */}
      <div className="mt-16 max-w-3xl mx-auto px-4">
        <h2 className="text-2xl font-bold text-center text-custom-text-primary mb-8">{t("pricing.faq.title")}</h2>
        <div className="space-y-4">
          <FaqItem question={t("pricing.faq.cancelQuestion")} answer={t("pricing.faq.cancelAnswer")} />
          <FaqItem question={t("pricing.faq.trialQuestion")} answer={t("pricing.faq.trialAnswer")} />
          <FaqItem question={t("pricing.faq.paymentQuestion")} answer={t("pricing.faq.paymentAnswer")} />
        </div>
      </div>
    </section>
  );
});

interface FaqItemProps {
  question: string;
  answer: string;
}

const FaqItem = observer(function FaqItem({ question, answer }: FaqItemProps) {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div className="border border-custom-border-200 rounded-lg overflow-hidden">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full flex items-center justify-between p-4 bg-custom-background hover:bg-custom-background-80 transition-colors"
      >
        <span className="font-medium text-custom-text-primary">{question}</span>
        <svg
          className={`w-5 h-5 text-custom-text-secondary transition-transform ${isOpen ? "rotate-180" : ""}`}
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>
      {isOpen && (
        <div className="p-4 bg-custom-background border-t border-custom-border-200">
          <p className="text-sm text-custom-text-secondary">{answer}</p>
        </div>
      )}
    </div>
  );
});
