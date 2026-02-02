# Copyright (c) 2023-present Plane Software, Inc. and contributors
# SPDX-License-Identifier: AGPL-3.0-only
# See the LICENSE file for details.

"""
Usage Tracker Service.

This module provides functionality for tracking feature usage
and enforcing limits based on subscription plans.
"""

import logging
from typing import Optional

from django.db import transaction
from django.utils import timezone

from plane.billing.models.subscription import Subscription, SubscriptionPlan
from plane.billing.models.usage import FeatureUsage, UsageEvent

logger = logging.getLogger(__name__)


# Feature limits by plan
# None means unlimited
PLAN_LIMITS = {
    SubscriptionPlan.FREE: {
        "projects": 3,
        "members": 5,
        "storage_mb": 100,
        "api_calls_per_month": 1000,
        "file_uploads_per_month": 50,
        "integrations": 1,
        "custom_fields": 0,
        "automations": 0,
        "ai_features": 0,
    },
    SubscriptionPlan.STARTER: {
        "projects": 10,
        "members": 20,
        "storage_mb": 1000,
        "api_calls_per_month": 10000,
        "file_uploads_per_month": 500,
        "integrations": 5,
        "custom_fields": 10,
        "automations": 5,
        "ai_features": 100,
    },
    SubscriptionPlan.PRO: {
        "projects": None,  # Unlimited
        "members": None,
        "storage_mb": 10000,
        "api_calls_per_month": 100000,
        "file_uploads_per_month": None,
        "integrations": None,
        "custom_fields": None,
        "automations": None,
        "ai_features": 1000,
    },
    SubscriptionPlan.ENTERPRISE: {
        "projects": None,
        "members": None,
        "storage_mb": None,
        "api_calls_per_month": None,
        "file_uploads_per_month": None,
        "integrations": None,
        "custom_fields": None,
        "automations": None,
        "ai_features": None,
    },
}


class UsageTracker:
    """
    Service for tracking and enforcing feature usage limits.

    Usage:
        tracker = UsageTracker(workspace)
        if tracker.can_use("projects"):
            tracker.increment("projects")
    """

    def __init__(self, workspace):
        self.workspace = workspace
        self._subscription = None

    @property
    def subscription(self) -> Subscription:
        """Get the workspace's subscription, creating one if needed."""
        if self._subscription is None:
            self._subscription, _ = Subscription.objects.get_or_create(
                workspace=self.workspace,
                defaults={
                    "plan": SubscriptionPlan.FREE,
                },
            )
        return self._subscription

    @property
    def plan(self) -> str:
        """Get the current plan."""
        return self.subscription.plan

    def get_limit(self, feature_key: str) -> Optional[int]:
        """
        Get the limit for a feature based on the current plan.

        Returns None if the feature is unlimited.
        """
        plan_limits = PLAN_LIMITS.get(self.plan, PLAN_LIMITS[SubscriptionPlan.FREE])
        return plan_limits.get(feature_key)

    def get_usage(self, feature_key: str) -> int:
        """Get the current usage for a feature."""
        usage = FeatureUsage.objects.filter(
            workspace=self.workspace,
            feature_key=feature_key,
        ).first()

        return usage.current_usage if usage else 0

    def get_or_create_usage(self, feature_key: str) -> FeatureUsage:
        """Get or create a usage record for a feature."""
        limit = self.get_limit(feature_key)

        usage, created = FeatureUsage.objects.get_or_create(
            workspace=self.workspace,
            feature_key=feature_key,
            defaults={
                "limit": limit,
                "current_usage": 0,
            },
        )

        # Update limit if plan changed
        if usage.limit != limit:
            usage.limit = limit
            usage.save()

        return usage

    def can_use(self, feature_key: str, amount: int = 1) -> bool:
        """
        Check if the workspace can use a feature.

        Args:
            feature_key: The feature to check
            amount: The amount to use (default 1)

        Returns:
            True if the feature can be used, False if at limit
        """
        limit = self.get_limit(feature_key)

        # Unlimited
        if limit is None:
            return True

        current_usage = self.get_usage(feature_key)
        return current_usage + amount <= limit

    @transaction.atomic
    def increment(
        self,
        feature_key: str,
        amount: int = 1,
        user=None,
        metadata: Optional[dict] = None,
    ) -> bool:
        """
        Increment usage for a feature.

        Args:
            feature_key: The feature to increment
            amount: The amount to increment by
            user: The user performing the action (optional)
            metadata: Additional metadata for the event

        Returns:
            True if successful, False if at limit
        """
        usage = self.get_or_create_usage(feature_key)

        if not usage.increment(amount):
            logger.warning(
                f"Workspace {self.workspace.id} at limit for {feature_key}"
            )
            return False

        # Log the event
        UsageEvent.objects.create(
            workspace=self.workspace,
            user=user,
            feature_key=feature_key,
            event_type="increment",
            amount=amount,
            metadata=metadata or {},
        )

        return True

    @transaction.atomic
    def decrement(
        self,
        feature_key: str,
        amount: int = 1,
        user=None,
        metadata: Optional[dict] = None,
    ):
        """
        Decrement usage for a feature.

        Args:
            feature_key: The feature to decrement
            amount: The amount to decrement by
            user: The user performing the action (optional)
            metadata: Additional metadata for the event
        """
        usage = self.get_or_create_usage(feature_key)
        usage.decrement(amount)

        # Log the event
        UsageEvent.objects.create(
            workspace=self.workspace,
            user=user,
            feature_key=feature_key,
            event_type="decrement",
            amount=amount,
            metadata=metadata or {},
        )

    def get_all_usage(self) -> dict:
        """
        Get usage information for all features.

        Returns a dictionary with feature keys and their usage info.
        """
        result = {}

        for feature_key in PLAN_LIMITS.get(self.plan, {}).keys():
            limit = self.get_limit(feature_key)
            usage = self.get_usage(feature_key)

            result[feature_key] = {
                "current": usage,
                "limit": limit,
                "remaining": None if limit is None else max(0, limit - usage),
                "percentage": 0 if limit is None or limit == 0 else (usage / limit) * 100,
                "is_at_limit": limit is not None and usage >= limit,
            }

        return result

    def reset_monthly_usage(self):
        """
        Reset usage counters for monthly-resettable features.

        This should be called at the start of each billing period.
        """
        monthly_features = [
            "api_calls_per_month",
            "file_uploads_per_month",
            "ai_features",
        ]

        for feature_key in monthly_features:
            usage = FeatureUsage.objects.filter(
                workspace=self.workspace,
                feature_key=feature_key,
            ).first()

            if usage:
                usage.reset()
                usage.period_start = timezone.now()
                usage.save()

                # Log the reset
                UsageEvent.objects.create(
                    workspace=self.workspace,
                    feature_key=feature_key,
                    event_type="reset",
                    amount=0,
                    metadata={"reason": "monthly_reset"},
                )

    def sync_actual_usage(self):
        """
        Sync usage counters with actual database counts.

        This is useful for correcting any drift between tracked
        usage and actual resource counts.
        """
        from plane.db.models import Project, WorkspaceMember

        # Sync project count
        actual_projects = Project.objects.filter(
            workspace=self.workspace,
            is_deleted=False,
        ).count()

        project_usage = self.get_or_create_usage("projects")
        if project_usage.current_usage != actual_projects:
            project_usage.current_usage = actual_projects
            project_usage.save()

        # Sync member count
        actual_members = WorkspaceMember.objects.filter(
            workspace=self.workspace,
            is_active=True,
        ).count()

        member_usage = self.get_or_create_usage("members")
        if member_usage.current_usage != actual_members:
            member_usage.current_usage = actual_members
            member_usage.save()


def check_feature_limit(workspace, feature_key: str, amount: int = 1) -> bool:
    """
    Convenience function to check if a workspace can use a feature.

    Usage:
        if check_feature_limit(workspace, "projects"):
            # Create project
    """
    tracker = UsageTracker(workspace)
    return tracker.can_use(feature_key, amount)


def increment_feature_usage(
    workspace,
    feature_key: str,
    amount: int = 1,
    user=None,
) -> bool:
    """
    Convenience function to increment feature usage.

    Usage:
        if increment_feature_usage(workspace, "projects"):
            # Project created successfully
    """
    tracker = UsageTracker(workspace)
    return tracker.increment(feature_key, amount, user)


def decrement_feature_usage(
    workspace,
    feature_key: str,
    amount: int = 1,
    user=None,
):
    """
    Convenience function to decrement feature usage.

    Usage:
        decrement_feature_usage(workspace, "projects")
    """
    tracker = UsageTracker(workspace)
    tracker.decrement(feature_key, amount, user)
