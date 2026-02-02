# Copyright (c) 2023-present Plane Software, Inc. and contributors
# SPDX-License-Identifier: AGPL-3.0-only
# See the LICENSE file for details.

"""
Billing API Views.

These views provide REST API endpoints for:
- Subscription management
- Checkout creation
- Customer portal access
- Usage tracking
"""

import json
import logging

from django.conf import settings
from django.http import JsonResponse
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from plane.app.permissions import WorkspaceEntityPermission
from plane.billing.services.subscription_service import SubscriptionService
from plane.billing.services.usage_tracker import UsageTracker
from plane.billing.services.lemon_squeezy import LemonSqueezyError
from plane.db.models import Workspace

logger = logging.getLogger(__name__)


class SubscriptionEndpoint(APIView):
    """
    API endpoint for subscription management.

    GET /api/v1/workspaces/:slug/billing/subscription/
        Get subscription details for a workspace

    DELETE /api/v1/workspaces/:slug/billing/subscription/
        Cancel the subscription
    """

    permission_classes = [IsAuthenticated, WorkspaceEntityPermission]

    def get(self, request, slug):
        """Get subscription details for a workspace."""
        try:
            workspace = Workspace.objects.get(slug=slug)
        except Workspace.DoesNotExist:
            return Response(
                {"error": "Workspace not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        service = SubscriptionService()
        subscription_details = service.get_subscription_details(workspace)

        return Response(subscription_details, status=status.HTTP_200_OK)

    def delete(self, request, slug):
        """Cancel the subscription."""
        try:
            workspace = Workspace.objects.get(slug=slug)
        except Workspace.DoesNotExist:
            return Response(
                {"error": "Workspace not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Check if user is workspace admin
        if not workspace.workspace_members.filter(
            member=request.user,
            role__gte=15,  # Admin or Owner
        ).exists():
            return Response(
                {"error": "Only workspace admins can cancel subscriptions"},
                status=status.HTTP_403_FORBIDDEN,
            )

        at_period_end = request.data.get("at_period_end", True)

        try:
            service = SubscriptionService()
            subscription = service.cancel_subscription(workspace, at_period_end)

            return Response(
                {
                    "message": "Subscription cancelled successfully",
                    "subscription": service.get_subscription_details(workspace),
                },
                status=status.HTTP_200_OK,
            )
        except ValueError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except LemonSqueezyError as e:
            logger.error(f"Failed to cancel subscription: {e}")
            return Response(
                {"error": "Failed to cancel subscription"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class CheckoutEndpoint(APIView):
    """
    API endpoint for creating checkout sessions.

    POST /api/v1/workspaces/:slug/billing/checkout/
        Create a checkout session for upgrading
    """

    permission_classes = [IsAuthenticated, WorkspaceEntityPermission]

    def post(self, request, slug):
        """Create a checkout session."""
        try:
            workspace = Workspace.objects.get(slug=slug)
        except Workspace.DoesNotExist:
            return Response(
                {"error": "Workspace not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Check if user is workspace admin
        if not workspace.workspace_members.filter(
            member=request.user,
            role__gte=15,  # Admin or Owner
        ).exists():
            return Response(
                {"error": "Only workspace admins can manage billing"},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Get checkout parameters
        plan = request.data.get("plan")
        billing_interval = request.data.get("billing_interval", "month")
        success_url = request.data.get("success_url")
        cancel_url = request.data.get("cancel_url")

        if not plan:
            return Response(
                {"error": "Plan is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            service = SubscriptionService()
            checkout = service.create_checkout(
                workspace=workspace,
                user=request.user,
                plan=plan,
                billing_interval=billing_interval,
                success_url=success_url,
                cancel_url=cancel_url,
            )

            return Response(
                {
                    "checkout_url": checkout.checkout_url,
                    "checkout_id": checkout.checkout_id,
                },
                status=status.HTTP_200_OK,
            )
        except ValueError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except LemonSqueezyError as e:
            logger.error(f"Failed to create checkout: {e}")
            return Response(
                {"error": "Failed to create checkout session"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class CustomerPortalEndpoint(APIView):
    """
    API endpoint for customer portal access.

    POST /api/v1/workspaces/:slug/billing/portal/
        Get the customer portal URL
    """

    permission_classes = [IsAuthenticated, WorkspaceEntityPermission]

    def post(self, request, slug):
        """Get the customer portal URL."""
        try:
            workspace = Workspace.objects.get(slug=slug)
        except Workspace.DoesNotExist:
            return Response(
                {"error": "Workspace not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Check if user is workspace admin
        if not workspace.workspace_members.filter(
            member=request.user,
            role__gte=15,  # Admin or Owner
        ).exists():
            return Response(
                {"error": "Only workspace admins can access billing portal"},
                status=status.HTTP_403_FORBIDDEN,
            )

        service = SubscriptionService()
        portal_url = service.get_customer_portal_url(workspace)

        if not portal_url:
            return Response(
                {"error": "No active subscription found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(
            {"portal_url": portal_url},
            status=status.HTTP_200_OK,
        )


class UsageEndpoint(APIView):
    """
    API endpoint for usage tracking.

    GET /api/v1/workspaces/:slug/billing/usage/
        Get usage information for all features
    """

    permission_classes = [IsAuthenticated, WorkspaceEntityPermission]

    def get(self, request, slug):
        """Get usage information for a workspace."""
        try:
            workspace = Workspace.objects.get(slug=slug)
        except Workspace.DoesNotExist:
            return Response(
                {"error": "Workspace not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        tracker = UsageTracker(workspace)
        usage = tracker.get_all_usage()

        return Response(
            {
                "plan": tracker.plan,
                "usage": usage,
            },
            status=status.HTTP_200_OK,
        )


class PlansEndpoint(APIView):
    """
    API endpoint for getting available plans.

    GET /api/v1/billing/plans/
        Get all available subscription plans
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Get available subscription plans."""
        from plane.billing.services.usage_tracker import PLAN_LIMITS
        from plane.billing.models.subscription import SubscriptionPlan

        plans = []

        # Plan pricing (these would typically come from Lemon Squeezy)
        plan_pricing = {
            SubscriptionPlan.FREE: {
                "monthly": 0,
                "yearly": 0,
            },
            SubscriptionPlan.STARTER: {
                "monthly": 10,
                "yearly": 100,
            },
            SubscriptionPlan.PRO: {
                "monthly": 25,
                "yearly": 250,
            },
            SubscriptionPlan.ENTERPRISE: {
                "monthly": 100,
                "yearly": 1000,
            },
        }

        for plan_key, limits in PLAN_LIMITS.items():
            pricing = plan_pricing.get(plan_key, {"monthly": 0, "yearly": 0})

            plans.append({
                "key": plan_key,
                "name": plan_key.replace("_", " ").title(),
                "limits": limits,
                "pricing": {
                    "monthly": pricing["monthly"],
                    "yearly": pricing["yearly"],
                    "yearly_savings": (pricing["monthly"] * 12) - pricing["yearly"],
                },
            })

        return Response({"plans": plans}, status=status.HTTP_200_OK)
