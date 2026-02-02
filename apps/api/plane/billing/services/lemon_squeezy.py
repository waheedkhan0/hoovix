# Copyright (c) 2023-present Plane Software, Inc. and contributors
# SPDX-License-Identifier: AGPL-3.0-only
# See the LICENSE file for details.

"""
Lemon Squeezy API Client.

This module provides a client for interacting with the Lemon Squeezy API
for subscription management, checkout creation, and customer portal access.
"""

import logging
from dataclasses import dataclass
from typing import Any, Optional

import requests
from django.conf import settings

logger = logging.getLogger(__name__)

LEMON_SQUEEZY_API_URL = "https://api.lemonsqueezy.com/v1"


@dataclass
class CheckoutOptions:
    """Options for creating a checkout session."""

    variant_id: str
    workspace_id: str
    user_email: str
    user_name: Optional[str] = None
    custom_data: Optional[dict] = None
    success_url: Optional[str] = None
    cancel_url: Optional[str] = None


@dataclass
class CheckoutResponse:
    """Response from creating a checkout session."""

    checkout_url: str
    checkout_id: str


class LemonSqueezyError(Exception):
    """Exception raised for Lemon Squeezy API errors."""

    def __init__(self, message: str, status_code: Optional[int] = None, response: Optional[dict] = None):
        super().__init__(message)
        self.status_code = status_code
        self.response = response


class LemonSqueezyClient:
    """
    Client for interacting with the Lemon Squeezy API.

    Usage:
        client = LemonSqueezyClient()
        checkout = client.create_checkout(CheckoutOptions(...))
    """

    def __init__(self, api_key: Optional[str] = None, store_id: Optional[str] = None):
        self.api_key = api_key or getattr(settings, "LEMON_SQUEEZY_API_KEY", None)
        self.store_id = store_id or getattr(settings, "LEMON_SQUEEZY_STORE_ID", None)

        if not self.api_key:
            raise LemonSqueezyError("LEMON_SQUEEZY_API_KEY is not configured")

    def _get_headers(self) -> dict:
        """Get the headers for API requests."""
        return {
            "Accept": "application/vnd.api+json",
            "Content-Type": "application/vnd.api+json",
            "Authorization": f"Bearer {self.api_key}",
        }

    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[dict] = None,
        params: Optional[dict] = None,
    ) -> dict:
        """Make a request to the Lemon Squeezy API."""
        url = f"{LEMON_SQUEEZY_API_URL}/{endpoint}"

        try:
            response = requests.request(
                method=method,
                url=url,
                headers=self._get_headers(),
                json=data,
                params=params,
                timeout=30,
            )

            if response.status_code >= 400:
                error_data = response.json() if response.content else {}
                raise LemonSqueezyError(
                    f"API request failed: {response.status_code}",
                    status_code=response.status_code,
                    response=error_data,
                )

            return response.json() if response.content else {}

        except requests.RequestException as e:
            logger.exception(f"Lemon Squeezy API request failed: {e}")
            raise LemonSqueezyError(f"API request failed: {str(e)}")

    def create_checkout(self, options: CheckoutOptions) -> CheckoutResponse:
        """
        Create a checkout session for a subscription.

        Args:
            options: Checkout options including variant ID and customer info

        Returns:
            CheckoutResponse with the checkout URL
        """
        custom_data = options.custom_data or {}
        custom_data["workspace_id"] = options.workspace_id

        checkout_data = {
            "data": {
                "type": "checkouts",
                "attributes": {
                    "checkout_data": {
                        "email": options.user_email,
                        "name": options.user_name,
                        "custom": custom_data,
                    },
                    "checkout_options": {
                        "embed": False,
                        "media": True,
                        "logo": True,
                        "desc": True,
                        "discount": True,
                        "dark": False,
                        "subscription_preview": True,
                    },
                    "product_options": {
                        "enabled_variants": [int(options.variant_id)],
                        "redirect_url": options.success_url,
                    },
                },
                "relationships": {
                    "store": {
                        "data": {
                            "type": "stores",
                            "id": self.store_id,
                        }
                    },
                    "variant": {
                        "data": {
                            "type": "variants",
                            "id": options.variant_id,
                        }
                    },
                },
            }
        }

        response = self._make_request("POST", "checkouts", data=checkout_data)

        checkout_url = response["data"]["attributes"]["url"]
        checkout_id = response["data"]["id"]

        return CheckoutResponse(checkout_url=checkout_url, checkout_id=checkout_id)

    def get_subscription(self, subscription_id: str) -> dict:
        """
        Get subscription details.

        Args:
            subscription_id: The Lemon Squeezy subscription ID

        Returns:
            Subscription data from the API
        """
        response = self._make_request("GET", f"subscriptions/{subscription_id}")
        return response["data"]

    def cancel_subscription(self, subscription_id: str) -> dict:
        """
        Cancel a subscription.

        Args:
            subscription_id: The Lemon Squeezy subscription ID

        Returns:
            Updated subscription data
        """
        response = self._make_request("DELETE", f"subscriptions/{subscription_id}")
        return response["data"]

    def resume_subscription(self, subscription_id: str) -> dict:
        """
        Resume a cancelled subscription.

        Args:
            subscription_id: The Lemon Squeezy subscription ID

        Returns:
            Updated subscription data
        """
        data = {
            "data": {
                "type": "subscriptions",
                "id": subscription_id,
                "attributes": {
                    "cancelled": False,
                },
            }
        }
        response = self._make_request("PATCH", f"subscriptions/{subscription_id}", data=data)
        return response["data"]

    def update_subscription(self, subscription_id: str, variant_id: str) -> dict:
        """
        Update a subscription to a different plan/variant.

        Args:
            subscription_id: The Lemon Squeezy subscription ID
            variant_id: The new variant ID to switch to

        Returns:
            Updated subscription data
        """
        data = {
            "data": {
                "type": "subscriptions",
                "id": subscription_id,
                "attributes": {
                    "variant_id": int(variant_id),
                },
            }
        }
        response = self._make_request("PATCH", f"subscriptions/{subscription_id}", data=data)
        return response["data"]

    def pause_subscription(self, subscription_id: str, mode: str = "void") -> dict:
        """
        Pause a subscription.

        Args:
            subscription_id: The Lemon Squeezy subscription ID
            mode: Pause mode - "void" or "free"

        Returns:
            Updated subscription data
        """
        data = {
            "data": {
                "type": "subscriptions",
                "id": subscription_id,
                "attributes": {
                    "pause": {
                        "mode": mode,
                    },
                },
            }
        }
        response = self._make_request("PATCH", f"subscriptions/{subscription_id}", data=data)
        return response["data"]

    def unpause_subscription(self, subscription_id: str) -> dict:
        """
        Unpause a subscription.

        Args:
            subscription_id: The Lemon Squeezy subscription ID

        Returns:
            Updated subscription data
        """
        data = {
            "data": {
                "type": "subscriptions",
                "id": subscription_id,
                "attributes": {
                    "pause": None,
                },
            }
        }
        response = self._make_request("PATCH", f"subscriptions/{subscription_id}", data=data)
        return response["data"]

    def get_customer(self, customer_id: str) -> dict:
        """
        Get customer details.

        Args:
            customer_id: The Lemon Squeezy customer ID

        Returns:
            Customer data from the API
        """
        response = self._make_request("GET", f"customers/{customer_id}")
        return response["data"]

    def get_customer_portal_url(self, customer_id: str) -> str:
        """
        Get the customer portal URL for managing subscriptions.

        Args:
            customer_id: The Lemon Squeezy customer ID

        Returns:
            URL to the customer portal
        """
        customer = self.get_customer(customer_id)
        return customer["attributes"]["urls"]["customer_portal"]

    def get_subscription_invoices(self, subscription_id: str) -> list:
        """
        Get invoices for a subscription.

        Args:
            subscription_id: The Lemon Squeezy subscription ID

        Returns:
            List of invoice data
        """
        response = self._make_request(
            "GET",
            "subscription-invoices",
            params={"filter[subscription_id]": subscription_id},
        )
        return response.get("data", [])

    def get_products(self) -> list:
        """
        Get all products for the store.

        Returns:
            List of product data
        """
        response = self._make_request(
            "GET",
            "products",
            params={"filter[store_id]": self.store_id},
        )
        return response.get("data", [])

    def get_variants(self, product_id: Optional[str] = None) -> list:
        """
        Get variants (pricing options) for products.

        Args:
            product_id: Optional product ID to filter by

        Returns:
            List of variant data
        """
        params = {}
        if product_id:
            params["filter[product_id]"] = product_id

        response = self._make_request("GET", "variants", params=params)
        return response.get("data", [])
