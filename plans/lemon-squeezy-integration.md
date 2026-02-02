# Lemon Squeezy Payment Integration Architecture

## Overview

This document outlines the comprehensive architecture for integrating Lemon Squeezy as the payment processor for Hoovix. Lemon Squeezy will handle subscription management, billing, and payment processing for the SaaS transformation.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              Hoovix Platform                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐                   │
│  │   Web App    │    │   Admin      │    │   API        │                   │
│  │   (React)    │◄──►│   Panel      │◄──►│   (Python)   │                   │
│  └──────┬───────┘    └──────┬───────┘    └──────┬───────┘                   │
│         │                   │                   │                           │
│         │                   │                   │                           │
│         ▼                   ▼                   ▼                           │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    Subscription Service Layer                        │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌────────────┐ │   │
│  │  │   Plans     │  │  Checkout   │  │   Portal    │  │   Usage    │ │   │
│  │  │   Config    │  │   Service   │  │   Service   │  │  Tracking  │ │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └────────────┘ │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│         │                                                                   │
│         │                                                                   │
│         ▼                                                                   │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    Webhook Handler Layer                             │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌────────────┐ │   │
│  │  │subscription_│  │subscription_│  │subscription_│  │  payment_  │ │   │
│  │  │  created    │  │  updated    │  │  cancelled  │  │  success   │ │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └────────────┘ │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│         │                                                                   │
└─────────┼───────────────────────────────────────────────────────────────────┘
          │
          │ HTTPS Webhooks
          ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                            Lemon Squeezy                                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Products   │  │   Checkout   │  │  Customer    │  │   Billing    │     │
│  │   & Plans    │  │   Sessions   │  │   Portal     │  │   Engine     │     │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Lemon Squeezy Configuration

### Store Setup

1. **Create Store**: Set up a Lemon Squeezy store for Hoovix
2. **Products**: Create products for each subscription tier
3. **Variants**: Define pricing variants for monthly/annual billing
4. **Webhooks**: Configure webhook endpoints for event notifications

### Product Structure

```
Hoovix
├── Product: Free Plan
│   └── Variant: Free (Price: $0)
│
├── Product: Starter Plan
│   ├── Variant: Monthly (Price: $12/user/month)
│   └── Variant: Annual (Price: $10/user/month, billed annually)
│
├── Product: Pro Plan
│   ├── Variant: Monthly (Price: $24/user/month)
│   └── Variant: Annual (Price: $20/user/month, billed annually)
│
└── Product: Enterprise Plan
    └── Variant: Custom (Contact sales)
```

## Database Schema

### Subscription Models

Add to [`apps/api/plane/db/models/subscription.py`](apps/api/plane/db/models/subscription.py:1):

```python
# Copyright (c) 2023-present Plane Software, Inc. and contributors
# SPDX-License-Identifier: AGPL-3.0-only

import uuid
from django.db import models
from django.contrib.auth import get_user_model

from plane.db.mixins import TimeAuditModel

User = get_user_model()


class SubscriptionStatus(models.TextChoices):
    ACTIVE = "active", "Active"
    CANCELLED = "cancelled", "Cancelled"
    PAST_DUE = "past_due", "Past Due"
    UNPAID = "unpaid", "Unpaid"
    PAUSED = "paused", "Paused"
    EXPIRED = "expired", "Expired"
    TRIALING = "trialing", "Trialing"


class PlanTier(models.TextChoices):
    FREE = "free", "Free"
    STARTER = "starter", "Starter"
    PRO = "pro", "Pro"
    ENTERPRISE = "enterprise", "Enterprise"


class Subscription(TimeAuditModel):
    """
    Stores subscription information synced from Lemon Squeezy.
    """
    id = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False,
        db_index=True,
        primary_key=True
    )
    
    # Lemon Squeezy IDs
    lemon_squeezy_id = models.CharField(
        max_length=255,
        unique=True,
        db_index=True,
        help_text="Lemon Squeezy subscription ID"
    )
    lemon_squeezy_customer_id = models.CharField(
        max_length=255,
        db_index=True,
        help_text="Lemon Squeezy customer ID"
    )
    lemon_squeezy_order_id = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="Lemon Squeezy order ID"
    )
    lemon_squeezy_product_id = models.CharField(
        max_length=255,
        help_text="Lemon Squeezy product ID"
    )
    lemon_squeezy_variant_id = models.CharField(
        max_length=255,
        help_text="Lemon Squeezy variant ID"
    )
    
    # Workspace relationship
    workspace = models.ForeignKey(
        "db.Workspace",
        on_delete=models.CASCADE,
        related_name="subscriptions",
        help_text="Workspace this subscription belongs to"
    )
    
    # Subscription details
    status = models.CharField(
        max_length=50,
        choices=SubscriptionStatus.choices,
        default=SubscriptionStatus.TRIALING,
        db_index=True
    )
    plan_tier = models.CharField(
        max_length=50,
        choices=PlanTier.choices,
        default=PlanTier.FREE,
        db_index=True
    )
    billing_interval = models.CharField(
        max_length=20,
        choices=[
            ("month", "Monthly"),
            ("year", "Yearly"),
            ("lifetime", "Lifetime"),
        ],
        default="month"
    )
    
    # Pricing
    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )
    quantity = models.PositiveIntegerField(default=1)
    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )
    currency = models.CharField(max_length=3, default="USD")
    
    # Trial
    is_trial = models.BooleanField(default=False)
    trial_ends_at = models.DateTimeField(null=True, blank=True)
    
    # Billing periods
    current_period_start = models.DateTimeField(null=True, blank=True)
    current_period_end = models.DateTimeField(null=True, blank=True)
    
    # Cancellation
    cancel_at_period_end = models.BooleanField(default=False)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    
    # URLs
    update_payment_method_url = models.URLField(null=True, blank=True)
    customer_portal_url = models.URLField(null=True, blank=True)
    
    # Metadata
    metadata = models.JSONField(default=dict, blank=True)
    
    class Meta:
        db_table = "subscriptions"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["workspace", "status"]),
            models.Index(fields=["lemon_squeezy_customer_id"]),
            models.Index(fields=["plan_tier", "status"]),
        ]
    
    def __str__(self):
        return f"{self.workspace.name} - {self.plan_tier} ({self.status})"
    
    @property
    def is_active(self):
        return self.status in [
            SubscriptionStatus.ACTIVE,
            SubscriptionStatus.TRIALING
        ]
    
    @property
    def is_paid_plan(self):
        return self.plan_tier != PlanTier.FREE


class SubscriptionEvent(TimeAuditModel):
    """
    Audit log for subscription events from Lemon Squeezy webhooks.
    """
    id = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False,
        db_index=True,
        primary_key=True
    )
    
    subscription = models.ForeignKey(
        Subscription,
        on_delete=models.CASCADE,
        related_name="events",
        null=True,
        blank=True
    )
    
    event_type = models.CharField(max_length=100, db_index=True)
    lemon_squeezy_event_id = models.CharField(
        max_length=255,
        unique=True,
        help_text="Lemon Squeezy webhook event ID"
    )
    
    payload = models.JSONField()
    processed = models.BooleanField(default=False)
    error_message = models.TextField(null=True, blank=True)
    
    class Meta:
        db_table = "subscription_events"
        ordering = ["-created_at"]
    
    def __str__(self):
        return f"{self.event_type} - {self.created_at}"


class FeatureUsage(TimeAuditModel):
    """
    Track feature usage for metered billing and limits.
    """
    id = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False,
        db_index=True,
        primary_key=True
    )
    
    workspace = models.ForeignKey(
        "db.Workspace",
        on_delete=models.CASCADE,
        related_name="feature_usage"
    )
    
    feature_name = models.CharField(max_length=100, db_index=True)
    usage_count = models.PositiveIntegerField(default=0)
    usage_date = models.DateField(db_index=True)
    
    # Additional metadata
    metadata = models.JSONField(default=dict, blank=True)
    
    class Meta:
        db_table = "feature_usage"
        unique_together = ["workspace", "feature_name", "usage_date"]
        indexes = [
            models.Index(fields=["workspace", "feature_name", "-usage_date"]),
        ]
    
    def __str__(self):
        return f"{self.workspace.name} - {self.feature_name} ({self.usage_date})"


class Invoice(TimeAuditModel):
    """
    Store invoice information from Lemon Squeezy.
    """
    id = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False,
        db_index=True,
        primary_key=True
    )
    
    subscription = models.ForeignKey(
        Subscription,
        on_delete=models.CASCADE,
        related_name="invoices"
    )
    
    lemon_squeezy_invoice_id = models.CharField(
        max_length=255,
        unique=True
    )
    
    invoice_number = models.CharField(max_length=100)
    status = models.CharField(max_length=50)
    
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3)
    
    invoiced_at = models.DateTimeField()
    due_at = models.DateTimeField()
    paid_at = models.DateTimeField(null=True, blank=True)
    
    pdf_url = models.URLField(null=True, blank=True)
    
    class Meta:
        db_table = "invoices"
        ordering = ["-invoiced_at"]
    
    def __str__(self):
        return f"{self.invoice_number} - {self.amount} {self.currency}"
```

### Migration

Create migration [`apps/api/plane/db/migrations/0119_add_subscription_models.py`](apps/api/plane/db/migrations/0119_add_subscription_models.py:1):

```python
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):
    dependencies = [
        ("db", "0118_workspaceuserproperties_navigation_control_preference_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="Subscription",
            fields=[
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "id",
                    models.UUIDField(
                        db_index=True,
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                        unique=True,
                    ),
                ),
                ("lemon_squeezy_id", models.CharField(db_index=True, max_length=255, unique=True)),
                ("lemon_squeezy_customer_id", models.CharField(db_index=True, max_length=255)),
                ("lemon_squeezy_order_id", models.CharField(blank=True, max_length=255, null=True)),
                ("lemon_squeezy_product_id", models.CharField(max_length=255)),
                ("lemon_squeezy_variant_id", models.CharField(max_length=255)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("active", "Active"),
                            ("cancelled", "Cancelled"),
                            ("past_due", "Past Due"),
                            ("unpaid", "Unpaid"),
                            ("paused", "Paused"),
                            ("expired", "Expired"),
                            ("trialing", "Trialing"),
                        ],
                        db_index=True,
                        default="trialing",
                        max_length=50,
                    ),
                ),
                (
                    "plan_tier",
                    models.CharField(
                        choices=[
                            ("free", "Free"),
                            ("starter", "Starter"),
                            ("pro", "Pro"),
                            ("enterprise", "Enterprise"),
                        ],
                        db_index=True,
                        default="free",
                        max_length=50,
                    ),
                ),
                (
                    "billing_interval",
                    models.CharField(
                        choices=[
                            ("month", "Monthly"),
                            ("year", "Yearly"),
                            ("lifetime", "Lifetime"),
                        ],
                        default="month",
                        max_length=20,
                    ),
                ),
                ("unit_price", models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ("quantity", models.PositiveIntegerField(default=1)),
                ("total_price", models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ("currency", models.CharField(default="USD", max_length=3)),
                ("is_trial", models.BooleanField(default=False)),
                ("trial_ends_at", models.DateTimeField(blank=True, null=True)),
                ("current_period_start", models.DateTimeField(blank=True, null=True)),
                ("current_period_end", models.DateTimeField(blank=True, null=True)),
                ("cancel_at_period_end", models.BooleanField(default=False)),
                ("cancelled_at", models.DateTimeField(blank=True, null=True)),
                ("update_payment_method_url", models.URLField(blank=True, null=True)),
                ("customer_portal_url", models.URLField(blank=True, null=True)),
                ("metadata", models.JSONField(blank=True, default=dict)),
                (
                    "workspace",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="subscriptions",
                        to="db.workspace",
                    ),
                ),
            ],
            options={
                "db_table": "subscriptions",
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="SubscriptionEvent",
            fields=[
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "id",
                    models.UUIDField(
                        db_index=True,
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                        unique=True,
                    ),
                ),
                ("event_type", models.CharField(db_index=True, max_length=100)),
                ("lemon_squeezy_event_id", models.CharField(max_length=255, unique=True)),
                ("payload", models.JSONField()),
                ("processed", models.BooleanField(default=False)),
                ("error_message", models.TextField(blank=True, null=True)),
                (
                    "subscription",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="events",
                        to="db.subscription",
                    ),
                ),
            ],
            options={
                "db_table": "subscription_events",
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="Invoice",
            fields=[
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "id",
                    models.UUIDField(
                        db_index=True,
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                        unique=True,
                    ),
                ),
                ("lemon_squeezy_invoice_id", models.CharField(max_length=255, unique=True)),
                ("invoice_number", models.CharField(max_length=100)),
                ("status", models.CharField(max_length=50)),
                ("amount", models.DecimalField(decimal_places=2, max_digits=10)),
                ("currency", models.CharField(max_length=3)),
                ("invoiced_at", models.DateTimeField()),
                ("due_at", models.DateTimeField()),
                ("paid_at", models.DateTimeField(blank=True, null=True)),
                ("pdf_url", models.URLField(blank=True, null=True)),
                (
                    "subscription",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="invoices",
                        to="db.subscription",
                    ),
                ),
            ],
            options={
                "db_table": "invoices",
                "ordering": ["-invoiced_at"],
            },
        ),
        migrations.CreateModel(
            name="FeatureUsage",
            fields=[
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "id",
                    models.UUIDField(
                        db_index=True,
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                        unique=True,
                    ),
                ),
                ("feature_name", models.CharField(db_index=True, max_length=100)),
                ("usage_count", models.PositiveIntegerField(default=0)),
                ("usage_date", models.DateField(db_index=True)),
                ("metadata", models.JSONField(blank=True, default=dict)),
                (
                    "workspace",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="feature_usage",
                        to="db.workspace",
                    ),
                ),
            ],
            options={
                "db_table": "feature_usage",
                "unique_together": {("workspace", "feature_name", "usage_date")},
            },
        ),
    ]
```

## Backend Implementation

### Lemon Squeezy Service

Create [`apps/api/plane/billing/services/lemon_squeezy.py`](apps/api/plane/billing/services/lemon_squeezy.py:1):

```python
# Copyright (c) 2023-present Plane Software, Inc. and contributors
# SPDX-License-Identifier: AGPL-3.0-only

import os
import requests
from typing import Optional, Dict, Any
from django.conf import settings


class LemonSqueezyAPI:
    """
    Client for Lemon Squeezy API.
    """
    BASE_URL = "https://api.lemonsqueezy.com/v1"
    
    def __init__(self):
        self.api_key = settings.LEMON_SQUEEZY_API_KEY
        self.headers = {
            "Accept": "application/vnd.api+json",
            "Content-Type": "application/vnd.api+json",
            "Authorization": f"Bearer {self.api_key}",
        }
    
    def _request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict:
        """Make authenticated request to Lemon Squeezy API."""
        url = f"{self.BASE_URL}/{endpoint}"
        
        response = requests.request(
            method=method,
            url=url,
            headers=self.headers,
            json=data,
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    
    def create_checkout(self, 
                       variant_id: str,
                       email: str,
                       workspace_id: str,
                       user_id: str,
                       custom_price: Optional[int] = None) -> Dict:
        """
        Create a checkout session for subscription.
        
        Args:
            variant_id: Lemon Squeezy variant ID
            email: Customer email
            workspace_id: Hoovix workspace ID
            user_id: Hoovix user ID
            custom_price: Optional custom price in cents
        """
        data = {
            "data": {
                "type": "checkouts",
                "attributes": {
                    "checkout_data": {
                        "email": email,
                        "custom": {
                            "workspace_id": str(workspace_id),
                            "user_id": str(user_id),
                        }
                    },
                    **({"custom_price": custom_price} if custom_price else {})
                },
                "relationships": {
                    "store": {
                        "data": {
                            "type": "stores",
                            "id": settings.LEMON_SQUEEZY_STORE_ID
                        }
                    },
                    "variant": {
                        "data": {
                            "type": "variants",
                            "id": variant_id
                        }
                    }
                }
            }
        }
        
        return self._request("POST", "checkouts", data)
    
    def get_subscription(self, subscription_id: str) -> Dict:
        """Get subscription details from Lemon Squeezy."""
        return self._request("GET", f"subscriptions/{subscription_id}")
    
    def update_subscription(self, subscription_id: str, data: Dict) -> Dict:
        """Update subscription in Lemon Squeezy."""
        payload = {
            "data": {
                "type": "subscriptions",
                "id": subscription_id,
                "attributes": data
            }
        }
        return self._request("PATCH", f"subscriptions/{subscription_id}", payload)
    
    def cancel_subscription(self, subscription_id: str) -> Dict:
        """Cancel a subscription."""
        return self._request("DELETE", f"subscriptions/{subscription_id}")
    
    def get_customer_portal_url(self, customer_id: str) -> str:
        """Get customer portal URL."""
        result = self._request("GET", f"customers/{customer_id}")
        return result.get("data", {}).get("attributes", {}).get("urls", {}).get("customer_portal", "")
    
    def get_invoices(self, customer_id: str) -> list:
        """Get invoices for a customer."""
        result = self._request("GET", f"invoices?filter[customer_id]={customer_id}")
        return result.get("data", [])


lemon_squeezy = LemonSqueezyAPI()
```

### Webhook Handlers

Create [`apps/api/plane/billing/webhooks/lemon_squeezy.py`](apps/api/plane/billing/webhooks/lemon_squeezy.py:1):

```python
# Copyright (c) 2023-present Plane Software, Inc. and contributors
# SPDX-License-Identifier: AGPL-3.0-only

import hashlib
import hmac
import json
import logging
from datetime import datetime
from typing import Dict, Any

from django.conf import settings
from django.db import transaction

from plane.db.models import Subscription, SubscriptionEvent, Invoice, PlanTier
from plane.db.models.subscription import SubscriptionStatus
from plane.db.models.workspace import Workspace

logger = logging.getLogger(__name__)


class LemonSqueezyWebhookHandler:
    """
    Handle Lemon Squeezy webhook events.
    """
    
    def __init__(self):
        self.secret = settings.LEMON_SQUEEZY_WEBHOOK_SECRET
    
    def verify_signature(self, payload: bytes, signature: str) -> bool:
        """Verify webhook signature."""
        expected_signature = hmac.new(
            self.secret.encode(),
            payload,
            hashlib.sha256
        ).hexdigest()
        return hmac.compare_digest(signature, expected_signature)
    
    def handle_event(self, event_type: str, payload: Dict[str, Any]) -> None:
        """Route event to appropriate handler."""
        handlers = {
            "subscription_created": self._handle_subscription_created,
            "subscription_updated": self._handle_subscription_updated,
            "subscription_cancelled": self._handle_subscription_cancelled,
            "subscription_expired": self._handle_subscription_expired,
            "subscription_paused": self._handle_subscription_paused,
            "subscription_resumed": self._handle_subscription_resumed,
            "subscription_payment_success": self._handle_payment_success,
            "subscription_payment_failed": self._handle_payment_failed,
            "subscription_payment_recovered": self._handle_payment_recovered,
            "order_created": self._handle_order_created,
            "license_key_created": self._handle_license_key_created,
        }
        
        handler = handlers.get(event_type)
        if handler:
            try:
                with transaction.atomic():
                    handler(payload)
            except Exception as e:
                logger.error(f"Error handling {event_type}: {e}")
                raise
        else:
            logger.warning(f"Unhandled event type: {event_type}")
    
    def _handle_subscription_created(self, payload: Dict) -> None:
        """Handle subscription_created event."""
        data = payload.get("data", {})
        attributes = data.get("attributes", {})
        relationships = data.get("relationships", {})
        
        # Extract IDs
        subscription_id = data.get("id")
        customer_id = relationships.get("customer", {}).get("data", {}).get("id")
        variant_id = relationships.get("variant", {}).get("data", {}).get("id")
        product_id = relationships.get("product", {}).get("data", {}).get("id")
        order_id = relationships.get("order", {}).get("data", {}).get("id")
        
        # Get custom data
        custom_data = attributes.get("checkout_data", {}).get("custom", {})
        workspace_id = custom_data.get("workspace_id")
        
        if not workspace_id:
            logger.error(f"No workspace_id in subscription {subscription_id}")
            return
        
        try:
            workspace = Workspace.objects.get(id=workspace_id)
        except Workspace.DoesNotExist:
            logger.error(f"Workspace {workspace_id} not found")
            return
        
        # Determine plan tier from variant
        plan_tier = self._get_plan_tier_from_variant(variant_id)
        
        # Create subscription
        subscription, created = Subscription.objects.update_or_create(
            lemon_squeezy_id=subscription_id,
            defaults={
                "workspace": workspace,
                "lemon_squeezy_customer_id": customer_id,
                "lemon_squeezy_order_id": order_id,
                "lemon_squeezy_product_id": product_id,
                "lemon_squeezy_variant_id": variant_id,
                "status": self._map_status(attributes.get("status")),
                "plan_tier": plan_tier,
                "billing_interval": attributes.get("billing_anchor", "month"),
                "unit_price": attributes.get("price", 0) / 100,  # Convert from cents
                "quantity": attributes.get("quantity", 1),
                "total_price": attributes.get("subtotal", 0) / 100,
                "currency": attributes.get("currency", "USD"),
                "is_trial": attributes.get("trial_ends_at") is not None,
                "trial_ends_at": attributes.get("trial_ends_at"),
                "current_period_start": attributes.get("renews_at"),
                "current_period_end": attributes.get("ends_at"),
                "cancel_at_period_end": attributes.get("cancelled", False),
                "cancelled_at": attributes.get("cancelled_at"),
                "update_payment_method_url": attributes.get("urls", {}).get("update_payment_method"),
                "customer_portal_url": attributes.get("urls", {}).get("customer_portal"),
            }
        )
        
        logger.info(f"Subscription {subscription_id} {'created' if created else 'updated'}")
    
    def _handle_subscription_updated(self, payload: Dict) -> None:
        """Handle subscription_updated event."""
        data = payload.get("data", {})
        subscription_id = data.get("id")
        attributes = data.get("attributes", {})
        
        try:
            subscription = Subscription.objects.get(lemon_squeezy_id=subscription_id)
        except Subscription.DoesNotExist:
            logger.error(f"Subscription {subscription_id} not found")
            return
        
        # Update subscription fields
        subscription.status = self._map_status(attributes.get("status"))
        subscription.cancel_at_period_end = attributes.get("cancelled", False)
        subscription.cancelled_at = attributes.get("cancelled_at")
        subscription.current_period_end = attributes.get("ends_at")
        subscription.save()
        
        logger.info(f"Subscription {subscription_id} updated")
    
    def _handle_subscription_cancelled(self, payload: Dict) -> None:
        """Handle subscription_cancelled event."""
        data = payload.get("data", {})
        subscription_id = data.get("id")
        
        try:
            subscription = Subscription.objects.get(lemon_squeezy_id=subscription_id)
            subscription.status = SubscriptionStatus.CANCELLED
            subscription.cancelled_at = datetime.now()
            subscription.save()
            
            logger.info(f"Subscription {subscription_id} cancelled")
        except Subscription.DoesNotExist:
            logger.error(f"Subscription {subscription_id} not found")
    
    def _handle_subscription_expired(self, payload: Dict) -> None:
        """Handle subscription_expired event."""
        data = payload.get("data", {})
        subscription_id = data.get("id")
        
        try:
            subscription = Subscription.objects.get(lemon_squeezy_id=subscription_id)
            subscription.status = SubscriptionStatus.EXPIRED
            subscription.save()
            
            logger.info(f"Subscription {subscription_id} expired")
        except Subscription.DoesNotExist:
            logger.error(f"Subscription {subscription_id} not found")
    
    def _handle_subscription_paused(self, payload: Dict) -> None:
        """Handle subscription_paused event."""
        data = payload.get("data", {})
        subscription_id = data.get("id")
        
        try:
            subscription = Subscription.objects.get(lemon_squeezy_id=subscription_id)
            subscription.status = SubscriptionStatus.PAUSED
            subscription.save()
            
            logger.info(f"Subscription {subscription_id} paused")
        except Subscription.DoesNotExist:
            logger.error(f"Subscription {subscription_id} not found")
    
    def _handle_subscription_resumed(self, payload: Dict) -> None:
        """Handle subscription_resumed event."""
        data = payload.get("data", {})
        subscription_id = data.get("id")
        
        try:
            subscription = Subscription.objects.get(lemon_squeezy_id=subscription_id)
            subscription.status = SubscriptionStatus.ACTIVE
            subscription.save()
            
            logger.info(f"Subscription {subscription_id} resumed")
        except Subscription.DoesNotExist:
            logger.error(f"Subscription {subscription_id} not found")
    
    def _handle_payment_success(self, payload: Dict) -> None:
        """Handle subscription_payment_success event."""
        data = payload.get("data", {})
        subscription_id = data.get("attributes", {}).get("subscription_id")
        
        if subscription_id:
            try:
                subscription = Subscription.objects.get(lemon_squeezy_id=subscription_id)
                subscription.status = SubscriptionStatus.ACTIVE
                subscription.save()
                
                logger.info(f"Payment success for subscription {subscription_id}")
            except Subscription.DoesNotExist:
                logger.error(f"Subscription {subscription_id} not found")
    
    def _handle_payment_failed(self, payload: Dict) -> None:
        """Handle subscription_payment_failed event."""
        data = payload.get("data", {})
        subscription_id = data.get("attributes", {}).get("subscription_id")
        
        if subscription_id:
            try:
                subscription = Subscription.objects.get(lemon_squeezy_id=subscription_id)
                subscription.status = SubscriptionStatus.PAST_DUE
                subscription.save()
                
                logger.info(f"Payment failed for subscription {subscription_id}")
            except Subscription.DoesNotExist:
                logger.error(f"Subscription {subscription_id} not found")
    
    def _handle_payment_recovered(self, payload: Dict) -> None:
        """Handle subscription_payment_recovered event."""
        data = payload.get("data", {})
        subscription_id = data.get("attributes", {}).get("subscription_id")
        
        if subscription_id:
            try:
                subscription = Subscription.objects.get(lemon_squeezy_id=subscription_id)
                subscription.status = SubscriptionStatus.ACTIVE
                subscription.save()
                
                logger.info(f"Payment recovered for subscription {subscription_id}")
            except Subscription.DoesNotExist:
                logger.error(f"Subscription {subscription_id} not found")
    
    def _handle_order_created(self, payload: Dict) -> None:
        """Handle order_created event."""
        data = payload.get("data", {})
        attributes = data.get("attributes", {})
        
        # Create invoice record
        order_id = data.get("id")
        subscription_id = attributes.get("subscription_id")
        
        if subscription_id:
            try:
                subscription = Subscription.objects.get(lemon_squeezy_id=subscription_id)
                
                Invoice.objects.create(
                    subscription=subscription,
                    lemon_squeezy_invoice_id=order_id,
                    invoice_number=attributes.get("order_number", ""),
                    status=attributes.get("status", ""),
                    amount=attributes.get("total", 0) / 100,
                    currency=attributes.get("currency", "USD"),
                    invoiced_at=attributes.get("created_at"),
                    due_at=attributes.get("created_at"),
                    paid_at=attributes.get("refunded_at") if attributes.get("refunded") else None,
                )
                
                logger.info(f"Invoice created for order {order_id}")
            except Subscription.DoesNotExist:
                logger.error(f"Subscription {subscription_id} not found")
    
    def _handle_license_key_created(self, payload: Dict) -> None:
        """Handle license_key_created event (for self-hosted enterprise)."""
        pass  # Implement if needed for enterprise licenses
    
    def _map_status(self, ls_status: str) -> str:
        """Map Lemon Squeezy status to our status."""
        status_map = {
            "active": SubscriptionStatus.ACTIVE,
            "cancelled": SubscriptionStatus.CANCELLED,
            "past_due": SubscriptionStatus.PAST_DUE,
            "unpaid": SubscriptionStatus.UNPAID,
            "paused": SubscriptionStatus.PAUSED,
            "expired": SubscriptionStatus.EXPIRED,
            "trialing": SubscriptionStatus.TRIALING,
        }
        return status_map.get(ls_status, SubscriptionStatus.ACTIVE)
    
    def _get_plan_tier_from_variant(self, variant_id: str) -> str:
        """Determine plan tier from variant ID."""
        # Map variant IDs to plan tiers
        # These should match your Lemon Squeezy variant IDs
        variant_map = {
            settings.LEMON_SQUEEZY_FREE_VARIANT_ID: PlanTier.FREE,
            settings.LEMON_SQUEEZY_STARTER_MONTHLY_VARIANT_ID: PlanTier.STARTER,
            settings.LEMON_SQUEEZY_STARTER_YEARLY_VARIANT_ID: PlanTier.STARTER,
            settings.LEMON_SQUEEZY_PRO_MONTHLY_VARIANT_ID: PlanTier.PRO,
            settings.LEMON_SQUEEZY_PRO_YEARLY_VARIANT_ID: PlanTier.PRO,
            settings.LEMON_SQUEEZY_ENTERPRISE_VARIANT_ID: PlanTier.ENTERPRISE,
        }
        return variant_map.get(variant_id, PlanTier.FREE)


webhook_handler = LemonSqueezyWebhookHandler()
```

### API Views

Create [`apps/api/plane/billing/views/subscription.py`](apps/api/plane/billing/views/subscription.py:1):

```python
# Copyright (c) 2023-present Plane Software, Inc. and contributors
# SPDX-License-Identifier: AGPL-3.0-only

import json
from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from plane.billing.services.lemon_squeezy import lemon_squeezy
from plane.billing.webhooks.lemon_squeezy import webhook_handler
from plane.db.models import Subscription, Invoice, FeatureUsage
from plane.db.models.subscription import PlanTier


class SubscriptionView(View):
    """Get current subscription details."""
    
    def get(self, request, workspace_slug):
        try:
            subscription = Subscription.objects.filter(
                workspace__slug=workspace_slug
            ).select_related("workspace").first()
            
            if not subscription:
                # Return free plan as default
                return JsonResponse({
                    "plan": PlanTier.FREE,
                    "status": "active",
                    "is_trial": False,
                    "features": self._get_free_plan_features(),
                })
            
            return JsonResponse({
                "id": str(subscription.id),
                "plan": subscription.plan_tier,
                "status": subscription.status,
                "is_trial": subscription.is_trial,
                "trial_ends_at": subscription.trial_ends_at.isoformat() if subscription.trial_ends_at else None,
                "current_period_start": subscription.current_period_start.isoformat() if subscription.current_period_start else None,
                "current_period_end": subscription.current_period_end.isoformat() if subscription.current_period_end else None,
                "cancel_at_period_end": subscription.cancel_at_period_end,
                "quantity": subscription.quantity,
                "unit_price": str(subscription.unit_price),
                "total_price": str(subscription.total_price),
                "currency": subscription.currency,
                "features": self._get_plan_features(subscription.plan_tier),
                "customer_portal_url": subscription.customer_portal_url,
            })
            
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    
    def _get_free_plan_features(self):
        return {
            "max_projects": 3,
            "max_members": 1,
            "max_storage_gb": 1,
            "features": ["basic_task_management", "kanban_view", "list_view"],
        }
    
    def _get_plan_features(self, plan_tier):
        features = {
            PlanTier.FREE: {
                "max_projects": 3,
                "max_members": 1,
                "max_storage_gb": 1,
                "features": ["basic_task_management", "kanban_view", "list_view"],
            },
            PlanTier.STARTER: {
                "max_projects": None,  # Unlimited
                "max_members": 10,
                "max_storage_gb": 10,
                "features": [
                    "basic_task_management",
                    "kanban_view",
                    "list_view",
                    "sprint_planning",
                    "cycle_management",
                    "basic_analytics",
                    "github_gitlab_integration",
                    "slack_notifications",
                ],
            },
            PlanTier.PRO: {
                "max_projects": None,
                "max_members": None,  # Unlimited
                "max_storage_gb": 50,
                "features": [
                    "all_starter_features",
                    "advanced_analytics",
                    "custom_workflows",
                    "time_tracking",
                    "bulk_operations",
                    "public_views",
                    "api_access",
                    "advanced_integrations",
                ],
            },
            PlanTier.ENTERPRISE: {
                "max_projects": None,
                "max_members": None,
                "max_storage_gb": None,  # Unlimited
                "features": [
                    "all_pro_features",
                    "sso_saml",
                    "advanced_security",
                    "audit_logs",
                    "dedicated_support",
                    "custom_integrations",
                ],
            },
        }
        return features.get(plan_tier, features[PlanTier.FREE])


class CheckoutView(View):
    """Create checkout session for subscription."""
    
    def post(self, request, workspace_slug):
        try:
            body = json.loads(request.body)
            variant_id = body.get("variant_id")
            
            if not variant_id:
                return JsonResponse({"error": "variant_id required"}, status=400)
            
            # Get workspace
            from plane.db.models import Workspace
            workspace = Workspace.objects.get(slug=workspace_slug)
            
            # Create checkout
            checkout = lemon_squeezy.create_checkout(
                variant_id=variant_id,
                email=request.user.email,
                workspace_id=str(workspace.id),
                user_id=str(request.user.id),
            )
            
            checkout_data = checkout.get("data", {})
            
            return JsonResponse({
                "checkout_id": checkout_data.get("id"),
                "checkout_url": checkout_data.get("attributes", {}).get("url"),
            })
            
        except Workspace.DoesNotExist:
            return JsonResponse({"error": "Workspace not found"}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)


class CustomerPortalView(View):
    """Get customer portal URL."""
    
    def post(self, request, workspace_slug):
        try:
            subscription = Subscription.objects.filter(
                workspace__slug=workspace_slug
            ).first()
            
            if not subscription:
                return JsonResponse({"error": "No subscription found"}, status=404)
            
            portal_url = lemon_squeezy.get_customer_portal_url(
                subscription.lemon_squeezy_customer_id
            )
            
            return JsonResponse({"portal_url": portal_url})
            
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)


class InvoicesView(View):
    """Get invoice history."""
    
    def get(self, request, workspace_slug):
        try:
            subscription = Subscription.objects.filter(
                workspace__slug=workspace_slug
            ).first()
            
            if not subscription:
                return JsonResponse({"invoices": []})
            
            invoices = Invoice.objects.filter(
                subscription=subscription
            ).order_by("-invoiced_at")
            
            return JsonResponse({
                "invoices": [
                    {
                        "id": str(inv.id),
                        "invoice_number": inv.invoice_number,
                        "status": inv.status,
                        "amount": str(inv.amount),
                        "currency": inv.currency,
                        "invoiced_at": inv.invoiced_at.isoformat(),
                        "paid_at": inv.paid_at.isoformat() if inv.paid_at else None,
                        "pdf_url": inv.pdf_url,
                    }
                    for inv in invoices
                ]
            })
            
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)


@method_decorator(csrf_exempt, name="dispatch")
class WebhookView(View):
    """Handle Lemon Squeezy webhooks."""
    
    def post(self, request):
        try:
            # Verify signature
            signature = request.META.get("HTTP_X_SIGNATURE", "")
            
            if not webhook_handler.verify_signature(request.body, signature):
                return JsonResponse({"error": "Invalid signature"}, status=401)
            
            # Parse payload
            payload = json.loads(request.body)
            event_type = payload.get("meta", {}).get("event_name")
            event_id = payload.get("meta", {}).get("event_id")
            
            # Log event
            from plane.db.models import SubscriptionEvent
            event = SubscriptionEvent.objects.create(
                event_type=event_type,
                lemon_squeezy_event_id=event_id,
                payload=payload,
            )
            
            # Process event
            webhook_handler.handle_event(event_type, payload)
            
            # Mark as processed
            event.processed = True
            event.save()
            
            return JsonResponse({"status": "ok"})
            
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)


class UsageView(View):
    """Get feature usage statistics."""
    
    def get(self, request, workspace_slug):
        try:
            workspace = Workspace.objects.get(slug=workspace_slug)
            
            # Get current period usage
            from datetime import date
            today = date.today()
            
            usage = FeatureUsage.objects.filter(
                workspace=workspace,
                usage_date__month=today.month,
                usage_date__year=today.year,
            )
            
            return JsonResponse({
                "usage": [
                    {
                        "feature": u.feature_name,
                        "count": u.usage_count,
                        "date": u.usage_date.isoformat(),
                    }
                    for u in usage
                ]
            })
            
        except Workspace.DoesNotExist:
            return JsonResponse({"error": "Workspace not found"}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
```

## Frontend Implementation

### Billing Service

Create [`apps/web/core/services/billing.service.ts`](apps/web/core/services/billing.service.ts:1):

```typescript
import { API_BASE_URL } from "@plane/constants";

export interface Subscription {
  id: string;
  plan: "free" | "starter" | "pro" | "enterprise";
  status: string;
  is_trial: boolean;
  trial_ends_at?: string;
  current_period_start?: string;
  current_period_end?: string;
  cancel_at_period_end: boolean;
  quantity: number;
  unit_price: string;
  total_price: string;
  currency: string;
  features: PlanFeatures;
  customer_portal_url?: string;
}

export interface PlanFeatures {
  max_projects: number | null;
  max_members: number | null;
  max_storage_gb: number | null;
  features: string[];
}

export interface Invoice {
  id: string;
  invoice_number: string;
  status: string;
  amount: string;
  currency: string;
  invoiced_at: string;
  paid_at?: string;
  pdf_url?: string;
}

export class BillingService {
  private baseUrl = `${API_BASE_URL}/api/billing`;

  async getSubscription(workspaceSlug: string): Promise<Subscription> {
    const response = await fetch(`${this.baseUrl}/${workspaceSlug}/subscription`, {
      credentials: "include",
    });
    
    if (!response.ok) {
      throw new Error("Failed to fetch subscription");
    }
    
    return response.json();
  }

  async createCheckout(workspaceSlug: string, variantId: string): Promise<{ checkout_id: string; checkout_url: string }> {
    const response = await fetch(`${this.baseUrl}/${workspaceSlug}/checkout`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify({ variant_id: variantId }),
    });
    
    if (!response.ok) {
      throw new Error("Failed to create checkout");
    }
    
    return response.json();
  }

  async getCustomerPortal(workspaceSlug: string): Promise<{ portal_url: string }> {
    const response = await fetch(`${this.baseUrl}/${workspaceSlug}/portal`, {
      method: "POST",
      credentials: "include",
    });
    
    if (!response.ok) {
      throw new Error("Failed to get customer portal");
    }
    
    return response.json();
  }

  async getInvoices(workspaceSlug: string): Promise<{ invoices: Invoice[] }> {
    const response = await fetch(`${this.baseUrl}/${workspaceSlug}/invoices`, {
      credentials: "include",
    });
    
    if (!response.ok) {
      throw new Error("Failed to fetch invoices");
    }
    
    return response.json();
  }

  async getUsage(workspaceSlug: string): Promise<{ usage: Array<{ feature: string; count: number; date: string }> }> {
    const response = await fetch(`${this.baseUrl}/${workspaceSlug}/usage`, {
      credentials: "include",
    });
    
    if (!response.ok) {
      throw new Error("Failed to fetch usage");
    }
    
    return response.json();
  }
}

export const billingService = new BillingService();
```

### Plan Configuration

Create [`apps/web/core/constants/plans.ts`](apps/web/core/constants/plans.ts:1):

```typescript
export const PLAN_TIERS = {
  FREE: "free",
  STARTER: "starter",
  PRO: "pro",
  ENTERPRISE: "enterprise",
} as const;

export type PlanTier = typeof PLAN_TIERS[keyof typeof PLAN_TIERS];

export interface PlanConfig {
  id: PlanTier;
  name: string;
  description: string;
  monthlyPrice: number;
  yearlyPrice: number;
  yearlyDiscount: string;
  features: PlanFeature[];
  limits: PlanLimits;
  cta: {
    text: string;
    variant: "primary" | "secondary" | "outline";
  };
}

export interface PlanFeature {
  name: string;
  included: boolean;
  tooltip?: string;
}

export interface PlanLimits {
  maxProjects: number | null;
  maxMembers: number | null;
  maxStorageGB: number | null;
  maxApiCalls?: number | null;
}

export const PLANS: Record<PlanTier, PlanConfig> = {
  [PLAN_TIERS.FREE]: {
    id: PLAN_TIERS.FREE,
    name: "Free",
    description: "For individuals getting started",
    monthlyPrice: 0,
    yearlyPrice: 0,
    yearlyDiscount: "",
    limits: {
      maxProjects: 3,
      maxMembers: 1,
      maxStorageGB: 1,
    },
    features: [
      { name: "Basic task management", included: true },
      { name: "Kanban & List views", included: true },
      { name: "Basic search", included: true },
      { name: "Email notifications", included: true },
      { name: "7-day activity history", included: true },
      { name: "Sprint planning", included: false },
      { name: "Cycle management", included: false },
      { name: "Analytics & reporting", included: false },
      { name: "API access", included: false },
    ],
    cta: {
      text: "Get Started Free",
      variant: "secondary",
    },
  },
  [PLAN_TIERS.STARTER]: {
    id: PLAN_TIERS.STARTER,
    name: "Starter",
    description: "For small teams",
    monthlyPrice: 12,
    yearlyPrice: 10,
    yearlyDiscount: "Save 17%",
    limits: {
      maxProjects: null,
      maxMembers: 10,
      maxStorageGB: 10,
    },
    features: [
      { name: "Everything in Free", included: true },
      { name: "Unlimited projects", included: true },
      { name: "Up to 10 team members", included: true },
      { name: "10 GB storage per user", included: true },
      { name: "Sprint planning", included: true },
      { name: "Cycle management", included: true },
      { name: "Basic analytics", included: true },
      { name: "GitHub/GitLab integration", included: true },
      { name: "Slack notifications", included: true },
      { name: "30-day activity history", included: true },
      { name: "Advanced analytics", included: false },
      { name: "Time tracking", included: false },
    ],
    cta: {
      text: "Start Free Trial",
      variant: "primary",
    },
  },
  [PLAN_TIERS.PRO]: {
    id: PLAN_TIERS.PRO,
    name: "Pro",
    description: "For growing teams",
    monthlyPrice: 24,
    yearlyPrice: 20,
    yearlyDiscount: "Save 17%",
    limits: {
      maxProjects: null,
      maxMembers: null,
      maxStorageGB: 50,
      maxApiCalls: 10000,
    },
    features: [
      { name: "Everything in Starter", included: true },
      { name: "Unlimited team members", included: true },
      { name: "50 GB storage per user", included: true },
      { name: "Advanced analytics & reporting", included: true },
      { name: "Custom workflows", included: true },
      { name: "Time tracking", included: true },
      { name: "Bulk operations", included: true },
      { name: "Public views & pages", included: true },
      { name: "API access (10K calls/month)", included: true },
      { name: "Advanced integrations", included: true },
      { name: "90-day activity history", included: true },
      { name: "Priority support", included: true },
    ],
    cta: {
      text: "Start Free Trial",
      variant: "primary",
    },
  },
  [PLAN_TIERS.ENTERPRISE]: {
    id: PLAN_TIERS.ENTERPRISE,
    name: "Enterprise",
    description: "For organizations",
    monthlyPrice: 49,
    yearlyPrice: 41,
    yearlyDiscount: "Custom pricing",
    limits: {
      maxProjects: null,
      maxMembers: null,
      maxStorageGB: null,
      maxApiCalls: null,
    },
    features: [
      { name: "Everything in Pro", included: true },
      { name: "Unlimited storage", included: true },
      { name: "SSO/SAML authentication", included: true },
      { name: "Advanced security controls", included: true },
      { name: "Audit logs", included: true },
      { name: "Dedicated account manager", included: true },
      { name: "Custom onboarding", included: true },
      { name: "SLA guarantee", included: true },
      { name: "Unlimited API access", included: true },
      { name: "Custom integrations", included: true },
      { name: "24/7 phone support", included: true },
    ],
    cta: {
      text: "Contact Sales",
      variant: "outline",
    },
  },
};

// Lemon Squeezy Variant IDs (to be configured)
export const LEMON_SQUEEZY_VARIANTS = {
  STARTER_MONTHLY: process.env.VITE_LEMON_SQUEEZY_STARTER_MONTHLY_VARIANT_ID,
  STARTER_YEARLY: process.env.VITE_LEMON_SQUEEZY_STARTER_YEARLY_VARIANT_ID,
  PRO_MONTHLY: process.env.VITE_LEMON_SQUEEZY_PRO_MONTHLY_VARIANT_ID,
  PRO_YEARLY: process.env.VITE_LEMON_SQUEEZY_PRO_YEARLY_VARIANT_ID,
  ENTERPRISE: process.env.VITE_LEMON_SQUEEZY_ENTERPRISE_VARIANT_ID,
};
```

## Environment Configuration

### Backend Settings

Add to [`apps/api/plane/settings/common.py`](apps/api/plane/settings/common.py:1):

```python
# Lemon Squeezy Configuration
LEMON_SQUEEZY_API_KEY = os.environ.get("LEMON_SQUEEZY_API_KEY", "")
LEMON_SQUEEZY_STORE_ID = os.environ.get("LEMON_SQUEEZY_STORE_ID", "")
LEMON_SQUEEZY_WEBHOOK_SECRET = os.environ.get("LEMON_SQUEEZY_WEBHOOK_SECRET", "")

# Variant IDs
LEMON_SQUEEZY_FREE_VARIANT_ID = os.environ.get("LEMON_SQUEEZY_FREE_VARIANT_ID", "")
LEMON_SQUEEZY_STARTER_MONTHLY_VARIANT_ID = os.environ.get("LEMON_SQUEEZY_STARTER_MONTHLY_VARIANT_ID", "")
LEMON_SQUEEZY_STARTER_YEARLY_VARIANT_ID = os.environ.get("LEMON_SQUEEZY_STARTER_YEARLY_VARIANT_ID", "")
LEMON_SQUEEZY_PRO_MONTHLY_VARIANT_ID = os.environ.get("LEMON_SQUEEZY_PRO_MONTHLY_VARIANT_ID", "")
LEMON_SQUEEZY_PRO_YEARLY_VARIANT_ID = os.environ.get("LEMON_SQUEEZY_PRO_YEARLY_VARIANT_ID", "")
LEMON_SQUEEZY_ENTERPRISE_VARIANT_ID = os.environ.get("LEMON_SQUEEZY_ENTERPRISE_VARIANT_ID", "")
```

### Frontend Environment

Add to [`apps/web/.env.example`](apps/web/.env.example:1):

```bash
# Lemon Squeezy
VITE_LEMON_SQUEEZY_STARTER_MONTHLY_VARIANT_ID=
VITE_LEMON_SQUEEZY_STARTER_YEARLY_VARIANT_ID=
VITE_LEMON_SQUEEZY_PRO_MONTHLY_VARIANT_ID=
VITE_LEMON_SQUEEZY_PRO_YEARLY_VARIANT_ID=
VITE_LEMON_SQUEEZY_ENTERPRISE_VARIANT_ID=
```

## Testing Strategy

### Webhook Testing

Create [`apps/api/plane/tests/billing/test_webhooks.py`](apps/api/plane/tests/billing/test_webhooks.py:1):

```python
import json
import pytest
from django.test import TestCase, Client
from unittest.mock import patch, MagicMock

from plane.billing.webhooks.lemon_squeezy import webhook_handler


class WebhookTests(TestCase):
    def setUp(self):
        self.client = Client()
    
    @patch("plane.billing.webhooks.lemon_squeezy.webhook_handler.verify_signature")
    def test_subscription_created_webhook(self, mock_verify):
        mock_verify.return_value = True
        
        payload = {
            "meta": {
                "event_name": "subscription_created",
                "event_id": "evt_123",
            },
            "data": {
                "id": "sub_123",
                "attributes": {
                    "status": "active",
                    "price": 1200,
                    "checkout_data": {
                        "custom": {
                            "workspace_id": "ws-123",
                        }
                    }
                },
                "relationships": {
                    "customer": {"data": {"id": "cus_123"}},
                    "variant": {"data": {"id": "var_123"}},
                    "product": {"data": {"id": "prod_123"}},
                }
            }
        }
        
        response = self.client.post(
            "/api/billing/webhook/",
            data=json.dumps(payload),
            content_type="application/json",
            HTTP_X_SIGNATURE="valid_signature"
        )
        
        self.assertEqual(response.status_code, 200)
```

## Security Considerations

1. **Webhook Verification**: Always verify webhook signatures
2. **API Key Security**: Store API keys securely in environment variables
3. **Idempotency**: Handle duplicate webhook events gracefully
4. **Data Validation**: Validate all incoming data before processing
5. **Access Control**: Ensure users can only access their own subscription data

## Monitoring and Analytics

1. **Subscription Metrics**: Track MRR, churn rate, and conversion rates
2. **Webhook Monitoring**: Monitor webhook delivery and processing
3. **Error Tracking**: Track and alert on payment failures
4. **Usage Analytics**: Monitor feature usage across plans
