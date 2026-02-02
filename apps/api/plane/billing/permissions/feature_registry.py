# Copyright (c) 2023-present Plane Software, Inc. and contributors
# SPDX-License-Identifier: AGPL-3.0-only
# See the LICENSE file for details.

"""
Feature Registry and Permission System.

This module provides a centralized feature registry that defines:
- Available features and their limits per plan
- Feature permissions and access rules
- Feature gating helpers
"""

from dataclasses import dataclass
from enum import Enum
from typing import Callable, Optional

from plane.billing.models.subscription import SubscriptionPlan


class FeatureStatus(Enum):
    """Feature availability status."""

    AVAILABLE = "available"
    LIMITED = "limited"
    UNAVAILABLE = "unavailable"
    LOCKED = "locked"


@dataclass
class FeatureDefinition:
    """Definition of a feature with its limits per plan."""

    key: str
    name: str
    description: str
    # Plan limits: None means unlimited
    limits: dict[SubscriptionPlan, Optional[int]]
    # Whether the feature is in beta
    beta: bool = False
    # Whether the feature requires an enterprise plan
    enterprise_only: bool = False
    # Custom validation function
    validator: Optional[Callable] = None


# Feature registry
FEATURE_REGISTRY: dict[str, FeatureDefinition] = {}


def register_feature(feature: FeatureDefinition):
    """Register a feature in the registry."""
    FEATURE_REGISTRY[feature.key] = feature


def get_feature(key: str) -> Optional[FeatureDefinition]:
    """Get a feature definition from the registry."""
    return FEATURE_REGISTRY.get(key)


def get_all_features() -> dict[str, FeatureDefinition]:
    """Get all registered features."""
    return FEATURE_REGISTRY.copy()


def register_default_features():
    """Register all default features."""

    # Project features
    register_feature(
        FeatureDefinition(
            key="projects",
            name="Projects",
            description="Number of projects allowed",
            limits={
                SubscriptionPlan.FREE: 3,
                SubscriptionPlan.STARTER: 10,
                SubscriptionPlan.PRO: None,
                SubscriptionPlan.ENTERPRISE: None,
            },
        )
    )

    # Member features
    register_feature(
        FeatureDefinition(
            key="members",
            name="Team Members",
            description="Number of team members allowed",
            limits={
                SubscriptionPlan.FREE: 5,
                SubscriptionPlan.STARTER: 20,
                SubscriptionPlan.PRO: None,
                SubscriptionPlan.ENTERPRISE: None,
            },
        )
    )

    # Storage features
    register_feature(
        FeatureDefinition(
            key="storage_mb",
            name="Storage",
            description="Storage limit in MB",
            limits={
                SubscriptionPlan.FREE: 100,
                SubscriptionPlan.STARTER: 1000,
                SubscriptionPlan.PRO: 10000,
                SubscriptionPlan.ENTERPRISE: None,
            },
        )
    )

    # API calls features
    register_feature(
        FeatureDefinition(
            key="api_calls_per_month",
            name="API Calls",
            description="Number of API calls per month",
            limits={
                SubscriptionPlan.FREE: 1000,
                SubscriptionPlan.STARTER: 10000,
                SubscriptionPlan.PRO: 100000,
                SubscriptionPlan.ENTERPRISE: None,
            },
        )
    )

    # File uploads features
    register_feature(
        FeatureDefinition(
            key="file_uploads_per_month",
            name="File Uploads",
            description="Number of file uploads per month",
            limits={
                SubscriptionPlan.FREE: 50,
                SubscriptionPlan.STARTER: 500,
                SubscriptionPlan.PRO: None,
                SubscriptionPlan.ENTERPRISE: None,
            },
        )
    )

    # Integration features
    register_feature(
        FeatureDefinition(
            key="integrations",
            name="Integrations",
            description="Number of integrations allowed",
            limits={
                SubscriptionPlan.FREE: 1,
                SubscriptionPlan.STARTER: 5,
                SubscriptionPlan.PRO: None,
                SubscriptionPlan.ENTERPRISE: None,
            },
        )
    )

    # Custom fields features
    register_feature(
        FeatureDefinition(
            key="custom_fields",
            name="Custom Fields",
            description="Number of custom fields allowed per project",
            limits={
                SubscriptionPlan.FREE: 0,
                SubscriptionPlan.STARTER: 10,
                SubscriptionPlan.PRO: None,
                SubscriptionPlan.ENTERPRISE: None,
            },
        )
    )

    # Automation features
    register_feature(
        FeatureDefinition(
            key="automations",
            name="Automations",
            description="Number of automation workflows allowed",
            limits={
                SubscriptionPlan.FREE: 0,
                SubscriptionPlan.STARTER: 5,
                SubscriptionPlan.PRO: None,
                SubscriptionPlan.ENTERPRISE: None,
            },
        )
    )

    # AI features
    register_feature(
        FeatureDefinition(
            key="ai_features",
            name="AI Features",
            description="Number of AI feature uses per month",
            limits={
                SubscriptionPlan.FREE: 0,
                SubscriptionPlan.STARTER: 100,
                SubscriptionPlan.PRO: 1000,
                SubscriptionPlan.ENTERPRISE: None,
            },
        )
    )

    # SSO features (enterprise only)
    register_feature(
        FeatureDefinition(
            key="sso",
            name="SSO (SAML/OIDC)",
            description="Single Sign-On with SAML or OIDC",
            limits={
                SubscriptionPlan.FREE: 0,
                SubscriptionPlan.STARTER: 0,
                SubscriptionPlan.PRO: 0,
                SubscriptionPlan.ENTERPRISE: None,
            },
            enterprise_only=True,
        )
    )

    # Advanced security features
    register_feature(
        FeatureDefinition(
            key="advanced_security",
            name="Advanced Security",
            description="Audit logs, IP restrictions, and advanced security features",
            limits={
                SubscriptionPlan.FREE: 0,
                SubscriptionPlan.STARTER: 0,
                SubscriptionPlan.PRO: 0,
                SubscriptionPlan.ENTERPRISE: None,
            },
            enterprise_only=True,
        )
    )

    # Custom domain features
    register_feature(
        FeatureDefinition(
            key="custom_domain",
            name="Custom Domain",
            description="Use a custom domain for your workspace",
            limits={
                SubscriptionPlan.FREE: 0,
                SubscriptionPlan.STARTER: 0,
                SubscriptionPlan.PRO: 0,
                SubscriptionPlan.ENTERPRISE: None,
            },
            enterprise_only=True,
        )
    )


class FeatureChecker:
    """
    Helper class for checking feature access.
    """

    def __init__(self, workspace):
        self.workspace = workspace

    def get_limit(self, feature_key: str) -> Optional[int]:
        """Get the limit for a feature based on workspace plan."""
        feature = get_feature(feature_key)
        if not feature:
            return None

        from plane.billing.models.subscription import Subscription

        subscription = Subscription.objects.filter(workspace=self.workspace).first()
        if not subscription:
            return feature.limits.get(SubscriptionPlan.FREE, None)

        return feature.limits.get(subscription.plan, None)

    def can_use(self, feature_key: str, amount: int = 1) -> tuple[bool, str]:
        """
        Check if the workspace can use a feature.

        Returns (can_use, reason)
        """
        feature = get_feature(feature_key)
        if not feature:
            return True, "Feature not registered"

        from plane.billing.models.subscription import Subscription

        subscription = Subscription.objects.filter(workspace=self.workspace).first()
        current_plan = subscription.plan if subscription else SubscriptionPlan.FREE

        # Check enterprise-only feature
        if feature.enterprise_only and current_plan != SubscriptionPlan.ENTERPRISE:
            return False, f"{feature.name} requires an Enterprise plan"

        # Get the limit for the current plan
        limit = feature.limits.get(current_plan)

        # Unlimited
        if limit is None:
            return True, None

        # Check current usage
        from plane.billing.models.usage import FeatureUsage

        usage = FeatureUsage.objects.filter(
            workspace=self.workspace,
            feature_key=feature_key,
        ).first()

        current_usage = usage.current_usage if usage else 0

        if current_usage + amount > limit:
            remaining = limit - current_usage
            return False, f"{feature.name} limit reached. {remaining} remaining."

        return True, None

    def get_status(self, feature_key: str) -> tuple[FeatureStatus, str]:
        """
        Get the status of a feature for the workspace.

        Returns (status, message)
        """
        feature = get_feature(feature_key)
        if not feature:
            return FeatureStatus.AVAILABLE, "Feature not registered"

        from plane.billing.models.subscription import Subscription

        subscription = Subscription.objects.filter(workspace=self.workspace).first()
        current_plan = subscription.plan if subscription else SubscriptionPlan.FREE

        # Check enterprise-only
        if feature.enterprise_only and current_plan != SubscriptionPlan.ENTERPRISE:
            return FeatureStatus.LOCKED, f"{feature.name} requires Enterprise plan"

        # Get limit
        limit = feature.limits.get(current_plan)

        if limit is None:
            return FeatureStatus.AVAILABLE, "Unlimited"

        # Get current usage
        from plane.billing.models.usage import FeatureUsage

        usage = FeatureUsage.objects.filter(
            workspace=self.workspace,
            feature_key=feature_key,
        ).first()

        current_usage = usage.current_usage if usage else 0

        if current_usage >= limit:
            return FeatureStatus.UNAVAILABLE, "Limit reached"

        if current_usage >= limit * 0.8:
            return FeatureStatus.LIMITED, f"{current_usage}/{limit} used"

        return FeatureStatus.AVAILABLE, f"{current_usage}/{limit} used"


# Initialize default features
register_default_features()
