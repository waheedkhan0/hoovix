# Copyright (c) 2023-present Plane Software, Inc. and contributors
# SPDX-License-Identifier: AGPL-3.0-only
# See the LICENSE file for details.

"""
Subscription Service.

This module provides high-level subscription management operations
that coordinate between the database and Lemon Squeezy API.
"""

import logging
from typing import Optional

from django.conf import settings
from django.db import transaction
from django.utils import timezone

from plane.billing.models.subscription import (
    Subscription,
    SubscriptionEvent,
    SubscriptionPlan,
    SubscriptionStatus,
    BillingInterval,
)
from plane.billing.services.lemon_squeezy import (
    LemonSqueezyClient,
    CheckoutOptions,
    CheckoutResponse,
    LemonSqueezyError,
)

logger = logging.getLogger(__name__)


# Plan variant mapping - maps plan names to Lemon Squeezy variant IDs
PLAN_VARIANTS = {
    SubscriptionPlan.STARTER: {
        BillingInterval.MONTHLY: getattr(settings, "LEMON_SQUEEZY_STARTER_MONTHLY_VARIANT_ID", None),
        BillingInterval.YEARLY: getattr(settings, "LEMON_SQUEEZY_STARTER_YEARLY_VARIANT_ID", None),
    },
    SubscriptionPlan.PRO: {
        BillingInterval.MONTHLY: getattr(settings, "LEMON_SQUEEZY_PRO_MONTHLY_VARIANT_ID", None),
        BillingInterval.YEARLY: getattr(settings, "LEMON_SQUEEZY_PRO_YEARLY_VARIANT_ID", None),
    },
    SubscriptionPlan.ENTERPRISE: {
        BillingInterval.MONTHLY: getattr(settings, "LEMON_SQUEEZY_ENTERPRISE_VARIANT_ID", None),
        BillingInterval.YEARLY: getattr(settings, "LEMON_SQUEEZY_ENTERPRISE_VARIANT_ID", None),
    },
}


class SubscriptionService:
    """
    Service for managing workspace subscriptions.

    This service provides methods for:
    - Creating checkout sessions
    - Managing subscription lifecycle
    - Syncing subscription data from webhooks
    """

    def __init__(self):
        self.client = LemonSqueezyClient()

    def get_or_create_subscription(self, workspace) -> Subscription:
        """
        Get or create a subscription for a workspace.

        New workspaces start on the free plan.
        """
        subscription, created = Subscription.objects.get_or_create(
            workspace=workspace,
            defaults={
                "plan": SubscriptionPlan.FREE,
                "status": SubscriptionStatus.ACTIVE,
            },
        )

        if created:
            logger.info(f"Created free subscription for workspace {workspace.id}")

        return subscription

    def create_checkout(
        self,
        workspace,
        user,
        plan: str,
        billing_interval: str,
        success_url: Optional[str] = None,
        cancel_url: Optional[str] = None,
    ) -> CheckoutResponse:
        """
        Create a checkout session for upgrading a workspace subscription.

        Args:
            workspace: The workspace to upgrade
            user: The user initiating the checkout
            plan: The plan to subscribe to (starter, pro, enterprise)
            billing_interval: Monthly or yearly billing
            success_url: URL to redirect to after successful checkout
            cancel_url: URL to redirect to if checkout is cancelled

        Returns:
            CheckoutResponse with the checkout URL
        """
        # Validate plan
        if plan not in [SubscriptionPlan.STARTER, SubscriptionPlan.PRO, SubscriptionPlan.ENTERPRISE]:
            raise ValueError(f"Invalid plan: {plan}")

        # Get variant ID for the plan
        variant_id = PLAN_VARIANTS.get(plan, {}).get(billing_interval)
        if not variant_id:
            raise ValueError(f"No variant configured for {plan} {billing_interval}")

        # Create checkout options
        options = CheckoutOptions(
            variant_id=variant_id,
            workspace_id=str(workspace.id),
            user_email=user.email,
            user_name=f"{user.first_name} {user.last_name}".strip() or user.email,
            custom_data={
                "workspace_id": str(workspace.id),
                "workspace_name": workspace.name,
                "user_id": str(user.id),
            },
            success_url=success_url,
            cancel_url=cancel_url,
        )

        return self.client.create_checkout(options)

    def get_customer_portal_url(self, workspace) -> Optional[str]:
        """
        Get the customer portal URL for a workspace.

        Returns None if the workspace doesn't have an active subscription.
        """
        subscription = Subscription.objects.filter(workspace=workspace).first()

        if not subscription or not subscription.lemon_squeezy_customer_id:
            return None

        try:
            return self.client.get_customer_portal_url(subscription.lemon_squeezy_customer_id)
        except LemonSqueezyError as e:
            logger.error(f"Failed to get customer portal URL: {e}")
            return subscription.customer_portal_url

    def cancel_subscription(self, workspace, at_period_end: bool = True) -> Subscription:
        """
        Cancel a workspace's subscription.

        Args:
            workspace: The workspace to cancel
            at_period_end: If True, cancel at the end of the billing period

        Returns:
            Updated subscription
        """
        subscription = Subscription.objects.filter(workspace=workspace).first()

        if not subscription:
            raise ValueError("Workspace has no subscription")

        if subscription.is_free_plan:
            raise ValueError("Cannot cancel free plan")

        if subscription.lemon_squeezy_subscription_id:
            try:
                self.client.cancel_subscription(subscription.lemon_squeezy_subscription_id)
            except LemonSqueezyError as e:
                logger.error(f"Failed to cancel subscription in Lemon Squeezy: {e}")
                raise

        subscription.cancel(at_period_end=at_period_end)

        # Log the event
        SubscriptionEvent.objects.create(
            subscription=subscription,
            event_type="subscription.cancelled",
            event_data={"at_period_end": at_period_end},
        )

        return subscription

    def resume_subscription(self, workspace) -> Subscription:
        """
        Resume a cancelled subscription.

        Args:
            workspace: The workspace to resume

        Returns:
            Updated subscription
        """
        subscription = Subscription.objects.filter(workspace=workspace).first()

        if not subscription:
            raise ValueError("Workspace has no subscription")

        if not subscription.is_cancelled:
            raise ValueError("Subscription is not cancelled")

        if subscription.lemon_squeezy_subscription_id:
            try:
                self.client.resume_subscription(subscription.lemon_squeezy_subscription_id)
            except LemonSqueezyError as e:
                logger.error(f"Failed to resume subscription in Lemon Squeezy: {e}")
                raise

        subscription.cancel_at_period_end = False
        subscription.status = SubscriptionStatus.ACTIVE
        subscription.save()

        # Log the event
        SubscriptionEvent.objects.create(
            subscription=subscription,
            event_type="subscription.resumed",
            event_data={},
        )

        return subscription

    @transaction.atomic
    def sync_from_webhook(self, event_type: str, event_data: dict) -> Optional[Subscription]:
        """
        Sync subscription data from a Lemon Squeezy webhook event.

        Args:
            event_type: The webhook event type
            event_data: The webhook event data

        Returns:
            Updated subscription or None
        """
        attributes = event_data.get("attributes", {})
        custom_data = attributes.get("first_subscription_item", {}).get("custom_data", {})

        # Try to get workspace_id from custom data
        workspace_id = custom_data.get("workspace_id")
        if not workspace_id:
            # Try to find by Lemon Squeezy subscription ID
            ls_subscription_id = str(event_data.get("id"))
            subscription = Subscription.objects.filter(
                lemon_squeezy_subscription_id=ls_subscription_id
            ).first()
            if subscription:
                workspace_id = str(subscription.workspace_id)

        if not workspace_id:
            logger.warning(f"Could not determine workspace for webhook event: {event_type}")
            return None

        # Get or create subscription
        from plane.db.models import Workspace

        try:
            workspace = Workspace.objects.get(id=workspace_id)
        except Workspace.DoesNotExist:
            logger.error(f"Workspace {workspace_id} not found for webhook event")
            return None

        subscription = self.get_or_create_subscription(workspace)

        # Update subscription from webhook data
        subscription.lemon_squeezy_subscription_id = str(event_data.get("id"))
        subscription.lemon_squeezy_customer_id = str(attributes.get("customer_id", ""))
        subscription.lemon_squeezy_order_id = str(attributes.get("order_id", ""))
        subscription.lemon_squeezy_product_id = str(attributes.get("product_id", ""))
        subscription.lemon_squeezy_variant_id = str(attributes.get("variant_id", ""))

        # Map status
        status_map = {
            "active": SubscriptionStatus.ACTIVE,
            "cancelled": SubscriptionStatus.CANCELLED,
            "expired": SubscriptionStatus.EXPIRED,
            "past_due": SubscriptionStatus.PAST_DUE,
            "paused": SubscriptionStatus.PAUSED,
            "unpaid": SubscriptionStatus.UNPAID,
            "on_trial": SubscriptionStatus.ON_TRIAL,
        }
        subscription.status = status_map.get(
            attributes.get("status"),
            SubscriptionStatus.ACTIVE,
        )

        # Map plan from variant ID
        variant_id = str(attributes.get("variant_id", ""))
        subscription.plan = self._get_plan_from_variant(variant_id)

        # Billing interval
        billing_anchor = attributes.get("billing_anchor")
        if billing_anchor:
            subscription.billing_interval = (
                BillingInterval.YEARLY if billing_anchor == 1 else BillingInterval.MONTHLY
            )

        # Card info
        card_brand = attributes.get("card_brand")
        card_last_four = attributes.get("card_last_four")
        if card_brand:
            subscription.card_brand = card_brand
        if card_last_four:
            subscription.card_last_four = card_last_four

        # Dates
        if attributes.get("trial_ends_at"):
            subscription.trial_ends_at = timezone.datetime.fromisoformat(
                attributes["trial_ends_at"].replace("Z", "+00:00")
            )
        if attributes.get("renews_at"):
            subscription.renews_at = timezone.datetime.fromisoformat(
                attributes["renews_at"].replace("Z", "+00:00")
            )
        if attributes.get("ends_at"):
            subscription.ends_at = timezone.datetime.fromisoformat(
                attributes["ends_at"].replace("Z", "+00:00")
            )

        # URLs
        urls = attributes.get("urls", {})
        subscription.update_payment_method_url = urls.get("update_payment_method")
        subscription.customer_portal_url = urls.get("customer_portal")

        subscription.save()

        # Log the event
        SubscriptionEvent.objects.create(
            subscription=subscription,
            event_type=event_type,
            event_data=event_data,
        )

        logger.info(f"Synced subscription {subscription.id} from webhook: {event_type}")

        return subscription

    def _get_plan_from_variant(self, variant_id: str) -> str:
        """Map a Lemon Squeezy variant ID to a plan."""
        for plan, intervals in PLAN_VARIANTS.items():
            for interval, vid in intervals.items():
                if vid and str(vid) == variant_id:
                    return plan
        return SubscriptionPlan.FREE

    def get_subscription_details(self, workspace) -> dict:
        """
        Get detailed subscription information for a workspace.

        Returns a dictionary with subscription details suitable for the frontend.
        """
        subscription = self.get_or_create_subscription(workspace)

        return {
            "id": str(subscription.id),
            "plan": subscription.plan,
            "status": subscription.status,
            "billing_interval": subscription.billing_interval,
            "is_active": subscription.is_active,
            "is_on_trial": subscription.is_on_trial,
            "is_cancelled": subscription.is_cancelled,
            "is_free_plan": subscription.is_free_plan,
            "trial_ends_at": subscription.trial_ends_at.isoformat() if subscription.trial_ends_at else None,
            "renews_at": subscription.renews_at.isoformat() if subscription.renews_at else None,
            "ends_at": subscription.ends_at.isoformat() if subscription.ends_at else None,
            "days_until_renewal": subscription.days_until_renewal,
            "card_brand": subscription.card_brand,
            "card_last_four": subscription.card_last_four,
            "customer_portal_url": subscription.customer_portal_url,
            "update_payment_method_url": subscription.update_payment_method_url,
        }
