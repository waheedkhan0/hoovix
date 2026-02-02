# Copyright (c) 2023-present Plane Software, Inc. and contributors
# SPDX-License-Identifier: AGPL-3.0-only
# See the LICENSE file for details.

from django.urls import path

from .views import (
    SubscriptionEndpoint,
    CheckoutEndpoint,
    CustomerPortalEndpoint,
    UsageEndpoint,
)
from .views.subscription import PlansEndpoint
from .webhooks import LemonSqueezyWebhookEndpoint

urlpatterns = [
    # Webhook endpoint (no auth required, uses signature verification)
    path("webhook/", LemonSqueezyWebhookEndpoint.as_view(), name="billing-webhook"),

    # Plans endpoint (authenticated, no workspace required)
    path("plans/", PlansEndpoint.as_view(), name="billing-plans"),

    # Workspace-scoped billing endpoints
    path(
        "workspaces/<str:slug>/subscription/",
        SubscriptionEndpoint.as_view(),
        name="workspace-subscription",
    ),
    path(
        "workspaces/<str:slug>/checkout/",
        CheckoutEndpoint.as_view(),
        name="workspace-checkout",
    ),
    path(
        "workspaces/<str:slug>/portal/",
        CustomerPortalEndpoint.as_view(),
        name="workspace-portal",
    ),
    path(
        "workspaces/<str:slug>/usage/",
        UsageEndpoint.as_view(),
        name="workspace-usage",
    ),
]
