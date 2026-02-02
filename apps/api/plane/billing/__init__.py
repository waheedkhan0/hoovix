# Copyright (c) 2023-present Plane Software, Inc. and contributors
# SPDX-License-Identifier: AGPL-3.0-only
# See the LICENSE file for details.

"""
Billing module for Hoovix SaaS.

This module handles:
- Subscription management via Lemon Squeezy
- Feature gating based on subscription plans
- Usage tracking and limits
- Billing webhooks
"""
