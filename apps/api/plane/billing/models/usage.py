# Copyright (c) 2023-present Plane Software, Inc. and contributors
# SPDX-License-Identifier: AGPL-3.0-only
# See the LICENSE file for details.

"""
Usage tracking models for feature gating.

These models track:
- Feature usage per workspace
- Usage events for analytics
"""

import uuid
from django.db import models
from django.utils import timezone


class FeatureUsage(models.Model):
    """
    Tracks feature usage for a workspace.

    This is used to enforce limits based on subscription plans.
    For example:
    - Number of projects
    - Number of members
    - Storage used
    - API calls
    """

    id = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False,
        db_index=True,
        primary_key=True,
    )

    workspace = models.ForeignKey(
        "db.Workspace",
        on_delete=models.CASCADE,
        related_name="feature_usage",
    )

    feature_key = models.CharField(max_length=100, db_index=True)
    current_usage = models.BigIntegerField(default=0)
    limit = models.BigIntegerField(null=True, blank=True)  # null = unlimited

    # Period tracking for resettable limits (e.g., monthly API calls)
    period_start = models.DateTimeField(null=True, blank=True)
    period_end = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "billing_feature_usage"
        verbose_name = "Feature Usage"
        verbose_name_plural = "Feature Usage"
        unique_together = ["workspace", "feature_key"]

    def __str__(self):
        return f"{self.workspace.name} - {self.feature_key}: {self.current_usage}"

    @property
    def is_at_limit(self) -> bool:
        """Check if the workspace has reached the limit for this feature."""
        if self.limit is None:
            return False
        return self.current_usage >= self.limit

    @property
    def usage_percentage(self) -> float:
        """Get the usage as a percentage of the limit."""
        if self.limit is None or self.limit == 0:
            return 0.0
        return (self.current_usage / self.limit) * 100

    @property
    def remaining(self) -> int | None:
        """Get the remaining usage before hitting the limit."""
        if self.limit is None:
            return None
        return max(0, self.limit - self.current_usage)

    def increment(self, amount: int = 1) -> bool:
        """
        Increment the usage counter.

        Returns True if the increment was successful (not at limit).
        Returns False if the limit would be exceeded.
        """
        if self.limit is not None and self.current_usage + amount > self.limit:
            return False
        self.current_usage += amount
        self.save()
        return True

    def decrement(self, amount: int = 1):
        """Decrement the usage counter."""
        self.current_usage = max(0, self.current_usage - amount)
        self.save()

    def reset(self):
        """Reset the usage counter to zero."""
        self.current_usage = 0
        self.save()


class UsageEvent(models.Model):
    """
    Tracks individual usage events for analytics and auditing.

    This provides a detailed log of feature usage that can be used for:
    - Billing calculations
    - Usage analytics
    - Debugging
    """

    id = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False,
        db_index=True,
        primary_key=True,
    )

    workspace = models.ForeignKey(
        "db.Workspace",
        on_delete=models.CASCADE,
        related_name="usage_events",
    )

    user = models.ForeignKey(
        "db.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="usage_events",
    )

    feature_key = models.CharField(max_length=100, db_index=True)
    event_type = models.CharField(max_length=50)  # e.g., "increment", "decrement", "reset"
    amount = models.IntegerField(default=1)
    metadata = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = "billing_usage_events"
        verbose_name = "Usage Event"
        verbose_name_plural = "Usage Events"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["workspace", "feature_key", "created_at"]),
        ]

    def __str__(self):
        return f"{self.workspace.name} - {self.feature_key} - {self.event_type}"
