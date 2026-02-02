# Hoovix Monetization Strategy

## Executive Summary

This document outlines the comprehensive monetization strategy for Hoovix, including pricing tiers, feature gating, usage tracking, and the technical implementation of the subscription-based business model.

## Pricing Strategy

### Overview

Hoovix will adopt a **freemium model** with four distinct tiers designed to cater to different user segments, from individual users to large enterprises.

### Pricing Tiers

#### Free Tier
**Target Audience**: Individual users, freelancers, and small personal projects

| Feature | Limit |
|---------|-------|
| Price | $0/month |
| Projects | 3 |
| Team Members | 1 (solo) |
| Storage | 1 GB |
| Activity History | 7 days |

**Included Features**:
- Basic task management
- Kanban and List views
- Basic search functionality
- Email notifications
- Basic integrations (GitHub/GitLab read-only)

**Limitations**:
- No sprint planning
- No cycle management
- No advanced analytics
- No API access
- No custom workflows
- Limited storage

#### Starter Tier
**Target Audience**: Small teams (2-10 members)

| Feature | Limit |
|---------|-------|
| Price | $12/user/month (monthly) / $10/user/month (annual) |
| Projects | Unlimited |
| Team Members | Up to 10 |
| Storage | 10 GB per user |
| Activity History | 30 days |

**Included Features**:
- Everything in Free
- Unlimited projects
- Sprint planning
- Cycle management
- Basic analytics & reporting
- GitHub/GitLab integration (full)
- Slack notifications
- Priority email support

**Value Proposition**:
- Remove project limits
- Enable agile methodologies (sprints, cycles)
- Team collaboration features
- Essential integrations

#### Pro Tier
**Target Audience**: Growing teams and startups (10+ members)

| Feature | Limit |
|---------|-------|
| Price | $24/user/month (monthly) / $20/user/month (annual) |
| Projects | Unlimited |
| Team Members | Unlimited |
| Storage | 50 GB per user |
| API Calls | 10,000/month |
| Activity History | 90 days |

**Included Features**:
- Everything in Starter
- Unlimited team members
- Advanced analytics & reporting
- Custom workflows
- Time tracking
- Bulk operations
- Public views & pages
- API access (10,000 calls/month)
- Advanced integrations (Zapier, Notion)
- Priority chat support

**Value Proposition**:
- Scale without limits
- Advanced project management
- Data-driven insights
- Automation capabilities
- External integrations

#### Enterprise Tier
**Target Audience**: Large organizations with advanced needs

| Feature | Limit |
|---------|-------|
| Price | Custom ($49+/user/month) |
| Projects | Unlimited |
| Team Members | Unlimited |
| Storage | Unlimited |
| API Calls | Unlimited |
| Activity History | Unlimited |

**Included Features**:
- Everything in Pro
- SSO/SAML authentication (via Clerk)
- Advanced security controls
- Audit logs
- Dedicated account manager
- Custom onboarding
- SLA guarantee (99.9% uptime)
- Custom integrations
- 24/7 phone support
- Custom contract terms

**Value Proposition**:
- Enterprise-grade security
- Compliance & audit requirements
- Dedicated support
- Custom solutions
- Guaranteed uptime

## Feature Gating Architecture

### Feature Registry

Create [`apps/api/plane/billing/feature_registry.py`](apps/api/plane/billing/feature_registry.py:1):

```python
# Copyright (c) 2023-present Plane Software, Inc. and contributors
# SPDX-License-Identifier: AGPL-3.0-only

from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from enum import Enum


class FeatureCategory(Enum):
    CORE = "core"
    COLLABORATION = "collaboration"
    ANALYTICS = "analytics"
    INTEGRATIONS = "integrations"
    AUTOMATION = "automation"
    SECURITY = "security"


@dataclass
class Feature:
    """Definition of a feature with its requirements."""
    key: str
    name: str
    description: str
    category: FeatureCategory
    min_plan: str  # free, starter, pro, enterprise
    requires_metering: bool = False
    limit_key: Optional[str] = None
    metadata: Dict[str, Any] = None


class FeatureRegistry:
    """Central registry of all features and their plan requirements."""
    
    FEATURES = {
        # Core Features
        "basic_task_management": Feature(
            key="basic_task_management",
            name="Basic Task Management",
            description="Create and manage tasks",
            category=FeatureCategory.CORE,
            min_plan="free",
        ),
        "kanban_view": Feature(
            key="kanban_view",
            name="Kanban View",
            description="Visualize tasks in Kanban board",
            category=FeatureCategory.CORE,
            min_plan="free",
        ),
        "list_view": Feature(
            key="list_view",
            name="List View",
            description="View tasks in list format",
            category=FeatureCategory.CORE,
            min_plan="free",
        ),
        "sprint_planning": Feature(
            key="sprint_planning",
            name="Sprint Planning",
            description="Plan and manage sprints",
            category=FeatureCategory.CORE,
            min_plan="starter",
        ),
        "cycle_management": Feature(
            key="cycle_management",
            name="Cycle Management",
            description="Manage development cycles",
            category=FeatureCategory.CORE,
            min_plan="starter",
        ),
        "custom_workflows": Feature(
            key="custom_workflows",
            name="Custom Workflows",
            description="Create custom state workflows",
            category=FeatureCategory.CORE,
            min_plan="pro",
        ),
        "time_tracking": Feature(
            key="time_tracking",
            name="Time Tracking",
            description="Track time spent on tasks",
            category=FeatureCategory.CORE,
            min_plan="pro",
        ),
        "bulk_operations": Feature(
            key="bulk_operations",
            name="Bulk Operations",
            description="Perform bulk actions on tasks",
            category=FeatureCategory.CORE,
            min_plan="pro",
        ),
        
        # Collaboration Features
        "team_members": Feature(
            key="team_members",
            name="Team Members",
            description="Number of team members allowed",
            category=FeatureCategory.COLLABORATION,
            min_plan="free",
            requires_metering=True,
            limit_key="max_members",
        ),
        "projects": Feature(
            key="projects",
            name="Projects",
            description="Number of projects allowed",
            category=FeatureCategory.COLLABORATION,
            min_plan="free",
            requires_metering=True,
            limit_key="max_projects",
        ),
        "public_views": Feature(
            key="public_views",
            name="Public Views",
            description="Share views publicly",
            category=FeatureCategory.COLLABORATION,
            min_plan="pro",
        ),
        
        # Analytics Features
        "basic_analytics": Feature(
            key="basic_analytics",
            name="Basic Analytics",
            description="Basic project analytics",
            category=FeatureCategory.ANALYTICS,
            min_plan="starter",
        ),
        "advanced_analytics": Feature(
            key="advanced_analytics",
            name="Advanced Analytics",
            description="Advanced reporting and insights",
            category=FeatureCategory.ANALYTICS,
            min_plan="pro",
        ),
        "custom_reports": Feature(
            key="custom_reports",
            name="Custom Reports",
            description="Create custom reports",
            category=FeatureCategory.ANALYTICS,
            min_plan="pro",
        ),
        
        # Integration Features
        "github_gitlab_integration": Feature(
            key="github_gitlab_integration",
            name="GitHub/GitLab Integration",
            description="Connect with GitHub/GitLab",
            category=FeatureCategory.INTEGRATIONS,
            min_plan="starter",
        ),
        "slack_notifications": Feature(
            key="slack_notifications",
            name="Slack Notifications",
            description="Slack integration for notifications",
            category=FeatureCategory.INTEGRATIONS,
            min_plan="starter",
        ),
        "advanced_integrations": Feature(
            key="advanced_integrations",
            name="Advanced Integrations",
            description="Zapier, Notion, and more",
            category=FeatureCategory.INTEGRATIONS,
            min_plan="pro",
        ),
        "api_access": Feature(
            key="api_access",
            name="API Access",
            description="Access to Hoovix API",
            category=FeatureCategory.INTEGRATIONS,
            min_plan="pro",
            requires_metering=True,
            limit_key="max_api_calls",
        ),
        "custom_integrations": Feature(
            key="custom_integrations",
            name="Custom Integrations",
            description="Custom integration development",
            category=FeatureCategory.INTEGRATIONS,
            min_plan="enterprise",
        ),
        
        # Automation Features
        "automations": Feature(
            key="automations",
            name="Automations",
            description="Workflow automation",
            category=FeatureCategory.AUTOMATION,
            min_plan="pro",
        ),
        
        # Security Features
        "sso_saml": Feature(
            key="sso_saml",
            name="SSO/SAML",
            description="Single sign-on with SAML",
            category=FeatureCategory.SECURITY,
            min_plan="enterprise",
        ),
        "audit_logs": Feature(
            key="audit_logs",
            name="Audit Logs",
            description="Detailed audit logging",
            category=FeatureCategory.SECURITY,
            min_plan="enterprise",
        ),
        "advanced_security": Feature(
            key="advanced_security",
            name="Advanced Security",
            description="Advanced security controls",
            category=FeatureCategory.SECURITY,
            min_plan="enterprise",
        ),
    }
    
    PLAN_HIERARCHY = {
        "free": 0,
        "starter": 1,
        "pro": 2,
        "enterprise": 3,
    }
    
    @classmethod
    def get_feature(cls, key: str) -> Optional[Feature]:
        """Get feature definition by key."""
        return cls.FEATURES.get(key)
    
    @classmethod
    def is_feature_available(cls, feature_key: str, plan_tier: str) -> bool:
        """Check if a feature is available for a given plan tier."""
        feature = cls.get_feature(feature_key)
        if not feature:
            return False
        
        user_plan_level = cls.PLAN_HIERARCHY.get(plan_tier, 0)
        required_plan_level = cls.PLAN_HIERARCHY.get(feature.min_plan, 0)
        
        return user_plan_level >= required_plan_level
    
    @classmethod
    def get_features_for_plan(cls, plan_tier: str) -> List[Feature]:
        """Get all features available for a plan tier."""
        return [
            feature for feature in cls.FEATURES.values()
            if cls.is_feature_available(feature.key, plan_tier)
        ]
    
    @classmethod
    def get_metered_features(cls, plan_tier: str) -> List[Feature]:
        """Get all metered features for a plan tier."""
        return [
            feature for feature in cls.get_features_for_plan(plan_tier)
            if feature.requires_metering
        ]


# Plan limits configuration
PLAN_LIMITS = {
    "free": {
        "max_projects": 3,
        "max_members": 1,
        "max_storage_gb": 1,
        "max_api_calls": 0,
        "activity_history_days": 7,
    },
    "starter": {
        "max_projects": None,  # Unlimited
        "max_members": 10,
        "max_storage_gb": 10,
        "max_api_calls": 0,
        "activity_history_days": 30,
    },
    "pro": {
        "max_projects": None,
        "max_members": None,  # Unlimited
        "max_storage_gb": 50,
        "max_api_calls": 10000,
        "activity_history_days": 90,
    },
    "enterprise": {
        "max_projects": None,
        "max_members": None,
        "max_storage_gb": None,  # Unlimited
        "max_api_calls": None,  # Unlimited
        "activity_history_days": None,  # Unlimited
    },
}
```

### Backend Feature Gate

Create [`apps/api/plane/billing/permissions/feature_gate.py`](apps/api/plane/billing/permissions/feature_gate.py:1):

```python
# Copyright (c) 2023-present Plane Software, Inc. and contributors
# SPDX-License-Identifier: AGPL-3.0-only

from functools import wraps
from typing import Optional, Callable, Any

from django.http import JsonResponse
from django.core.exceptions import PermissionDenied

from plane.billing.feature_registry import FeatureRegistry, PLAN_LIMITS
from plane.db.models import Subscription, FeatureUsage
from plane.db.models.subscription import PlanTier


class FeatureGate:
    """
    Feature gating utility for checking feature availability and limits.
    """
    
    def __init__(self, workspace):
        self.workspace = workspace
        self._subscription = None
        self._plan_tier = None
        self._limits = None
    
    @property
    def subscription(self) -> Optional[Subscription]:
        """Get active subscription for workspace."""
        if self._subscription is None:
            self._subscription = Subscription.objects.filter(
                workspace=self.workspace,
                status__in=["active", "trialing"]
            ).first()
        return self._subscription
    
    @property
    def plan_tier(self) -> str:
        """Get current plan tier."""
        if self._plan_tier is None:
            if self.subscription:
                self._plan_tier = self.subscription.plan_tier
            else:
                self._plan_tier = PlanTier.FREE
        return self._plan_tier
    
    @property
    def limits(self) -> dict:
        """Get plan limits."""
        if self._limits is None:
            self._limits = PLAN_LIMITS.get(self.plan_tier, PLAN_LIMITS["free"])
        return self._limits
    
    def is_feature_available(self, feature_key: str) -> bool:
        """Check if a feature is available."""
        return FeatureRegistry.is_feature_available(feature_key, self.plan_tier)
    
    def check_feature(self, feature_key: str) -> bool:
        """
        Check if feature is available. Raises PermissionDenied if not.
        """
        if not self.is_feature_available(feature_key):
            raise PermissionDenied(
                f"Feature '{feature_key}' is not available on your current plan. "
                f"Please upgrade to access this feature."
            )
        return True
    
    def get_limit(self, limit_key: str) -> Optional[int]:
        """Get limit value for a specific limit key."""
        return self.limits.get(limit_key)
    
    def check_limit(self, limit_key: str, current_value: int) -> bool:
        """
        Check if current value is within plan limits.
        """
        limit = self.get_limit(limit_key)
        
        # None means unlimited
        if limit is None:
            return True
        
        return current_value < limit
    
    def check_and_increment_usage(self, feature_key: str, increment: int = 1) -> bool:
        """
        Check usage limit and increment if within limits.
        """
        feature = FeatureRegistry.get_feature(feature_key)
        if not feature or not feature.requires_metering:
            return True
        
        from datetime import date
        
        today = date.today()
        usage, created = FeatureUsage.objects.get_or_create(
            workspace=self.workspace,
            feature_name=feature_key,
            usage_date=today,
            defaults={"usage_count": 0}
        )
        
        limit = self.get_limit(feature.limit_key)
        if limit is not None:
            if usage.usage_count + increment > limit:
                return False
        
        usage.usage_count += increment
        usage.save()
        
        return True
    
    def get_usage(self, feature_key: str) -> int:
        """Get current usage for a feature."""
        from datetime import date
        
        today = date.today()
        try:
            usage = FeatureUsage.objects.get(
                workspace=self.workspace,
                feature_name=feature_key,
                usage_date=today
            )
            return usage.usage_count
        except FeatureUsage.DoesNotExist:
            return 0
    
    def get_usage_percentage(self, feature_key: str) -> float:
        """Get usage percentage for a feature."""
        feature = FeatureRegistry.get_feature(feature_key)
        if not feature or not feature.requires_metering:
            return 0.0
        
        usage = self.get_usage(feature_key)
        limit = self.get_limit(feature.limit_key)
        
        if limit is None:
            return 0.0
        
        return (usage / limit) * 100


def require_feature(feature_key: str):
    """
    Decorator to require a feature for a view.
    """
    def decorator(view_func: Callable) -> Callable:
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # Get workspace from request or kwargs
            workspace = getattr(request, "workspace", None)
            if not workspace and "workspace_slug" in kwargs:
                from plane.db.models import Workspace
                try:
                    workspace = Workspace.objects.get(slug=kwargs["workspace_slug"])
                except Workspace.DoesNotExist:
                    return JsonResponse({"error": "Workspace not found"}, status=404)
            
            if not workspace:
                return JsonResponse({"error": "Workspace required"}, status=400)
            
            gate = FeatureGate(workspace)
            
            try:
                gate.check_feature(feature_key)
            except PermissionDenied as e:
                return JsonResponse(
                    {
                        "error": str(e),
                        "feature": feature_key,
                        "current_plan": gate.plan_tier,
                        "upgrade_required": True,
                    },
                    status=403
                )
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def require_limit(limit_key: str, get_current_value: Callable):
    """
    Decorator to check plan limits.
    
    Args:
        limit_key: The limit to check
        get_current_value: Function to get current usage value
    """
    def decorator(view_func: Callable) -> Callable:
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            workspace = getattr(request, "workspace", None)
            if not workspace and "workspace_slug" in kwargs:
                from plane.db.models import Workspace
                try:
                    workspace = Workspace.objects.get(slug=kwargs["workspace_slug"])
                except Workspace.DoesNotExist:
                    return JsonResponse({"error": "Workspace not found"}, status=404)
            
            if not workspace:
                return JsonResponse({"error": "Workspace required"}, status=400)
            
            gate = FeatureGate(workspace)
            current_value = get_current_value(request, *args, **kwargs)
            
            if not gate.check_limit(limit_key, current_value):
                limit = gate.get_limit(limit_key)
                return JsonResponse(
                    {
                        "error": f"Plan limit exceeded. Current plan allows {limit} {limit_key}.",
                        "limit": limit,
                        "current": current_value,
                        "upgrade_required": True,
                    },
                    status=403
                )
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator
```

### Frontend Feature Gate Components

Create [`apps/web/core/components/billing/feature-gate.tsx`](apps/web/core/components/billing/feature-gate.tsx:1):

```typescript
import React from "react";
import { observer } from "mobx-react";
import { useParams } from "react-router";

import { useWorkspace } from "@/hooks/store/use-workspace";
import { useSubscription } from "@/hooks/store/use-subscription";
import { UpgradePrompt } from "./upgrade-prompt";

interface FeatureGateProps {
  feature: string;
  children: React.ReactNode;
  fallback?: React.ReactNode;
  showUpgradePrompt?: boolean;
}

export const FeatureGate = observer(function FeatureGate({
  feature,
  children,
  fallback,
  showUpgradePrompt = true,
}: FeatureGateProps) {
  const { workspaceSlug } = useParams();
  const { currentWorkspace } = useWorkspace();
  const { subscription, isLoading } = useSubscription(workspaceSlug);

  if (isLoading) {
    return null;
  }

  const planTier = subscription?.plan_tier || "free";
  const isAvailable = checkFeatureAvailability(feature, planTier);

  if (isAvailable) {
    return <>{children}</>;
  }

  if (fallback) {
    return <>{fallback}</>;
  }

  if (showUpgradePrompt) {
    return <UpgradePrompt feature={feature} currentPlan={planTier} />;
  }

  return null;
});

interface LimitGateProps {
  limitKey: string;
  currentValue: number;
  children: React.ReactNode;
  showWarningAt?: number; // Percentage at which to show warning (0-100)
}

export const LimitGate = observer(function LimitGate({
  limitKey,
  currentValue,
  children,
  showWarningAt = 80,
}: LimitGateProps) {
  const { workspaceSlug } = useParams();
  const { subscription, limits, isLoading } = useSubscription(workspaceSlug);

  if (isLoading) {
    return null;
  }

  const limit = limits?.[limitKey];
  
  // Unlimited
  if (limit === null || limit === undefined) {
    return <>{children}</>;
  }

  const percentage = (currentValue / limit) * 100;
  const isAtLimit = currentValue >= limit;
  const showWarning = percentage >= showWarningAt && !isAtLimit;

  return (
    <div className="relative">
      {isAtLimit ? (
        <UpgradePrompt
          title="Limit Reached"
          description={`You've reached the ${limitKey} limit for your current plan (${currentValue}/${limit}).`}
          currentPlan={subscription?.plan_tier || "free"}
        />
      ) : (
        <>
          {children}
          {showWarning && (
            <LimitWarning
              limitKey={limitKey}
              current={currentValue}
              limit={limit}
              percentage={percentage}
            />
          )}
        </>
      )}
    </div>
  );
});

// Helper function to check feature availability
function checkFeatureAvailability(feature: string, planTier: string): boolean {
  const featureRequirements: Record<string, string[]> = {
    basic_task_management: ["free", "starter", "pro", "enterprise"],
    kanban_view: ["free", "starter", "pro", "enterprise"],
    list_view: ["free", "starter", "pro", "enterprise"],
    sprint_planning: ["starter", "pro", "enterprise"],
    cycle_management: ["starter", "pro", "enterprise"],
    custom_workflows: ["pro", "enterprise"],
    time_tracking: ["pro", "enterprise"],
    bulk_operations: ["pro", "enterprise"],
    public_views: ["pro", "enterprise"],
    basic_analytics: ["starter", "pro", "enterprise"],
    advanced_analytics: ["pro", "enterprise"],
    github_gitlab_integration: ["starter", "pro", "enterprise"],
    slack_notifications: ["starter", "pro", "enterprise"],
    advanced_integrations: ["pro", "enterprise"],
    api_access: ["pro", "enterprise"],
    sso_saml: ["enterprise"],
    audit_logs: ["enterprise"],
  };

  const allowedPlans = featureRequirements[feature] || [];
  return allowedPlans.includes(planTier);
}

// Limit warning component
function LimitWarning({
  limitKey,
  current,
  limit,
  percentage,
}: {
  limitKey: string;
  current: number;
  limit: number;
  percentage: number;
}) {
  return (
    <div className="mt-2 p-3 bg-yellow-50 border border-yellow-200 rounded-md">
      <div className="flex items-center gap-2">
        <span className="text-yellow-600">⚠️</span>
        <span className="text-sm text-yellow-800">
          You're using {current} of {limit} {limitKey.replace(/_/g, " ")} ({percentage.toFixed(0)}%)
        </span>
      </div>
      <div className="mt-2 h-2 bg-yellow-200 rounded-full overflow-hidden">
        <div
          className="h-full bg-yellow-500 transition-all"
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  );
}
```

### Upgrade Prompt Component

Create [`apps/web/core/components/billing/upgrade-prompt.tsx`](apps/web/core/components/billing/upgrade-prompt.tsx:1):

```typescript
import React from "react";
import { useNavigate } from "react-router";
import { Button } from "@plane/ui";
import { Lock, Sparkles } from "lucide-react";

interface UpgradePromptProps {
  feature?: string;
  title?: string;
  description?: string;
  currentPlan: string;
}

export function UpgradePrompt({
  feature,
  title,
  description,
  currentPlan,
}: UpgradePromptProps) {
  const navigate = useNavigate();
  const { workspaceSlug } = useParams();

  const handleUpgrade = () => {
    navigate(`/${workspaceSlug}/settings/billing`);
  };

  const getFeatureName = (key?: string) => {
    if (!key) return "this feature";
    return key.replace(/_/g, " ");
  };

  const getUpgradePath = (current: string) => {
    const paths: Record<string, string> = {
      free: "Starter",
      starter: "Pro",
      pro: "Enterprise",
    };
    return paths[current] || "Pro";
  };

  return (
    <div className="flex flex-col items-center justify-center p-8 bg-surface-1 rounded-lg border border-border">
      <div className="w-16 h-16 bg-primary-100 rounded-full flex items-center justify-center mb-4">
        <Lock className="w-8 h-8 text-primary-600" />
      </div>
      
      <h3 className="text-lg font-semibold text-foreground mb-2">
        {title || `${getFeatureName(feature)} is a Premium Feature`}
      </h3>
      
      <p className="text-sm text-muted-foreground text-center mb-6 max-w-md">
        {description ||
          `Upgrade to the ${getUpgradePath(
            currentPlan
          )} plan to access ${getFeatureName(feature)} and more advanced features.`}
      </p>
      
      <div className="flex gap-3">
        <Button variant="outline" onClick={() => navigate(-1)}>
          Go Back
        </Button>
        <Button onClick={handleUpgrade} className="gap-2">
          <Sparkles className="w-4 h-4" />
          Upgrade Now
        </Button>
      </div>
      
      <p className="mt-4 text-xs text-muted-foreground">
        Current plan: <span className="capitalize font-medium">{currentPlan}</span>
      </p>
    </div>
  );
}
```

## Usage Tracking System

### Usage Tracking Service

Create [`apps/api/plane/billing/services/usage_tracker.py`](apps/api/plane/billing/services/usage_tracker.py:1):

```python
# Copyright (c) 2023-present Plane Software, Inc. and contributors
# SPDX-License-Identifier: AGPL-3.0-only

from datetime import date, datetime, timedelta
from typing import Optional, Dict, List
from django.db.models import Sum, Count
from django.utils import timezone

from plane.db.models import FeatureUsage, Subscription
from plane.db.models.workspace import Workspace


class UsageTracker:
    """
    Track and report feature usage for billing and analytics.
    """
    
    FEATURES_TO_TRACK = [
        "api_calls",
        "storage_gb",
        "team_members",
        "projects",
        "automations_run",
        "exports",
        "integrations_sync",
    ]
    
    @staticmethod
    def record_usage(
        workspace: Workspace,
        feature_name: str,
        usage_count: int = 1,
        metadata: Optional[Dict] = None
    ) -> FeatureUsage:
        """
        Record feature usage for today.
        """
        today = date.today()
        
        usage, created = FeatureUsage.objects.get_or_create(
            workspace=workspace,
            feature_name=feature_name,
            usage_date=today,
            defaults={
                "usage_count": 0,
                "metadata": metadata or {},
            }
        )
        
        usage.usage_count += usage_count
        if metadata:
            usage.metadata.update(metadata)
        usage.save()
        
        return usage
    
    @staticmethod
    def get_usage_for_period(
        workspace: Workspace,
        feature_name: str,
        start_date: date,
        end_date: date
    ) -> int:
        """
        Get total usage for a feature over a date range.
        """
        result = FeatureUsage.objects.filter(
            workspace=workspace,
            feature_name=feature_name,
            usage_date__range=[start_date, end_date]
        ).aggregate(total=Sum("usage_count"))
        
        return result["total"] or 0
    
    @staticmethod
    def get_current_month_usage(workspace: Workspace, feature_name: str) -> int:
        """
        Get usage for current month.
        """
        today = date.today()
        start_of_month = today.replace(day=1)
        
        return UsageTracker.get_usage_for_period(
            workspace, feature_name, start_of_month, today
        )
    
    @staticmethod
    def get_usage_report(
        workspace: Workspace,
        start_date: date,
        end_date: date
    ) -> Dict:
        """
        Generate comprehensive usage report.
        """
        report = {
            "workspace_id": str(workspace.id),
            "workspace_name": workspace.name,
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat(),
            },
            "features": {},
        }
        
        for feature in UsageTracker.FEATURES_TO_TRACK:
            usage = UsageTracker.get_usage_for_period(
                workspace, feature, start_date, end_date
            )
            report["features"][feature] = usage
        
        return report
    
    @staticmethod
    def get_usage_trends(
        workspace: Workspace,
        feature_name: str,
        days: int = 30
    ) -> List[Dict]:
        """
        Get daily usage trends for a feature.
        """
        end_date = date.today()
        start_date = end_date - timedelta(days=days)
        
        usages = FeatureUsage.objects.filter(
            workspace=workspace,
            feature_name=feature_name,
            usage_date__range=[start_date, end_date]
        ).order_by("usage_date")
        
        return [
            {
                "date": usage.usage_date.isoformat(),
                "count": usage.usage_count,
            }
            for usage in usages
        ]
    
    @staticmethod
    def check_usage_against_limits(workspace: Workspace) -> Dict:
        """
        Check current usage against plan limits.
        """
        from plane.billing.permissions.feature_gate import FeatureGate
        
        gate = FeatureGate(workspace)
        
        checks = {
            "team_members": {
                "current": workspace.workspace_member.count(),
                "limit": gate.get_limit("max_members"),
            },
            "projects": {
                "current": workspace.project.count(),
                "limit": gate.get_limit("max_projects"),
            },
            "storage_gb": {
                "current": UsageTracker.get_current_month_usage(workspace, "storage_gb"),
                "limit": gate.get_limit("max_storage_gb"),
            },
            "api_calls": {
                "current": UsageTracker.get_current_month_usage(workspace, "api_calls"),
                "limit": gate.get_limit("max_api_calls"),
            },
        }
        
        # Calculate percentages
        for key, data in checks.items():
            if data["limit"] is not None:
                data["percentage"] = (data["current"] / data["limit"]) * 100
            else:
                data["percentage"] = 0
        
        return checks


# Middleware to track API usage
class APIUsageMiddleware:
    """
    Middleware to track API call usage.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        response = self.get_response(request)
        
        # Track API usage for authenticated requests
        if request.user and request.user.is_authenticated:
            if hasattr(request, "workspace"):
                # Track the API call
                UsageTracker.record_usage(
                    workspace=request.workspace,
                    feature_name="api_calls",
                    usage_count=1,
                    metadata={
                        "path": request.path,
                        "method": request.method,
                    }
                )
        
        return response
```

## Billing Dashboard UI

### Subscription Store

Create [`apps/web/core/store/subscription.store.ts`](apps/web/core/store/subscription.store.ts:1):

```typescript
import { makeObservable, observable, action, computed, runInAction } from "mobx";
import { billingService, Subscription } from "@/services/billing.service";
import { PLAN_LIMITS } from "@/constants/plans";

export class SubscriptionStore {
  subscription: Subscription | null = null;
  isLoading = false;
  error: string | null = null;
  workspaceSlug: string | null = null;

  constructor() {
    makeObservable(this, {
      subscription: observable,
      isLoading: observable,
      error: observable,
      planTier: computed,
      limits: computed,
      isPaidPlan: computed,
      isTrial: computed,
      daysUntilTrialEnds: computed,
      fetchSubscription: action,
      createCheckout: action,
      openCustomerPortal: action,
    });
  }

  get planTier(): string {
    return this.subscription?.plan || "free";
  }

  get limits() {
    return PLAN_LIMITS[this.planTier] || PLAN_LIMITS.free;
  }

  get isPaidPlan(): boolean {
    return this.planTier !== "free";
  }

  get isTrial(): boolean {
    return this.subscription?.is_trial || false;
  }

  get daysUntilTrialEnds(): number | null {
    if (!this.subscription?.trial_ends_at) return null;
    const endDate = new Date(this.subscription.trial_ends_at);
    const now = new Date();
    const diffTime = endDate.getTime() - now.getTime();
    return Math.ceil(diffTime / (1000 * 60 * 60 * 24));
  }

  async fetchSubscription(workspaceSlug: string) {
    this.workspaceSlug = workspaceSlug;
    this.isLoading = true;
    this.error = null;

    try {
      const data = await billingService.getSubscription(workspaceSlug);
      runInAction(() => {
        this.subscription = data;
        this.isLoading = false;
      });
    } catch (err) {
      runInAction(() => {
        this.error = err instanceof Error ? err.message : "Failed to fetch subscription";
        this.isLoading = false;
      });
    }
  }

  async createCheckout(variantId: string): Promise<string> {
    if (!this.workspaceSlug) throw new Error("No workspace selected");
    
    const { checkout_url } = await billingService.createCheckout(
      this.workspaceSlug,
      variantId
    );
    return checkout_url;
  }

  async openCustomerPortal(): Promise<string> {
    if (!this.workspaceSlug) throw new Error("No workspace selected");
    
    const { portal_url } = await billingService.getCustomerPortal(this.workspaceSlug);
    return portal_url;
  }

  canUseFeature(featureKey: string): boolean {
    const featureRequirements: Record<string, string[]> = {
      basic_task_management: ["free", "starter", "pro", "enterprise"],
      sprint_planning: ["starter", "pro", "enterprise"],
      custom_workflows: ["pro", "enterprise"],
      // ... more features
    };

    const allowedPlans = featureRequirements[featureKey] || [];
    return allowedPlans.includes(this.planTier);
  }

  isWithinLimit(limitKey: string, currentValue: number): boolean {
    const limit = this.limits[limitKey];
    if (limit === null || limit === undefined) return true;
    return currentValue < limit;
  }
}
```

## Trial Management

### Trial Configuration

```python
# Trial settings
TRIAL_SETTINGS = {
    "duration_days": 14,
    "plans_available": ["starter", "pro"],
    "requires_credit_card": False,
    "features_enabled": "all",  # All features of the selected plan
}
```

### Trial Flow

1. **Sign Up**: User signs up via Clerk
2. **Plan Selection**: User selects trial plan (Starter or Pro)
3. **Trial Activation**: 14-day trial begins immediately
4. **Trial Reminders**: Email reminders at day 7, day 13
5. **Conversion**: User upgrades to paid plan or downgrades to Free

### Trial API Endpoints

```python
# Start trial
POST /api/billing/trial/start
{
    "plan_tier": "pro"
}

# Get trial status
GET /api/billing/trial/status
{
    "is_trial": true,
    "plan_tier": "pro",
    "trial_started_at": "2024-01-01T00:00:00Z",
    "trial_ends_at": "2024-01-15T00:00:00Z",
    "days_remaining": 7
}
```

## Revenue Optimization Strategies

### 1. Usage-Based Upsells

- Show usage warnings at 80% of limit
- Offer one-time top-ups for overages
- Suggest plan upgrades when consistently near limits

### 2. Annual Billing Incentives

- 17% discount for annual billing
- Highlight savings in UI
- Default to annual on pricing page

### 3. Team Growth Notifications

- Alert when approaching member limit
- Show per-seat pricing clearly
- Bulk discount for large teams

### 4. Feature Discovery

- Show locked features with preview
- "Try Pro for 14 days" prompts
- Feature usage analytics

## Analytics and Reporting

### Key Metrics to Track

1. **Conversion Metrics**
   - Trial-to-paid conversion rate
   - Free-to-paid conversion rate
   - Plan upgrade/downgrade rates

2. **Revenue Metrics**
   - MRR (Monthly Recurring Revenue)
   - ARR (Annual Recurring Revenue)
   - ARPU (Average Revenue Per User)
   - Churn rate

3. **Usage Metrics**
   - Feature adoption rates
   - API usage patterns
   - Storage utilization
   - Team size distribution

4. **Engagement Metrics**
   - DAU/MAU ratio
   - Feature usage frequency
   - Time to upgrade
   - Trial engagement score

### Reporting Dashboard

Create admin dashboard for:
- Real-time revenue metrics
- Subscription health overview
- Churn analysis
- Feature usage analytics
- Customer segmentation
