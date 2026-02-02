# Copyright (c) 2023-present Plane Software, Inc. and contributors
# SPDX-License-Identifier: AGPL-3.0-only
# See the LICENSE file for details.

"""
Lemon Squeezy Webhook Handler.

This module handles webhook events from Lemon Squeezy for:
- Subscription lifecycle events
- Payment events
- Order events
"""

import hashlib
import hmac
import json
import logging

from django.conf import settings
from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from plane.billing.services.subscription_service import SubscriptionService

logger = logging.getLogger(__name__)


# Webhook event types we handle
SUBSCRIPTION_EVENTS = [
    "subscription_created",
    "subscription_updated",
    "subscription_cancelled",
    "subscription_resumed",
    "subscription_expired",
    "subscription_paused",
    "subscription_unpaused",
]

PAYMENT_EVENTS = [
    "subscription_payment_success",
    "subscription_payment_failed",
    "subscription_payment_recovered",
]

ORDER_EVENTS = [
    "order_created",
    "order_refunded",
]


def verify_webhook_signature(payload: bytes, signature: str, secret: str) -> bool:
    """
    Verify the webhook signature from Lemon Squeezy.

    Args:
        payload: The raw request body
        signature: The X-Signature header value
        secret: The webhook secret

    Returns:
        True if the signature is valid
    """
    if not signature or not secret:
        return False

    expected_signature = hmac.new(
        secret.encode("utf-8"),
        payload,
        hashlib.sha256,
    ).hexdigest()

    return hmac.compare_digest(expected_signature, signature)


@method_decorator(csrf_exempt, name="dispatch")
class LemonSqueezyWebhookEndpoint(View):
    """
    Endpoint to handle Lemon Squeezy webhook events.

    POST /api/billing/webhook/
    Headers:
        X-Signature: <hmac_signature>
    Body:
        {
            "meta": {
                "event_name": "subscription_created",
                "custom_data": { ... }
            },
            "data": { ... }
        }
    """

    def post(self, request):
        # Check if billing is enabled
        if not getattr(settings, "ENABLE_LEMON_SQUEEZY", False):
            return JsonResponse(
                {"error": "Billing is not enabled"},
                status=400,
            )

        # Verify webhook signature
        webhook_secret = getattr(settings, "LEMON_SQUEEZY_WEBHOOK_SECRET", None)
        if not webhook_secret:
            logger.error("LEMON_SQUEEZY_WEBHOOK_SECRET not configured")
            return JsonResponse(
                {"error": "Webhook secret not configured"},
                status=500,
            )

        signature = request.META.get("HTTP_X_SIGNATURE", "")
        if not verify_webhook_signature(request.body, signature, webhook_secret):
            logger.warning("Lemon Squeezy webhook signature verification failed")
            return JsonResponse(
                {"error": "Invalid signature"},
                status=401,
            )

        # Parse webhook payload
        try:
            payload = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse(
                {"error": "Invalid JSON body"},
                status=400,
            )

        meta = payload.get("meta", {})
        event_name = meta.get("event_name")
        event_data = payload.get("data", {})

        logger.info(f"Received Lemon Squeezy webhook: {event_name}")

        # Handle the event
        try:
            if event_name in SUBSCRIPTION_EVENTS:
                self._handle_subscription_event(event_name, event_data, meta)
            elif event_name in PAYMENT_EVENTS:
                self._handle_payment_event(event_name, event_data, meta)
            elif event_name in ORDER_EVENTS:
                self._handle_order_event(event_name, event_data, meta)
            else:
                logger.info(f"Unhandled Lemon Squeezy webhook event: {event_name}")

            return JsonResponse({"status": "ok"}, status=200)

        except Exception as e:
            logger.exception(f"Error handling Lemon Squeezy webhook: {e}")
            return JsonResponse(
                {"error": "Failed to process webhook"},
                status=500,
            )

    def _handle_subscription_event(self, event_name: str, event_data: dict, meta: dict):
        """Handle subscription lifecycle events."""
        service = SubscriptionService()

        # Map event names to internal event types
        event_type_map = {
            "subscription_created": "subscription.created",
            "subscription_updated": "subscription.updated",
            "subscription_cancelled": "subscription.cancelled",
            "subscription_resumed": "subscription.resumed",
            "subscription_expired": "subscription.expired",
            "subscription_paused": "subscription.paused",
            "subscription_unpaused": "subscription.unpaused",
        }

        internal_event_type = event_type_map.get(event_name, event_name)

        # Sync subscription from webhook data
        subscription = service.sync_from_webhook(internal_event_type, event_data)

        if subscription:
            logger.info(
                f"Processed {event_name} for subscription {subscription.id}"
            )
        else:
            logger.warning(f"Could not process {event_name}: subscription not found")

    def _handle_payment_event(self, event_name: str, event_data: dict, meta: dict):
        """Handle payment events."""
        service = SubscriptionService()

        # Get subscription ID from event data
        attributes = event_data.get("attributes", {})
        subscription_id = attributes.get("subscription_id")

        if not subscription_id:
            logger.warning(f"Payment event {event_name} missing subscription_id")
            return

        # Map event names
        event_type_map = {
            "subscription_payment_success": "payment.success",
            "subscription_payment_failed": "payment.failed",
            "subscription_payment_recovered": "payment.recovered",
        }

        internal_event_type = event_type_map.get(event_name, event_name)

        # For payment events, we mainly want to log them
        # The subscription status is updated via subscription events
        from plane.billing.models.subscription import Subscription, SubscriptionEvent

        subscription = Subscription.objects.filter(
            lemon_squeezy_subscription_id=str(subscription_id)
        ).first()

        if subscription:
            SubscriptionEvent.objects.create(
                subscription=subscription,
                event_type=internal_event_type,
                event_data=event_data,
            )
            logger.info(f"Logged payment event {event_name} for subscription {subscription.id}")

            # Handle payment failure - update status
            if event_name == "subscription_payment_failed":
                from plane.billing.models.subscription import SubscriptionStatus

                subscription.status = SubscriptionStatus.PAST_DUE
                subscription.save()

    def _handle_order_event(self, event_name: str, event_data: dict, meta: dict):
        """Handle order events."""
        # Order events are typically for one-time purchases
        # For subscriptions, we mainly care about subscription events
        logger.info(f"Received order event: {event_name}")

        # If this is a subscription order, the subscription_created event
        # will handle the actual subscription creation
        pass
