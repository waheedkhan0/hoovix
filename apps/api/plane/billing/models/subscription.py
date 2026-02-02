# Copyright (c) 2023-present Plane Software, Inc. and contributors
# SPDX-License-Identifier: AGPL-3.0-only
# See the LICENSE file for details.

"""
Subscription models for Lemon Squeezy integration.

These models track:
- Subscription plans and their features
- Workspace subscriptions
- Subscription lifecycle events
"""

import uuid
from django.db import models
from django.utils import timezone


class SubscriptionPlan(models.TextChoices):
    """Available subscription plans."""

    FREE = "free", "Free"
    STARTER = "starter", "Starter"
    PRO = "pro", "Pro"
    ENTERPRISE = "enterprise", "Enterprise"


class SubscriptionStatus(models.TextChoices):
    """Subscription status values from Lemon Squeezy."""

    ACTIVE = "active", "Active"
    CANCELLED = "cancelled", "Cancelled"
    EXPIRED = "expired", "Expired"
    PAST_DUE = "past_due", "Past Due"
    PAUSED = "paused", "Paused"
    UNPAID = "unpaid", "Unpaid"
    ON_TRIAL = "on_trial", "On Trial"


class BillingInterval(models.TextChoices):
    """Billing interval options."""

    MONTHLY = "month", "Monthly"
    YEARLY = "year", "Yearly"


class Subscription(models.Model):
    """
    Represents a workspace's subscription to a plan.

    This model stores the subscription data from Lemon Squeezy and links
    it to a workspace in the Plane system.
    """

    id = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False,
        db_index=True,
        primary_key=True,
    )

    # Link to workspace
    workspace = models.OneToOneField(
        "db.Workspace",
        on_delete=models.CASCADE,
        related_name="subscription",
    )

    # Lemon Squeezy identifiers
    lemon_squeezy_subscription_id = models.CharField(
        max_length=255,
        unique=True,
        null=True,
        blank=True,
        db_index=True,
    )
    lemon_squeezy_customer_id = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        db_index=True,
    )
    lemon_squeezy_order_id = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )
    lemon_squeezy_product_id = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )
    lemon_squeezy_variant_id = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )

    # Subscription details
    plan = models.CharField(
        max_length=20,
        choices=SubscriptionPlan.choices,
        default=SubscriptionPlan.FREE,
    )
    status = models.CharField(
        max_length=20,
        choices=SubscriptionStatus.choices,
        default=SubscriptionStatus.ACTIVE,
    )
    billing_interval = models.CharField(
        max_length=10,
        choices=BillingInterval.choices,
        null=True,
        blank=True,
    )

    # Billing information
    card_brand = models.CharField(max_length=50, null=True, blank=True)
    card_last_four = models.CharField(max_length=4, null=True, blank=True)

    # Dates
    trial_ends_at = models.DateTimeField(null=True, blank=True)
    renews_at = models.DateTimeField(null=True, blank=True)
    ends_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Cancellation
    cancelled_at = models.DateTimeField(null=True, blank=True)
    cancel_at_period_end = models.BooleanField(default=False)

    # URLs from Lemon Squeezy
    update_payment_method_url = models.URLField(max_length=500, null=True, blank=True)
    customer_portal_url = models.URLField(max_length=500, null=True, blank=True)

    class Meta:
        db_table = "billing_subscriptions"
        verbose_name = "Subscription"
        verbose_name_plural = "Subscriptions"

    def __str__(self):
        return f"{self.workspace.name} - {self.plan} ({self.status})"

    @property
    def is_active(self) -> bool:
        """Check if the subscription is currently active."""
        return self.status in [
            SubscriptionStatus.ACTIVE,
            SubscriptionStatus.ON_TRIAL,
        ]

    @property
    def is_on_trial(self) -> bool:
        """Check if the subscription is on trial."""
        return self.status == SubscriptionStatus.ON_TRIAL

    @property
    def is_cancelled(self) -> bool:
        """Check if the subscription is cancelled."""
        return self.status == SubscriptionStatus.CANCELLED or self.cancel_at_period_end

    @property
    def is_free_plan(self) -> bool:
        """Check if this is a free plan."""
        return self.plan == SubscriptionPlan.FREE

    @property
    def days_until_renewal(self) -> int | None:
        """Get the number of days until renewal."""
        if not self.renews_at:
            return None
        delta = self.renews_at - timezone.now()
        return max(0, delta.days)

    def cancel(self, at_period_end: bool = True):
        """Cancel the subscription."""
        self.cancel_at_period_end = at_period_end
        if not at_period_end:
            self.status = SubscriptionStatus.CANCELLED
            self.cancelled_at = timezone.now()
        self.save()


class SubscriptionEvent(models.Model):
    """
    Tracks subscription lifecycle events.

    This is useful for:
    - Audit trail
    - Debugging webhook issues
    - Analytics
    """

    id = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False,
        db_index=True,
        primary_key=True,
    )

    subscription = models.ForeignKey(
        Subscription,
        on_delete=models.CASCADE,
        related_name="events",
    )

    event_type = models.CharField(max_length=100)
    event_data = models.JSONField(default=dict)
    lemon_squeezy_event_id = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        db_index=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "billing_subscription_events"
        verbose_name = "Subscription Event"
        verbose_name_plural = "Subscription Events"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.subscription.workspace.name} - {self.event_type}"
