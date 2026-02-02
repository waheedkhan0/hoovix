# Copyright (c) 2023-present Plane Software, Inc. and contributors
# SPDX-License-Identifier: AGPL-3.0-only
# See the LICENSE file for details.

"""
Usage Tracking Middleware.

This middleware tracks feature usage for workspaces and enforces
usage limits by adding feature tracking to requests.
"""

import logging
import re
from typing import Callable, Optional

from django.http import HttpRequest, HttpResponse

from plane.billing.services.usage_tracker import UsageTrackerService

logger = logging.getLogger(__name__)


# Define patterns for tracking feature usage
# Format: (http_method, url_pattern, feature_key, amount)
USAGE_TRACKING_PATTERNS = [
    # Projects
    ("POST", r"^/api/workspaces/[\w-]+/projects/$", "projects", 1),
    ("DELETE", r"^/api/workspaces/[\w-]+/projects/[\w-]+/$", "projects", -1),
    # Issues
    ("POST", r"^/api/workspaces/[\w-]+/projects/[\w-]+/issues/$", "issues", 1),
    ("DELETE", r"^/api/workspaces/[\w-]+/projects/[\w-]+/issues/[\w-]+/$", "issues", -1),
    # Views
    ("POST", r"^/api/workspaces/[\w-]+/projects/[\w-]+/views/$", "views", 1),
    # Cycles
    ("POST", r"^/api/workspaces/[\w-]+/projects/[\w-]+/cycles/$", "cycles", 1),
    # Modules
    ("POST", r"^/api/workspaces/[\w-]+/projects/[\w-]+/modules/$", "modules", 1),
    # Pages
    ("POST", r"^/api/workspaces/[\w-]+/projects/[\w-]+/pages/$", "pages", 1),
    ("DELETE", r"^/api/workspaces/[\w-]+/projects/[\w-]+/pages/[\w-]+/$", "pages", -1),
    # Files/Assets
    ("POST", r"^/api/workspaces/[\w-]+/projects/[\w-]+/assets/$", "storage", 1),
    # Workspaces (invites)
    ("POST", r"^/api/workspaces/[\w-]+/invitations/$", "team_members", 1),
    # Webhooks
    ("POST", r"^/api/workspaces/[\w-]+/projects/[\w-]+/webhooks/$", "webhooks", 1),
    # Automations (AI)
    ("POST", r"^/api/workspaces/[\w-]+/projects/[\w-]+/automations/$", "ai_features", 1),
    # Estimates
    ("POST", r"^/api/workspaces/[\w-]+/projects/[\w-]+/estimates/$", "estimates", 1),
]


class UsageTrackingMiddleware:
    """
    Middleware to track feature usage based on API requests.

    This middleware:
    1. Matches incoming requests against usage tracking patterns
    2. Increments/decrements usage counters for the workspace
    3. Can be extended to block requests when limits are exceeded
    """

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]):
        self.get_response = get_response
        self.usage_tracker = UsageTrackerService()
        # Pre-compile regex patterns for performance
        self.compiled_patterns = [
            (method, re.compile(pattern), feature, amount)
            for method, pattern, feature, amount in USAGE_TRACKING_PATTERNS
        ]

    def __call__(self, request: HttpRequest) -> HttpResponse:
        # Process the request first
        response = self.get_response(request)

        # Track usage after successful requests
        if self._should_track(request, response):
            self._track_usage(request)

        return response

    def _should_track(self, request: HttpRequest, response: HttpResponse) -> bool:
        """Check if the request should be tracked."""
        # Only track successful requests (2xx status codes)
        if not 200 <= response.status_code < 300:
            return False

        # Only track POST, PUT, PATCH, DELETE methods
        if request.method not in ("POST", "PUT", "PATCH", "DELETE"):
            return False

        return True

    def _get_workspace_id(self, request: HttpRequest) -> Optional[str]:
        """Extract workspace ID from the request URL or user."""
        # Try to get from URL pattern
        # URL format: /api/workspaces/{workspace_slug}/...
        path_parts = request.path.split("/")

        try:
            workspaces_index = path_parts.index("workspaces")
            if workspaces_index + 1 < len(path_parts):
                return path_parts[workspaces_index + 1]
        except ValueError:
            pass

        # Fallback to request user
        if hasattr(request, "user") and hasattr(request.user, "workspace"):
            return str(request.user.workspace.id) if request.user.workspace else None

        return None

    def _track_usage(self, request: HttpRequest) -> None:
        """Track usage for the matched pattern."""
        workspace_id = self._get_workspace_id(request)

        if not workspace_id:
            logger.debug(f"Could not determine workspace for {request.path}")
            return

        for method, pattern, feature, amount in self.compiled_patterns:
            if pattern.match(request.path) and request.method == method:
                try:
                    self.usage_tracker.track_usage(
                        workspace_id=workspace_id,
                        feature_key=feature,
                        amount=amount,
                    )
                    logger.info(
                        f"Tracked usage: {feature} ({amount:+d}) for workspace {workspace_id}"
                    )
                except Exception as e:
                    logger.error(
                        f"Failed to track usage for {feature}: {e}",
                        exc_info=True,
                    )
                break


class FeatureGateMiddleware:
    """
    Middleware to enforce feature limits on API requests.

    This middleware blocks requests when a workspace has exceeded
    their feature limits.
    """

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]):
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        # Check if the request is for a feature-limited endpoint
        gate_result = self._check_feature_gate(request)

        if gate_result.blocked:
            from rest_framework.response import Response
            from rest_framework import status

            return Response(
                {
                    "error": "Feature limit exceeded",
                    "message": gate_result.reason,
                    "upgrade_url": f"/{request.path.split('/')[2]}/settings/billing",
                },
                status=status.HTTP_402_PAYMENT_REQUIRED,
            )

        return self.get_response(request)

    def _check_feature_gate(self, request: HttpRequest) -> "GateResult":
        """Check if the request should be blocked by feature gate."""
        from dataclasses import dataclass

        @dataclass
        class GateResult:
            blocked: bool = False
            reason: str = ""

        # Skip for non-workspace API endpoints
        if "/workspaces/" not in request.path:
            return GateResult()

        # Skip for billing endpoints (prevent circular dependency)
        if "/billing/" in request.path or "/subscriptions/" in request.path:
            return GateResult()

        # Skip for read-only operations
        if request.method in ("GET", "HEAD", "OPTIONS"):
            return GateResult()

        # Get workspace
        workspace_id = self._extract_workspace_id(request)

        if not workspace_id:
            return GateResult()

        # Check feature limits
        from plane.billing.permissions.feature_registry import FeatureChecker

        checker = FeatureChecker(workspace_id)

        for method, pattern, feature, amount in USAGE_TRACKING_PATTERNS:
            if pattern.match(request.path) and request.method == method:
                if amount > 0:  # Only check for creation/addition
                    can_use, reason = checker.can_use(feature, amount)
                    if not can_use:
                        return GateResult(blocked=True, reason=reason)
                break

        return GateResult()

    def _extract_workspace_id(self, request: HttpRequest) -> Optional[str]:
        """Extract workspace ID from the request."""
        path_parts = request.path.split("/")

        try:
            workspaces_index = path_parts.index("workspaces")
            if workspaces_index + 1 < len(path_parts):
                return path_parts[workspaces_index + 1]
        except ValueError:
            pass

        return None
