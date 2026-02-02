# Hoovix SaaS Implementation Roadmap

## Overview

This document provides a comprehensive implementation roadmap for transforming Hoovix into a SaaS product with Clerk authentication and Lemon Squeezy payments. The roadmap is organized into phases with clear milestones, deliverables, and timelines.

## Phase 1: Foundation - Clerk Authentication (Weeks 1-3)

### Week 1: Setup and Configuration

#### Day 1-2: Environment Setup
- [ ] Create Clerk account and application
- [ ] Configure Clerk dashboard
  - [ ] Set up social login providers (Google, GitHub, Microsoft)
  - [ ] Configure JWT templates
  - [ ] Set up webhook endpoints
  - [ ] Configure MFA options
- [ ] Add environment variables to `.env.example`
- [ ] Document Clerk credentials in team vault

#### Day 3-4: Frontend Dependencies
- [ ] Install `@clerk/clerk-react` in `apps/web`
- [ ] Install `@clerk/themes` for UI customization
- [ ] Update `package.json` with new dependencies
- [ ] Run `pnpm install` to verify installation

#### Day 5: Backend Dependencies
- [ ] Add `clerk-backend-api` to Python requirements
- [ ] Add `PyJWT` and `cryptography` for JWT validation
- [ ] Update `requirements.txt`
- [ ] Test Python package installation

### Week 2: Frontend Implementation

#### Day 1-2: Clerk Provider Setup
- [ ] Create `ClerkAuthProvider` component
- [ ] Update `app/provider.tsx` to wrap with Clerk
- [ ] Configure theme integration with next-themes
- [ ] Test provider initialization

#### Day 3-4: Authentication Pages
- [ ] Create `/sign-in` page with Clerk `<SignIn />`
- [ ] Create `/sign-up` page with Clerk `<SignUp />`
- [ ] Update routing configuration
- [ ] Style auth pages to match Hoovix design

#### Day 5: Authentication Wrapper Updates
- [ ] Update `AuthenticationWrapper` to use Clerk hooks
- [ ] Implement user sync logic
- [ ] Add loading states
- [ ] Test route protection

### Week 3: Backend Implementation

#### Day 1-2: JWT Middleware
- [ ] Create `ClerkJWTAuthenticationMiddleware`
- [ ] Implement JWKS loading and caching
- [ ] Add token verification logic
- [ ] Write unit tests

#### Day 3-4: User Sync and Webhooks
- [ ] Create user sync endpoint
- [ ] Implement Clerk webhook handler
- [ ] Add user model migrations
- [ ] Test webhook signature verification

#### Day 5: Integration Testing
- [ ] End-to-end auth flow testing
- [ ] Social login testing
- [ ] Session management testing
- [ ] Security testing

**Phase 1 Deliverables:**
- Working Clerk authentication
- User sync between Clerk and Hoovix
- JWT validation middleware
- Webhook handlers

---

## Phase 2: Payments - Lemon Squeezy Integration (Weeks 4-6)

### Week 4: Lemon Squeezy Setup

#### Day 1-2: Store Configuration
- [ ] Create Lemon Squeezy store
- [ ] Configure products and variants
  - [ ] Free Plan
  - [ ] Starter Plan (Monthly/Annual)
  - [ ] Pro Plan (Monthly/Annual)
  - [ ] Enterprise Plan
- [ ] Set up webhook endpoints
- [ ] Configure tax settings

#### Day 3-4: Database Schema
- [ ] Create `Subscription` model
- [ ] Create `SubscriptionEvent` model
- [ ] Create `FeatureUsage` model
- [ ] Create `Invoice` model
- [ ] Run migrations

#### Day 5: API Client
- [ ] Create `LemonSqueezyAPI` client
- [ ] Implement checkout creation
- [ ] Implement subscription management
- [ ] Add error handling

### Week 5: Webhook Implementation

#### Day 1-2: Webhook Handlers
- [ ] Implement `subscription_created` handler
- [ ] Implement `subscription_updated` handler
- [ ] Implement `subscription_cancelled` handler
- [ ] Implement `subscription_expired` handler

#### Day 3-4: Payment Handlers
- [ ] Implement `subscription_payment_success` handler
- [ ] Implement `subscription_payment_failed` handler
- [ ] Implement `subscription_payment_recovered` handler
- [ ] Implement `order_created` handler

#### Day 5: Testing
- [ ] Test webhook signature verification
- [ ] Test event processing
- [ ] Test error handling
- [ ] Create webhook test fixtures

### Week 6: Frontend Billing

#### Day 1-2: Billing Service
- [ ] Create `billingService` class
- [ ] Implement subscription fetching
- [ ] Implement checkout creation
- [ ] Implement portal access

#### Day 3-4: Billing UI Components
- [ ] Create `BillingPage` component
- [ ] Create `PlanSelector` component
- [ ] Create `SubscriptionCard` component
- [ ] Create `InvoiceList` component

#### Day 5: Integration
- [ ] Add billing link to settings
- [ ] Integrate with workspace settings
- [ ] Test checkout flow
- [ ] Test portal access

**Phase 2 Deliverables:**
- Working Lemon Squeezy integration
- Subscription management
- Webhook handlers
- Billing UI

---

## Phase 3: Feature Gating (Weeks 7-8)

### Week 7: Backend Feature Gating

#### Day 1-2: Feature Registry
- [ ] Create `FeatureRegistry` class
- [ ] Define all features and requirements
- [ ] Create plan limits configuration
- [ ] Write tests

#### Day 3-4: Permission System
- [ ] Create `FeatureGate` class
- [ ] Implement `require_feature` decorator
- [ ] Implement `require_limit` decorator
- [ ] Add middleware for API usage tracking

#### Day 5: Usage Tracking
- [ ] Create `UsageTracker` service
- [ ] Implement usage recording
- [ ] Create usage reporting
- [ ] Add usage alerts

### Week 8: Frontend Feature Gating

#### Day 1-2: Feature Gate Components
- [ ] Create `FeatureGate` component
- [ ] Create `LimitGate` component
- [ ] Create `UpgradePrompt` component
- [ ] Add feature checking utilities

#### Day 3-4: Plan Constants
- [ ] Define `PLANS` configuration
- [ ] Create feature availability maps
- [ ] Add limit configurations
- [ ] Document plan differences

#### Day 5: Integration
- [ ] Apply feature gates to existing features
- [ ] Add upgrade prompts
- [ ] Test feature availability
- [ ] Test limit enforcement

**Phase 3 Deliverables:**
- Feature gating system
- Usage tracking
- Upgrade prompts
- Plan enforcement

---

## Phase 4: UI/UX Improvements (Weeks 9-10)

### Week 9: Landing Page

#### Day 1-2: Hero Section
- [ ] Design hero section
- [ ] Add product demo/animation
- [ ] Create CTA buttons
- [ ] Implement responsive design

#### Day 3-4: Pricing Section
- [ ] Create pricing table
- [ ] Add plan comparison
- [ ] Implement billing toggle (monthly/annual)
- [ ] Add feature tooltips

#### Day 5: Additional Sections
- [ ] Features grid
- [ ] Testimonials
- [ ] FAQ section
- [ ] Footer

### Week 10: Onboarding

#### Day 1-2: Onboarding Flow
- [ ] Create onboarding wizard
- [ ] Step 1: Welcome & profile
- [ ] Step 2: Workspace creation
- [ ] Step 3: Team invitation

#### Day 3-4: Tutorial System
- [ ] Create tutorial overlay
- [ ] Add tooltips
- [ ] Implement progress tracking
- [ ] Add skip option

#### Day 5: Polish
- [ ] Add animations
- [ ] Test onboarding flow
- [ ] Optimize for mobile
- [ ] Add analytics tracking

**Phase 4 Deliverables:**
- New landing page
- Onboarding flow
- Tutorial system
- Improved UX

---

## Phase 5: Advanced Features (Weeks 11-12)

### Week 11: Team Management

#### Day 1-2: Member Limits
- [ ] Enforce member limits
- [ ] Show member usage
- [ ] Add upgrade prompts
- [ ] Implement member invitations

#### Day 3-4: Role Management
- [ ] Update role permissions
- [ ] Add admin controls
- [ ] Implement role-based access
- [ ] Test permission enforcement

#### Day 5: Billing Management
- [ ] Add billing admin controls
- [ ] Implement seat management
- [ ] Add usage reports
- [ ] Create billing dashboard

### Week 12: Enterprise Features

#### Day 1-2: SSO/SAML
- [ ] Configure Clerk SSO
- [ ] Add SAML providers
- [ ] Test SSO flow
- [ ] Document setup

#### Day 3-4: Security
- [ ] Add audit logs
- [ ] Implement security controls
- [ ] Add compliance features
- [ ] Test security settings

#### Day 5: Documentation
- [ ] Create admin documentation
- [ ] Write user guides
- [ ] Document API
- [ ] Create troubleshooting guide

**Phase 5 Deliverables:**
- Team management
- Enterprise features
- Documentation
- Admin controls

---

## Phase 6: Testing & Launch (Weeks 13-14)

### Week 13: Testing

#### Day 1-2: Unit Testing
- [ ] Test authentication flows
- [ ] Test payment flows
- [ ] Test feature gating
- [ ] Test usage tracking

#### Day 3-4: Integration Testing
- [ ] End-to-end user flows
- [ ] Webhook testing
- [ ] Load testing
- [ ] Security testing

#### Day 5: Bug Fixes
- [ ] Fix critical bugs
- [ ] Address performance issues
- [ ] Polish UI/UX
- [ ] Update documentation

### Week 14: Launch Preparation

#### Day 1-2: Production Setup
- [ ] Configure production Clerk
- [ ] Configure production Lemon Squeezy
- [ ] Set up monitoring
- [ ] Configure alerts

#### Day 3-4: Soft Launch
- [ ] Launch to beta users
- [ ] Monitor metrics
- [ ] Gather feedback
- [ ] Make adjustments

#### Day 5: Public Launch
- [ ] Announce launch
- [ ] Monitor closely
- [ ] Support users
- [ ] Celebrate! 🎉

**Phase 6 Deliverables:**
- Tested and stable product
- Production environment
- Monitoring and alerts
- Public launch

---

## Technical Implementation Details

### File Structure

```
apps/
├── web/
│   ├── app/
│   │   ├── providers/
│   │   │   └── clerk-provider.tsx
│   │   ├── (home)/
│   │   │   ├── sign-in/
│   │   │   │   └── page.tsx
│   │   │   └── sign-up/
│   │   │       └── page.tsx
│   │   └── (all)/
│   │       └── [workspaceSlug]/
│   │           └── settings/
│   │               └── billing/
│   │                   └── page.tsx
│   ├── core/
│   │   ├── components/
│   │   │   └── billing/
│   │   │       ├── feature-gate.tsx
│   │   │       ├── upgrade-prompt.tsx
│   │   │       ├── plan-selector.tsx
│   │   │       └── subscription-card.tsx
│   │   ├── constants/
│   │   │   └── plans.ts
│   │   ├── hooks/
│   │   │   └── store/
│   │   │       └── use-subscription.tsx
│   │   ├── services/
│   │   │   └── billing.service.ts
│   │   └── store/
│   │       └── subscription.store.ts
│   └── helpers/
│       └── authentication.helper.tsx
│
└── api/
    └── plane/
        ├── authentication/
        │   ├── middleware/
        │   │   └── clerk_jwt.py
        │   └── views/
        │       └── app/
        │           └── clerk.py
        ├── billing/
        │   ├── feature_registry.py
        │   ├── permissions/
        │   │   └── feature_gate.py
        │   ├── services/
        │   │   ├── lemon_squeezy.py
        │   │   └── usage_tracker.py
        │   ├── views/
        │   │   └── subscription.py
        │   └── webhooks/
        │       └── lemon_squeezy.py
        └── db/
            ├── migrations/
            │   └── 0119_add_subscription_models.py
            └── models/
                ├── subscription.py
                └── user.py
```

### Key Implementation Files

| File | Purpose | Phase |
|------|---------|-------|
| [`clerk-provider.tsx`](apps/web/app/providers/clerk-provider.tsx:1) | Clerk React provider | 1 |
| [`clerk_jwt.py`](apps/api/plane/authentication/middleware/clerk_jwt.py:1) | JWT validation middleware | 1 |
| [`subscription.py`](apps/api/plane/db/models/subscription.py:1) | Subscription models | 2 |
| [`lemon_squeezy.py`](apps/api/plane/billing/services/lemon_squeezy.py:1) | Lemon Squeezy API client | 2 |
| [`feature_registry.py`](apps/api/plane/billing/feature_registry.py:1) | Feature definitions | 3 |
| [`feature_gate.py`](apps/api/plane/billing/permissions/feature_gate.py:1) | Permission system | 3 |
| [`feature-gate.tsx`](apps/web/core/components/billing/feature-gate.tsx:1) | React feature gate | 3 |
| [`plans.ts`](apps/web/core/constants/plans.ts:1) | Plan configuration | 3 |

### Environment Variables

```bash
# Clerk
VITE_CLERK_PUBLISHABLE_KEY=pk_test_...
CLERK_SECRET_KEY=sk_test_...
CLERK_DOMAIN=https://clerk.your-domain.com
CLERK_WEBHOOK_SECRET=whsec_...

# Lemon Squeezy
LEMON_SQUEEZY_API_KEY=...
LEMON_SQUEEZY_STORE_ID=...
LEMON_SQUEEZY_WEBHOOK_SECRET=...
LEMON_SQUEEZY_STARTER_MONTHLY_VARIANT_ID=...
LEMON_SQUEEZY_STARTER_YEARLY_VARIANT_ID=...
LEMON_SQUEEZY_PRO_MONTHLY_VARIANT_ID=...
LEMON_SQUEEZY_PRO_YEARLY_VARIANT_ID=...
LEMON_SQUEEZY_ENTERPRISE_VARIANT_ID=...

# Feature Flags
ENABLE_CLERK_AUTH=true
ENABLE_LEMON_SQUEEZY=true
ENABLE_FEATURE_GATING=true
```

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/auth/clerk/sync/` | POST | Sync Clerk user |
| `/api/auth/clerk/webhook/` | POST | Clerk webhooks |
| `/api/billing/subscription/` | GET | Get subscription |
| `/api/billing/checkout/` | POST | Create checkout |
| `/api/billing/portal/` | POST | Get portal URL |
| `/api/billing/invoices/` | GET | Get invoices |
| `/api/billing/webhook/` | POST | Lemon Squeezy webhooks |
| `/api/billing/usage/` | GET | Get usage stats |

## Risk Management

### Technical Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Clerk integration issues | High | Thorough testing, fallback auth |
| Webhook failures | High | Retry logic, monitoring |
| Data migration issues | High | Backups, gradual rollout |
| Performance degradation | Medium | Load testing, caching |

### Business Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Low conversion rates | High | A/B testing, pricing experiments |
| High churn | High | Onboarding improvements, support |
| Payment failures | Medium | Multiple providers, monitoring |

## Success Metrics

### Phase 1 (Authentication)
- [ ] 100% of users can sign up via Clerk
- [ ] < 2s authentication time
- [ ] Zero security incidents

### Phase 2 (Payments)
- [ ] Successful checkout completion > 80%
- [ ] Webhook processing 100% success
- [ ] Payment failure rate < 5%

### Phase 3 (Feature Gating)
- [ ] Feature availability 99.9%
- [ ] Usage tracking accuracy 100%
- [ ] Upgrade conversion > 10%

### Overall Launch
- [ ] MRR growth > 20% MoM
- [ ] Churn rate < 5%
- [ ] NPS score > 50

## Post-Launch Roadmap

### Month 1-3: Optimization
- [ ] Analyze conversion funnels
- [ ] Optimize pricing page
- [ ] Improve onboarding
- [ ] Add more integrations

### Month 4-6: Expansion
- [ ] Add new features
- [ ] Expand plan options
- [ ] International support
- [ ] Mobile app

### Month 7-12: Scale
- [ ] Enterprise sales
- [ ] Partner program
- [ ] API marketplace
- [ ] White-label options
