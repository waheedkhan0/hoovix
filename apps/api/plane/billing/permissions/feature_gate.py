# Copyright (c) 2023-present Plane Software, Inc. and contributors
# SPDX-License-Identifier: AGPL-3.0-only
# See the LICENSE file for details.

"""
Feature Gate Permissions for Django REST Framework.

This module provides permission classes and decorators for enforcing
feature limits on API endpoints.
"""

import logging
from functools import wraps
from typing import Callable

from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework.exceptions import PermissionDenied

from plane.billing.permissions.feature_registry import FeatureChecker, get_feature

logger = logging.getLogger(__name__)


class FeaturePermission(permissions.BasePermission):
    """
    Permission class that checks feature limits for a workspace.

    Usage:
        class MyView(APIView):
            permission_classes = [FeaturePermission]
            feature = "projects"

            def check_feature(self, request):
                return request.user.workspace  # Return the workspace
    """

    feature_key: str = None
    feature_amount: int = 1

    def has_permission(self, request, view: APIView) -> bool:
        """Check if the user has permission based on feature limits."""
        # Get the workspace from the view
        workspace = getattr(view, "get_workspace", lambda: None)()

        if not workspace:
            # Try to get from the request
            workspace = getattr(request, "workspace", None)

        if not workspace:
            return True  # Allow if no workspace context

        # Get feature key from view or class attribute
        feature_key = getattr(view, "feature_key", None) or self.feature_key

        if not feature_key:
            return True  # No feature gate configured

        # Check feature access
        checker = FeatureChecker(workspace)
        can_use, reason = checker.can_use(feature_key, self.feature_amount)

        if not can_use:
            logger.info(
                f"Feature gate blocked: {feature_key} for workspace {workspace.id} - {reason}"
            )
            # Store the reason for the error handler
            request.feature_gate_reason = reason
            request.feature_gate_feature = feature_key

        return can_use

    def get_permission_denied_message(self, request) -> str:
        """Customize the permission denied message."""
        return getattr(request, "feature_gate_reason", "Feature not available")


class PlanPermission(permissions.BasePermission):
    """
    Permission class that checks minimum plan requirement.

    Usage:
        class MyView(APIView):
            permission_classes = [PlanPermission]
            required_plan = "pro"
    """

    required_plan: str = None
    message = "This feature requires a higher plan."

    def has_permission(self, request, view: APIView) -> bool:
        """Check if the user's workspace meets the plan requirement."""
        # Get the workspace from the request
        workspace = getattr(request, "workspace", None)

        if not workspace:
            return True

        # Get required plan from view or class attribute
        required_plan = getattr(view, "required_plan", None) or self.required_plan

        if not required_plan:
            return True

        # Check plan
        from plane.billing.models.subscription import Subscription, SubscriptionPlan

        subscription = Subscription.objects.filter(workspace=workspace).first()
        current_plan = subscription.plan if subscription else SubscriptionPlan.FREE

        plan_hierarchy = [
            SubscriptionPlan.FREE,
            SubscriptionPlan.STARTER,
            SubscriptionPlan.PRO,
            SubscriptionPlan.ENTERPRISE,
        ]

        try:
            required_index = plan_hierarchy.index(SubscriptionPlan(required_plan))
            current_index = plan_hierarchy.index(current_plan)
            return current_index >= required_index
        except (ValueError, KeyError):
            return True


def require_feature(feature_key: str, amount: int = 1):
    """
    Decorator to require a feature for a view method.

    Usage:
        @require_feature("projects")
        def create_project(request):
            ...
    """

    def decorator(view_func: Callable):
        @wraps(view_func)
        def wrapper(view, request, *args, **kwargs):
            workspace = getattr(request, "workspace", None)

            if not workspace:
                return view_func(view, request, *args, **kwargs)

            checker = FeatureChecker(workspace)
            can_use, reason = checker.can_use(feature_key, amount)

            if not can_use:
                logger.info(
                    f"Feature gate blocked: {feature_key} for workspace {workspace.id} - {reason}"
                )
                raise PermissionDenied(detail=reason)

            return view_func(view, request, *args, **kwargs)

        return wrapper

    return decorator


def require_plan(required_plan: str):
    """
    Decorator to require a minimum plan for a view method.

    Usage:
        @require_plan("pro")
        def create_automation(request):
            ...
    """

    def decorator(view_func: Callable):
        @wraps(view_func)
        def wrapper(view, request, *args, **kwargs):
            workspace = getattr(request, "workspace", None)

            if not workspace:
                return view_func(view, request, *args, **kwargs)

            from plane.billing.models.subscription import Subscription, SubscriptionPlan

            subscription = Subscription.objects.filter(workspace=workspace).first()
            current_plan = subscription.plan if subscription else SubscriptionPlan.FREE

            plan_hierarchy = [
                SubscriptionPlan.FREE,
                SubscriptionPlan.STARTER,
                SubscriptionPlan.PRO,
                SubscriptionPlan.ENTERPRISE,
            ]

            try:
                required_index = plan_hierarchy.index(SubscriptionPlan(required_plan))
                current_index = plan_hierarchy.index(current_plan)

                if current_index < required_index:
                    raise PermissionDenied(
                        detail=f"This feature requires a {required_plan} plan or higher."
                    )
            except (ValueError, KeyError):
                pass

            return view_func(view, request, *args, **kwargs)

        return wrapper

    return decorator
