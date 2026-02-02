# Hoovix UI/UX Design System & Improvements

## Executive Summary

This document outlines comprehensive UI/UX improvements for Hoovix to transform it into a modern, competitive SaaS product rivaling Jira, Linear, Monday, and ClickUp. The design focuses on creating a premium, polished feel that justifies SaaS pricing tiers while maintaining exceptional usability and accessibility.

**Design Philosophy:**
- **Clarity First**: Every element serves a purpose
- **Delightful Interactions**: Micro-animations that feel responsive
- **Accessibility**: WCAG 2.1 AA compliance minimum
- **Performance**: 60fps animations, instant feedback
- **Consistency**: Unified design language across all touchpoints

---

## Table of Contents

1. [Design System Foundation](#1-design-system-foundation)
2. [Landing Page Design](#2-landing-page-design)
3. [Onboarding Flow](#3-onboarding-flow)
4. [Dashboard Enhancements](#4-dashboard-enhancements)
5. [Navigation Improvements](#5-navigation-improvements)
6. [Theme & Styling](#6-theme--styling)
7. [Mobile Responsiveness](#7-mobile-responsiveness)
8. [Billing UI Components](#8-billing-ui-components)
9. [Component Specifications](#9-component-specifications)
10. [Implementation Roadmap](#10-implementation-roadmap)

---

## 1. Design System Foundation

### 1.1 Color Palette Refinement

#### Primary Brand Colors
```css
/* Refined Brand Palette - More Vibrant */
--brand-50: oklch(0.97 0.02 242);
--brand-100: oklch(0.94 0.04 242);
--brand-200: oklch(0.88 0.08 242);
--brand-300: oklch(0.82 0.12 242);
--brand-400: oklch(0.74 0.16 242);
--brand-500: oklch(0.65 0.20 242);  /* Primary */
--brand-600: oklch(0.58 0.18 242);
--brand-700: oklch(0.51 0.16 242);
--brand-800: oklch(0.44 0.14 242);
--brand-900: oklch(0.37 0.12 242);
--brand-950: oklch(0.25 0.08 242);
```

#### Semantic Colors
```css
/* Success - Emerald */
--success-50: oklch(0.97 0.03 155);
--success-500: oklch(0.65 0.18 155);
--success-600: oklch(0.58 0.16 155);

/* Warning - Amber */
--warning-50: oklch(0.97 0.04 85);
--warning-500: oklch(0.75 0.16 85);
--warning-600: oklch(0.68 0.14 85);

/* Error - Rose */
--error-50: oklch(0.96 0.03 25);
--error-500: oklch(0.63 0.22 25);
--error-600: oklch(0.56 0.20 25);

/* Info - Blue */
--info-50: oklch(0.97 0.02 250);
--info-500: oklch(0.65 0.18 250);
--info-600: oklch(0.58 0.16 250);
```

#### Surface Colors (Light Mode)
```css
--surface-canvas: #fafafa;
--surface-primary: #ffffff;
--surface-secondary: #f5f5f5;
--surface-tertiary: #ebebeb;
--surface-elevated: #ffffff;
--surface-overlay: rgba(0, 0, 0, 0.5);
```

#### Surface Colors (Dark Mode)
```css
--surface-canvas: #0a0a0a;
--surface-primary: #141414;
--surface-secondary: #1a1a1a;
--surface-tertiary: #262626;
--surface-elevated: #1f1f1f;
--surface-overlay: rgba(0, 0, 0, 0.8);
```

### 1.2 Typography System

#### Font Stack
```css
--font-sans: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
--font-mono: 'JetBrains Mono', 'Fira Code', 'SF Mono', Consolas, monospace;
--font-display: 'Inter', sans-serif; /* For headings */
```

#### Type Scale
| Token | Size | Line Height | Weight | Letter Spacing | Usage |
|-------|------|-------------|--------|----------------|-------|
| text-2xs | 10px | 14px | 400 | 0.02em | Captions, timestamps |
| text-xs | 12px | 16px | 400 | 0.01em | Labels, small text |
| text-sm | 14px | 20px | 400 | 0 | Body text, descriptions |
| text-base | 16px | 24px | 400 | 0 | Primary body text |
| text-lg | 18px | 28px | 400 | -0.01em | Lead paragraphs |
| text-xl | 20px | 30px | 500 | -0.02em | Small headings |
| text-2xl | 24px | 32px | 600 | -0.02em | Section headings |
| text-3xl | 30px | 38px | 600 | -0.02em | Page headings |
| text-4xl | 36px | 44px | 700 | -0.03em | Hero text |
| text-5xl | 48px | 56px | 700 | -0.03em | Large display |
| text-6xl | 60px | 68px | 800 | -0.04em | Hero display |

### 1.3 Spacing System

```css
/* 4px base unit */
--space-0: 0;
--space-1: 4px;
--space-2: 8px;
--space-3: 12px;
--space-4: 16px;
--space-5: 20px;
--space-6: 24px;
--space-8: 32px;
--space-10: 40px;
--space-12: 48px;
--space-16: 64px;
--space-20: 80px;
--space-24: 96px;
--space-32: 128px;
```

### 1.4 Border Radius

```css
--radius-none: 0;
--radius-sm: 4px;
--radius-md: 6px;
--radius-lg: 8px;
--radius-xl: 12px;
--radius-2xl: 16px;
--radius-3xl: 24px;
--radius-full: 9999px;
```

### 1.5 Shadow System

```css
/* Light Mode Shadows */
--shadow-xs: 0 1px 2px rgba(0, 0, 0, 0.04);
--shadow-sm: 0 1px 3px rgba(0, 0, 0, 0.08), 0 1px 2px rgba(0, 0, 0, 0.04);
--shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.08), 0 2px 4px -1px rgba(0, 0, 0, 0.04);
--shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.08), 0 4px 6px -2px rgba(0, 0, 0, 0.04);
--shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.08), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
--shadow-2xl: 0 25px 50px -12px rgba(0, 0, 0, 0.25);

/* Dark Mode Shadows (subtle glow) */
--shadow-glow-sm: 0 0 8px rgba(255, 255, 255, 0.04);
--shadow-glow-md: 0 0 16px rgba(255, 255, 255, 0.06);
--shadow-glow-lg: 0 0 32px rgba(255, 255, 255, 0.08);
```

### 1.6 Animation & Easing

```css
/* Duration */
--duration-instant: 0ms;
--duration-fast: 100ms;
--duration-normal: 200ms;
--duration-slow: 300ms;
--duration-slower: 500ms;

/* Easing Functions */
--ease-linear: linear;
--ease-in: cubic-bezier(0.4, 0, 1, 1);
--ease-out: cubic-bezier(0, 0, 0.2, 1);
--ease-in-out: cubic-bezier(0.4, 0, 0.2, 1);
--ease-spring: cubic-bezier(0.34, 1.56, 0.64, 1);
--ease-bounce: cubic-bezier(0.68, -0.55, 0.265, 1.55);
```

---

## 2. Landing Page Design

### 2.1 Overall Structure

```
┌─────────────────────────────────────────────────────────────┐
│  NAVIGATION BAR (Fixed, glassmorphism on scroll)           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  HERO SECTION                                               │
│  - Animated gradient background                             │
│  - Main headline with typewriter effect                     │
│  - Subheadline with fade-in                                 │
│  - Primary CTA button with pulse animation                  │
│  - Product demo video/screenshot with 3D tilt               │
│  - Trust badges (logos of companies using)                  │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  SOCIAL PROOF SECTION                                       │
│  - Star rating with count                                   │
│  - User testimonial cards (horizontal scroll on mobile)     │
│  - "Loved by X teams" counter                               │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  FEATURES GRID (Bento Box Layout)                          │
│  ┌─────────────┬─────────────┬─────────────┐               │
│  │   Feature   │   Feature   │   Feature   │               │
│  │     1       │     2       │     3       │               │
│  │  (Large)    │  (Medium)   │  (Medium)   │               │
│  ├─────────────┴─────────────┼─────────────┤               │
│  │        Feature 4          │   Feature   │               │
│  │        (Wide)             │     5       │               │
│  │                           │  (Small)    │               │
│  └───────────────────────────┴─────────────┘               │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  HOW IT WORKS SECTION                                       │
│  - 3-step process with animated illustrations               │
│  - Step indicators with progress line                       │
│  - Interactive hover states                                 │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  INTERACTIVE PRICING TABLE                                  │
│  - Toggle: Monthly/Annual (save 20%)                        │
│  - 4-tier comparison (Free, Starter, Pro, Enterprise)       │
│  - Feature comparison with checkmarks                       │
│  - Popular plan highlight (Pro)                             │
│  - Hover effects on pricing cards                           │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  TESTIMONIALS SECTION                                       │
│  - Video testimonials with play overlay                     │
│  - Quote cards with avatar, name, role                      │
│  - Company logos carousel                                   │
│  - Star ratings                                             │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  FAQ ACCORDION SECTION                                      │
│  - Categorized questions                                    │
│  - Smooth expand/collapse animations                        │
│  - Search functionality                                     │
│  - "Still have questions?" CTA                              │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  FINAL CTA SECTION                                          │
│  - Gradient background                                      │
│  - Compelling headline                                      │
│  - Email capture form                                       │
│  - "Start free, no credit card" reassurance                 │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│  FOOTER                                                     │
│  - Multi-column links                                       │
│  - Newsletter signup                                        │
│  - Social links                                             │
│  - Legal links                                              │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 Hero Section Specifications

#### Layout
- **Height**: 100vh (min-height: 700px)
- **Background**: Animated gradient mesh (subtle movement)
- **Content**: Centered, max-width 900px
- **Padding**: 120px top, 80px bottom

#### Elements

**Navigation Bar**
```
Height: 72px
Background: transparent → rgba(255,255,255,0.8) on scroll
Backdrop-filter: blur(12px) on scroll
Position: fixed, z-index: 50
```

**Headline**
```
Font: text-6xl (60px), font-weight: 800
Color: --text-primary
Animation: Fade in + slide up (y: 30px → 0)
Duration: 600ms, delay: 200ms
```

**Subheadline**
```
Font: text-xl (20px), font-weight: 400
Color: --text-secondary
Max-width: 600px
Animation: Fade in, delay: 400ms
```

**CTA Button**
```
Size: lg (px-8 py-4)
Variant: primary with gradient
Shadow: shadow-lg with brand color glow
Animation: Subtle pulse on idle, scale on hover
Icon: ArrowRight, animates on hover
```

**Product Demo**
```
Container: rounded-2xl, shadow-2xl
Effect: 3D tilt on mouse move (max 5deg)
Border: 1px solid --border-subtle
Overlay: "Watch Demo" play button
```

### 2.3 Features Grid (Bento Box)

#### Layout Structure
```css
.features-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  grid-template-rows: repeat(2, 280px);
  gap: 24px;
}

.feature-card-large {
  grid-column: span 2;
  grid-row: span 2;
}

.feature-card-wide {
  grid-column: span 2;
}
```

#### Card Design
```
Background: --surface-primary
Border: 1px solid --border-subtle
Border-radius: --radius-2xl (16px)
Padding: 32px
Hover: translateY(-4px), shadow-lg, border-color transition
```

#### Card Content Pattern
```
Icon: 48px, rounded-xl background, gradient
Title: text-xl, font-weight: 600
Description: text-sm, --text-secondary
Visual: Screenshot/illustration at bottom
```

### 2.4 Pricing Table Specifications

#### Layout
```
Container: max-width 1200px, centered
Toggle: Monthly/Annual switch above table
Grid: 4 columns on desktop, 1 column on mobile
Gap: 24px
```

#### Pricing Card Design
```
Background: --surface-primary
Border: 1px solid --border-subtle
Border-radius: --radius-2xl
Padding: 32px
Popular Plan: 2px brand border, "Most Popular" badge

Hover: shadow-xl, translateY(-8px)
Transition: all 300ms ease-out
```

#### Card Content
```
Plan Name: text-lg, font-weight: 600, --text-secondary
Price: text-5xl, font-weight: 700
Billing: text-sm, --text-secondary
Features List:
  - Check icon (brand color)
  - Feature text
  - Disabled features (muted)
CTA Button: Full width, variant based on plan
```

### 2.5 FAQ Accordion Specifications

#### Layout
```
Container: max-width 800px, centered
Categories: Horizontal tabs above accordion
Items: Stacked vertically
```

#### Accordion Item Design
```
Background: transparent
Border-bottom: 1px solid --border-subtle
Padding: 24px 0

Question: text-lg, font-weight: 500
Icon: ChevronDown, rotates 180deg on open
Answer: text-base, --text-secondary, padding-top: 16px

Animation: 
  - Height: 0 → auto (300ms ease-out)
  - Opacity: 0 → 1 (200ms, 100ms delay)
  - Icon rotation: 300ms spring easing
```

---

## 3. Onboarding Flow

### 3.1 Flow Overview

```
┌─────────────────────────────────────────────────────────────┐
│  STEP 1: WELCOME                                            │
│  - Animated logo entrance                                   │
│  - Value proposition headline                               │
│  - "Get Started" primary CTA                                │
│  - "Already have an account? Sign in" link                  │
│  - Background: subtle gradient pattern                      │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  STEP 2: PROFILE SETUP                                      │
│  - Avatar upload with preview                               │
│  - Display name input                                       │
│  - Username validation (real-time)                          │
│  - Timezone selection (auto-detected)                       │
│  - Progress: 25%                                            │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  STEP 3: WORKSPACE CREATION                                 │
│  - Workspace name input                                     │
│  - URL slug auto-generation                                 │
│  - Workspace icon/color picker                              │
│  - Template selection (optional)                            │
│  - Progress: 50%                                            │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  STEP 4: TEAM INVITATION (Optional)                         │
│  - Email input with chip-style entries                      │
│  - Role selection per invitee                               │
│  - "Skip for now" option                                    │
│  - Progress: 75%                                            │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  STEP 5: QUICK TOUR / DASHBOARD                             │
│  - Interactive product tour (optional)                      │
│  - "Take a quick tour" or "Explore on my own"               │
│  - Confetti celebration on completion                       │
│  - Progress: 100%                                           │
└─────────────────────────────────────────────────────────────┘
```

### 3.2 Progress Indicator

```
Position: Top of content area, sticky
Height: 4px
Background: --border-subtle
Fill: brand gradient
Animation: Smooth width transition between steps
```

### 3.3 Step Navigation

```
Buttons:
  - "Back" (secondary, hidden on step 1)
  - "Continue" / "Get Started" (primary)
  - "Skip" (tertiary, where applicable)

Validation:
  - Real-time field validation
  - Continue disabled until valid
  - Error messages below fields
```

### 3.4 Profile Setup Step

#### Layout
```
Centered card, max-width 480px
Avatar upload centered at top
Form fields stacked below
```

#### Avatar Upload
```
Size: 120px diameter
Default: Initials with gradient background
Hover: Overlay with "Change" text
Click: Opens file picker
Preview: Immediate update on selection
Remove: X button on hover
```

#### Form Fields
```
Display Name:
  - Label: "What should we call you?"
  - Placeholder: "Your name"
  - Validation: Required, 2-50 chars

Username:
  - Label: "Choose a username"
  - Prefix: @
  - Validation: Real-time availability check
  - Loading: Spinner while checking
  - Success: Checkmark icon
  - Error: Red border + message

Timezone:
  - Label: "Your timezone"
  - Default: Auto-detected from browser
  - Dropdown: Searchable select
```

### 3.5 Workspace Creation Step

#### Layout
```
Two-column on desktop (form left, preview right)
Single column on mobile
```

#### Form Fields
```
Workspace Name:
  - Label: "What's your workspace name?"
  - Placeholder: "Acme Inc."
  - Validation: Required

Workspace URL:
  - Label: "Workspace URL"
  - Format: hoovix.com/[slug]
  - Auto-generated from name
  - Editable
  - Validation: Unique, alphanumeric + hyphens

Workspace Icon:
  - Color picker (preset palette)
  - Icon picker (emoji or Lucide icons)
  - Preview in real-time
```

#### Template Selection (Optional)
```
Grid of 4 template cards:
  - Blank
  - Software Development
  - Marketing
  - Design Team

Card Design:
  - Icon + Title
  - Brief description
  - Selected: Brand border, checkmark
```

### 3.6 Team Invitation Step

#### Email Input Component
```
Chip-style input:
  - Emails appear as removable chips
  - Comma or Enter to add
  - Validation: Email format
  - Duplicate prevention
  - Max: 10 invites at once

Role Selection:
  - Per-invitee dropdown
  - Options: Admin, Member, Viewer
  - Default: Member
```

### 3.7 Quick Tour

#### Tour Steps
```
1. Welcome tooltip on dashboard
2. Highlight sidebar navigation
3. Show project creation
4. Demonstrate task creation
5. Point out profile/settings

Each step:
  - Spotlight overlay on target
  - Tooltip with description
  - "Next" / "Skip Tour" buttons
  - Progress dots
```

---

## 4. Dashboard Enhancements

### 4.1 Widget System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  DASHBOARD HEADER                                           │
│  - Title + date                                             │
│  - "Customize" button                                       │
│  - View toggle (Grid/List)                                  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   WIDGET     │  │   WIDGET     │  │   WIDGET     │      │
│  │   (Large)    │  │   (Medium)   │  │   (Medium)   │      │
│  │              │  │              │  │              │      │
│  │  My Tasks    │  │  Activity    │  │   Quick      │      │
│  │              │  │   Feed       │  │   Actions    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│                                                             │
│  ┌────────────────────────┐  ┌────────────────────────┐    │
│  │        WIDGET          │  │        WIDGET          │    │
│  │        (Wide)          │  │        (Wide)          │    │
│  │                        │  │                        │    │
│  │     Sprint Progress    │  │      Team Activity     │    │
│  │                        │  │                        │    │
│  └────────────────────────┘  └────────────────────────┘    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 4.2 Widget Specifications

#### Widget Container
```
Background: --surface-primary
Border: 1px solid --border-subtle
Border-radius: --radius-xl
Padding: 24px
Shadow: --shadow-sm

Hover: shadow-md, border-color transition
Drag handle: Visible on hover, top-right corner
Resize: Corner handle on hover
```

#### Widget Header
```
Layout: Flex, space-between
Title: text-base, font-weight: 600
Actions: Settings (gear), Remove (x), Drag handle
```

### 4.3 Widget Types

#### 1. My Tasks Widget
```
Size: Large (2x2)
Content:
  - Tab filter: All | In Progress | Due Today
  - Task list (max 5 items)
  - Each item: Checkbox + Title + Due date + Priority
  - "View all tasks" link

Empty State:
  - Illustration
  - "No tasks assigned"
  - "Create a task" CTA
```

#### 2. Activity Feed Widget
```
Size: Medium (1x2)
Content:
  - Scrollable list
  - Activity items with avatar, action, timestamp
  - Group by date
  - Filter by type

Activity Types:
  - Task created/completed
  - Comment added
  - Status changed
  - Member joined
```

#### 3. Quick Actions Widget
```
Size: Medium (1x1)
Content:
  - Grid of action buttons
  - Icons with labels
  - Actions:
    * New Task
    * New Project
    * Invite Team
    * Create Sprint
```

#### 4. Sprint Progress Widget
```
Size: Wide (2x1)
Content:
  - Sprint name + dates
  - Progress bar with stats
  - Burndown sparkline
  - Days remaining counter
  - "View Sprint" link
```

#### 5. Stats Overview Widget
```
Size: Wide (2x1)
Content:
  - 4 metric cards in row
  - Metrics:
    * Tasks Completed
    * Active Issues
    * Team Velocity
    * Sprint Progress
  - Trend indicators (up/down)
```

#### 6. Recent Projects Widget
```
Size: Medium (1x2)
Content:
  - Project cards (icon, name, progress)
  - Progress bar per project
  - Member avatars
  - "View all" link
```

### 4.4 Drag-and-Drop Implementation

```typescript
// Using @dnd-kit/core
interface WidgetLayout {
  id: string;
  type: WidgetType;
  position: { x: number; y: number };
  size: { w: number; h: number };
}

// Grid system: 12 columns
// Widget sizes: 1x1 (3 cols), 1x2 (3 cols x 2 rows), 2x1 (6 cols), 2x2 (6 cols x 2 rows)
```

### 4.5 Customization Modal

```
Title: "Customize Dashboard"
Tabs: Available Widgets | Layout | Settings

Available Widgets:
  - Grid of widget previews
  - Toggle to add/remove
  - Drag to reorder

Layout:
  - Preset layouts (Default, Compact, Focus)
  - Column count selector

Settings:
  - Auto-refresh interval
  - Default date range
```

### 4.6 Empty States

```
Design Pattern:
  - Centered illustration (120px)
  - Title: text-lg, font-weight: 600
  - Description: text-sm, --text-secondary
  - Primary CTA button
  - Secondary link (optional)

Examples:
  - No tasks: "You're all caught up!" + "Create task"
  - No projects: "Start your first project" + "Create project"
  - No activity: "No recent activity" + "Invite team"
```

---

## 5. Navigation Improvements

### 5.1 Command Palette (Cmd+K)

#### Trigger
```
Keyboard: Cmd/Ctrl + K
Button: Search icon in header
Animation: Scale from center, fade in backdrop
```

#### Layout
```
Container:
  - Max-width: 640px
  - Position: Fixed, centered
  - Margin-top: 20vh
  - Border-radius: --radius-xl
  - Shadow: --shadow-2xl

Search Input:
  - Full width, no border
  - Placeholder: "Type a command or search..."
  - Prefix: Search icon
  - Height: 56px
  - Font-size: text-lg

Results Area:
  - Max-height: 400px
  - Scrollable
  - Grouped by category
```

#### Result Categories
```
Recent: Recently viewed items
Navigate: Pages, Projects, Settings
Actions: Create task, Invite member, etc.
Search: Matching tasks, projects, people
```

#### Result Item Design
```
Layout: Flex, gap-12px
Icon: 20px, --text-secondary
Title: text-sm, font-weight: 500
Subtitle: text-xs, --text-secondary
Shortcut: Right-aligned, kbd style

Selected State:
  - Background: --bg-accent-subtle
  - Border-left: 3px brand color
```

#### Keyboard Navigation
```
↑/↓: Navigate results
Enter: Select
Esc: Close
Cmd+Number: Quick select
```

### 5.2 Breadcrumb Navigation

```
Layout: Horizontal, below header
Items: Home > Workspace > Project > Page

Design:
  - Home: House icon
  - Separator: ChevronRight (16px)
  - Current page: Bold, no link
  - Previous: Link style

Dropdown:
  - Truncated items show "..."
  - Click to show dropdown with full path
```

### 5.3 Recent Items Quick Access

```
Location: Sidebar section
Design:
  - Collapsible section
  - Max 5 items
  - Each: Icon + Name + Pin option
  - Hover: Show "x" to remove

Items:
  - Recently viewed projects
  - Recently edited tasks
  - Pinned items persist
```

### 5.4 Collapsible Sidebar Sections

```
Behavior:
  - Chevron to expand/collapse
  - State persisted in localStorage
  - Smooth height animation

Sections:
  - Workspace
  - Projects (with count badge)
  - Views
  - Recent
  - Favorites
```

### 5.5 Keyboard Shortcuts Help

#### Trigger
```
Keyboard: Cmd/Ctrl + /
Menu: Help > Keyboard Shortcuts
```

#### Modal Design
```
Title: "Keyboard Shortcuts"
Search: Filter shortcuts

Categories:
  - Navigation
  - Task Management
  - View Controls
  - General

Shortcut Display:
  - Action name (left)
  - Key combination (right, kbd style)
```

#### Key Combination Style
```
Background: --bg-layer-1
Border: 1px solid --border-subtle
Border-radius: --radius-sm
Padding: 2px 6px
Font: font-mono, text-xs
```

### 5.6 Mobile Navigation Drawer

```
Trigger: Hamburger menu (top-left)
Animation: Slide in from left (300ms ease-out)
Backdrop: Fade in, clickable to close

Content:
  - User profile card
  - Workspace switcher
  - Main navigation
  - Recent items
  - Settings link

Swipe: Right-to-left to close
```

---

## 6. Theme & Styling

### 6.1 Dark Mode Improvements

#### Current Issues
- Some contrast ratios too low
- Inconsistent shadow usage
- Missing hover states

#### Improvements
```css
/* Enhanced dark mode backgrounds */
--dark-canvas: #0a0a0a;
--dark-surface: #141414;
--dark-elevated: #1a1a1a;
--dark-layer: #262626;

/* Improved contrast ratios */
--dark-text-primary: rgba(255, 255, 255, 0.95);   /* 15:1 */
--dark-text-secondary: rgba(255, 255, 255, 0.70); /* 7:1 */
--dark-text-tertiary: rgba(255, 255, 255, 0.50);  /* 4.5:1 */

/* Subtle glow instead of shadows */
--dark-shadow-sm: 0 0 8px rgba(255, 255, 255, 0.04);
--dark-shadow-md: 0 0 16px rgba(255, 255, 255, 0.06);
--dark-shadow-lg: 0 0 32px rgba(255, 255, 255, 0.08);
```

### 6.2 High Contrast Mode

```css
/* For accessibility */
@media (prefers-contrast: high) {
  --border-subtle: rgba(255, 255, 255, 0.4);
  --border-strong: rgba(255, 255, 255, 0.6);
  --text-secondary: rgba(255, 255, 255, 0.85);
  --focus-ring: 3px solid currentColor;
}

/* Manual toggle option */
[data-theme="high-contrast"] {
  /* High contrast overrides */
}
```

### 6.3 System Preference Detection

```typescript
// next-themes implementation
import { ThemeProvider } from 'next-themes';

<ThemeProvider
  attribute="data-theme"
  defaultTheme="system"
  enableSystem
  themes={['light', 'dark', 'high-contrast']}
>
  {children}
</ThemeProvider>
```

### 6.4 Theme Transitions

```css
/* Smooth theme switching */
* {
  transition: background-color 200ms ease-out,
              border-color 200ms ease-out,
              color 150ms ease-out;
}

/* Disable transitions during page load */
.preload * {
  transition: none !important;
}
```

### 6.5 Custom Theme Builder (Enterprise)

```
Features:
  - Primary color picker
  - Border radius slider
  - Font family selection
  - Density setting (compact/comfortable)
  
Preview:
  - Live preview of changes
  - Component showcase
  
Export:
  - CSS variables
  - Theme config JSON
```

### 6.6 Micro-interactions

#### Button Hover
```css
.button {
  transition: transform 150ms ease-out,
              box-shadow 150ms ease-out;
}

.button:hover {
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
}

.button:active {
  transform: translateY(0);
  transition-duration: 50ms;
}
```

#### Input Focus
```css
.input {
  transition: border-color 150ms ease-out,
              box-shadow 150ms ease-out;
}

.input:focus {
  border-color: var(--brand-500);
  box-shadow: 0 0 0 3px var(--brand-100);
}
```

#### Card Hover
```css
.card {
  transition: transform 200ms ease-out,
              box-shadow 200ms ease-out;
}

.card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-lg);
}
```

#### Loading States
```css
.skeleton {
  background: linear-gradient(
    90deg,
    var(--bg-layer-1) 25%,
    var(--bg-layer-2) 50%,
    var(--bg-layer-1) 75%
  );
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
}

@keyframes shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}
```

---

## 7. Mobile Responsiveness

### 7.1 Breakpoint Strategy

```css
/* Mobile-first approach */
--breakpoint-sm: 640px;   /* Large phones */
--breakpoint-md: 768px;   /* Tablets */
--breakpoint-lg: 1024px;  /* Small laptops */
--breakpoint-xl: 1280px;  /* Desktops */
--breakpoint-2xl: 1536px; /* Large screens */
```

### 7.2 Touch-Friendly Controls

```css
/* Minimum touch target */
.touch-target {
  min-width: 44px;
  min-height: 44px;
}

/* Larger touch targets for primary actions */
.touch-target-lg {
  min-width: 56px;
  min-height: 56px;
}

/* Spacing between touch targets */
.touch-group > * + * {
  margin-left: 8px;
}
```

### 7.3 Swipe Gestures

```typescript
// Using react-swipeable or similar
interface SwipeConfig {
  onSwipedLeft: () => void;   // Close drawer, next item
  onSwipedRight: () => void;  // Open drawer, previous item
  onSwipedUp: () => void;     // Expand, reveal more
  onSwipedDown: () => void;   // Collapse, refresh
}

// Common gestures
const gestures = {
  // Task list: Swipe right to complete
  taskItem: {
    right: { action: 'complete', color: 'green', icon: Check },
    left: { action: 'delete', color: 'red', icon: Trash },
  },
  
  // Sidebar: Swipe right to open
  sidebar: {
    right: { action: 'open' },
  },
  
  // Modal: Swipe down to close
  modal: {
    down: { action: 'close' },
  },
};
```

### 7.4 Mobile Navigation Drawer

```
Width: 85% of screen (max 320px)
Animation: Slide in from left (300ms ease-out)
Backdrop: Fade in, close on tap

Sections:
  1. User profile (avatar, name, email)
  2. Workspace switcher
  3. Main navigation (icons + labels)
  4. Recent projects
  5. Settings & help

Swipe to close: Left gesture anywhere
```

### 7.5 Responsive Layout Patterns

#### Dashboard
```
Desktop (lg+): Multi-column grid, all widgets visible
Tablet (md): 2-column grid, stacked widgets
Mobile (<md): Single column, collapsible sections
```

#### Project Board
```
Desktop: Horizontal scrollable columns
Tablet: Same, touch scroll
Mobile: 
  - Vertical list view default
  - Optional horizontal swipe between columns
  - Column selector dropdown
```

#### Forms
```
Desktop: Multi-column layouts
Tablet: 2-column where appropriate
Mobile: Single column, full-width inputs
```

### 7.6 PWA Considerations

```json
// manifest.json additions
{
  "display": "standalone",
  "orientation": "portrait-primary",
  "theme_color": "#3b82f6",
  "background_color": "#ffffff",
  "icons": [
    { "src": "/icon-192.png", "sizes": "192x192" },
    { "src": "/icon-512.png", "sizes": "512x512" }
  ]
}
```

```javascript
// Service Worker for offline support
// Cache critical assets
// Offline fallback page
```

---

## 8. Billing UI Components

### 8.1 Pricing Page

#### Layout
```
Header:
  - Page title: "Simple, transparent pricing"
  - Subtitle: "Start free, upgrade when you need"
  
Toggle:
  - Monthly / Annual
  - "Save 20%" badge on annual

Grid:
  - 4 cards (Free, Starter, Pro, Enterprise)
  - Equal height cards
  - Pro card highlighted

Comparison Table:
  - Below pricing cards
  - Sticky header on scroll
  - Feature categories
  - Expandable on mobile
```

#### Pricing Card Design
```
Container:
  - Background: --surface-primary
  - Border: 1px solid --border-subtle
  - Border-radius: --radius-2xl
  - Padding: 32px

Popular Variant:
  - Border: 2px solid --brand-500
  - Shadow: --shadow-lg + brand glow
  - "Most Popular" badge

Content:
  - Plan icon (48px)
  - Plan name (text-lg, bold)
  - Price (text-5xl)
  - Billing period (text-sm)
  - Description (text-sm)
  - Feature list
  - CTA button (full-width)
```

### 8.2 Checkout Modal

```
Container:
  - Max-width: 480px
  - Centered modal
  - Step indicator at top

Steps:
  1. Plan Selection (if not pre-selected)
  2. Team Size
  3. Payment (Lemon Squeezy embed)
  4. Confirmation

Design:
  - Clean, minimal
  - Progress bar
  - Clear CTAs
  - Secure payment indicators
```

### 8.3 Subscription Management Card

```
Container:
  - Dashboard settings section
  - Card with shadow

Content:
  - Current plan badge
  - Price and billing cycle
  - Next billing date
  - Payment method (last 4 digits)
  - Usage summary

Actions:
  - Upgrade/Downgrade
  - Cancel subscription
  - Update payment method
  - View invoices
```

### 8.4 Usage Meters

```
Design:
  - Label + current/max on left
  - Progress bar below
  - Percentage on right

Progress Bar:
  - Height: 8px
  - Border-radius: full
  - Background: --bg-layer-1
  - Fill: gradient based on usage
    * <70%: Brand color
    * 70-90%: Warning color
    * >90%: Error color

Animation: Smooth width transition on update
```

### 8.5 Invoice List

```
Table Columns:
  - Date
  - Description
  - Amount
  - Status (Paid, Pending, Failed)
  - Actions (Download PDF)

Row Design:
  - Hover: --bg-surface-2
  - Status badges with colors
  - Download icon button

Empty State:
  - "No invoices yet"
  - Icon: FileText
```

### 8.6 Upgrade Prompts

#### Inline Prompt
```
Location: Feature that requires upgrade
Design: 
  - Subtle banner
  - "Upgrade to Pro" link
  - Lock icon
```

#### Modal Prompt
```
Trigger: Attempting to use limited feature
Design:
  - Feature preview image
  - Benefits list
  - Plan comparison
  - CTA buttons
  - "Maybe later" option
```

---

## 9. Component Specifications

### 9.1 New Components to Build

#### 1. Command Palette
```typescript
interface CommandPaletteProps {
  isOpen: boolean;
  onClose: () => void;
  commands: Command[];
  recentItems?: RecentItem[];
}

interface Command {
  id: string;
  title: string;
  shortcut?: string;
  icon: React.ReactNode;
  action: () => void;
  category: string;
}
```

#### 2. Onboarding Flow
```typescript
interface OnboardingFlowProps {
  steps: OnboardingStep[];
  onComplete: () => void;
  onSkip: () => void;
  allowSkip?: boolean;
}

interface OnboardingStep {
  id: string;
  title: string;
  component: React.ComponentType;
  validate: () => boolean;
}
```

#### 3. Dashboard Widget System
```typescript
interface WidgetProps {
  id: string;
  type: WidgetType;
  title: string;
  size: WidgetSize;
  data?: any;
  onRemove?: () => void;
  onConfigure?: () => void;
}

type WidgetSize = 'small' | 'medium' | 'large' | 'wide';
type WidgetType = 'tasks' | 'activity' | 'stats' | 'sprint' | 'projects' | 'actions';
```

#### 4. Pricing Table
```typescript
interface PricingTableProps {
  plans: Plan[];
  billingCycle: 'monthly' | 'annual';
  onCycleChange: (cycle: 'monthly' | 'annual') => void;
  onSelectPlan: (plan: Plan) => void;
  currentPlan?: string;
}

interface Plan {
  id: string;
  name: string;
  description: string;
  price: number;
  annualPrice?: number;
  features: Feature[];
  isPopular?: boolean;
  ctaText: string;
}
```

#### 5. Tour/Onboarding Tooltip
```typescript
interface TourProps {
  steps: TourStep[];
  isOpen: boolean;
  onComplete: () => void;
  onSkip: () => void;
}

interface TourStep {
  target: string; // CSS selector
  title: string;
  content: string;
  placement: 'top' | 'bottom' | 'left' | 'right';
}
```

### 9.2 Component Patterns

#### Empty State Pattern
```tsx
<EmptyState
  icon={IconComponent}
  title="No items yet"
  description="Get started by creating your first item"
  action={{
    label: "Create Item",
    onClick: handleCreate,
  }}
  secondaryAction={{
    label: "Learn more",
    onClick: handleLearnMore,
  }}
/>
```

#### Loading State Pattern
```tsx
<Skeleton>
  <Skeleton.Item height={20} width="60%" />
  <Skeleton.Item height={16} width="40%" />
  <Skeleton.Item height={16} width="80%" />
</Skeleton>
```

#### Error State Pattern
```tsx
<ErrorState
  error={error}
  title="Something went wrong"
  description="We couldn't load your data"
  retry={handleRetry}
/>
```

---

## 10. Implementation Roadmap

### Phase 1: Foundation (Week 1-2)
- [ ] Update color palette and CSS variables
- [ ] Implement theme switching improvements
- [ ] Add high contrast mode
- [ ] Create animation utilities
- [ ] Update typography system

### Phase 2: Landing Page (Week 2-3)
- [ ] Build hero section with animations
- [ ] Create features grid (bento box)
- [ ] Implement pricing table
- [ ] Build FAQ accordion
- [ ] Add testimonials section
- [ ] Implement responsive layouts

### Phase 3: Onboarding (Week 3-4)
- [ ] Create onboarding flow container
- [ ] Build profile setup step
- [ ] Implement workspace creation
- [ ] Create team invitation step
- [ ] Build quick tour component
- [ ] Add progress indicator

### Phase 4: Dashboard (Week 4-5)
- [ ] Create widget system architecture
- [ ] Build base widget components
- [ ] Implement drag-and-drop
- [ ] Create widget types (tasks, activity, stats)
- [ ] Add customization modal
- [ ] Implement empty states

### Phase 5: Navigation (Week 5-6)
- [ ] Build command palette
- [ ] Implement breadcrumb navigation
- [ ] Create recent items section
- [ ] Add keyboard shortcuts modal
- [ ] Build mobile navigation drawer
- [ ] Implement swipe gestures

### Phase 6: Billing UI (Week 6-7)
- [ ] Create pricing page
- [ ] Build checkout modal
- [ ] Implement subscription management
- [ ] Create usage meters
- [ ] Build invoice list
- [ ] Add upgrade prompts

### Phase 7: Polish (Week 7-8)
- [ ] Add micro-interactions
- [ ] Implement smooth transitions
- [ ] Optimize animations for performance
- [ ] Test accessibility (WCAG)
- [ ] Mobile responsiveness audit
- [ ] Cross-browser testing

---

## 11. Accessibility Requirements

### 11.1 WCAG 2.1 AA Compliance

#### Color Contrast
- Normal text: 4.5:1 minimum
- Large text: 3:1 minimum
- UI components: 3:1 minimum

#### Keyboard Navigation
- All interactive elements focusable
- Visible focus indicators
- Logical tab order
- Skip links for navigation

#### Screen Reader Support
- Semantic HTML elements
- ARIA labels where needed
- Alt text for images
- Live regions for dynamic content

### 11.2 Motion Preferences

```css
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
```

---

## 12. Performance Guidelines

### 12.1 Animation Performance
- Use `transform` and `opacity` only
- Add `will-change` sparingly
- Use CSS animations over JS where possible
- Target 60fps

### 12.2 Loading Strategies
- Lazy load below-fold content
- Skeleton screens for perceived performance
- Progressive image loading
- Code splitting by route

### 12.3 Bundle Size
- Tree-shake unused components
- Dynamic import heavy components
- Optimize icon imports (individual vs bundle)

---

## 13. Design Tokens Reference

### Complete Token List

```css
/* Colors */
--color-*: /* All color tokens */

/* Typography */
--font-*: /* Font families */
--text-*: /* Font sizes */
--leading-*: /* Line heights */
--tracking-*: /* Letter spacing */

/* Spacing */
--space-*: /* Spacing scale */

/* Borders */
--radius-*: /* Border radius */
--border-*: /* Border colors */

/* Shadows */
--shadow-*: /* Box shadows */

/* Animation */
--duration-*: /* Durations */
--ease-*: /* Easing functions */

/* Z-index */
--z-*: /* Z-index scale */
```

---

## 14. File Structure

```
packages/ui/src/
├── components/
│   ├── command-palette/
│   │   ├── command-palette.tsx
│   │   ├── command-item.tsx
│   │   └── index.ts
│   ├── onboarding/
│   │   ├── onboarding-flow.tsx
│   │   ├── onboarding-step.tsx
│   │   └── index.ts
│   ├── dashboard/
│   │   ├── widget-container.tsx
│   │   ├── widget-grid.tsx
│   │   └── widgets/
│   │       ├── tasks-widget.tsx
│   │       ├── activity-widget.tsx
│   │       └── ...
│   ├── pricing/
│   │   ├── pricing-table.tsx
│   │   ├── pricing-card.tsx
│   │   └── index.ts
│   ├── tour/
│   │   ├── tour.tsx
│   │   ├── tour-step.tsx
│   │   └── index.ts
│   └── ...
├── hooks/
│   ├── use-theme.ts
│   ├── use-command-palette.ts
│   └── ...
└── styles/
    ├── animations.css
    └── utilities.css
```

---

## 15. Storybook Stories

Each new component should have comprehensive Storybook stories:

```typescript
// Example: CommandPalette.stories.tsx
import type { Meta, StoryObj } from '@storybook/react';
import { CommandPalette } from './command-palette';

const meta: Meta<typeof CommandPalette> = {
  title: 'Navigation/CommandPalette',
  component: CommandPalette,
  parameters: {
    layout: 'fullscreen',
  },
};

export default meta;

type Story = StoryObj<typeof CommandPalette>;

export const Default: Story = {
  args: {
    isOpen: true,
    commands: mockCommands,
  },
};

export const WithRecentItems: Story = {
  args: {
    isOpen: true,
    commands: mockCommands,
    recentItems: mockRecentItems,
  },
};

export const Empty: Story = {
  args: {
    isOpen: true,
    commands: [],
  },
};
```

---

## Conclusion

This design system provides a comprehensive foundation for transforming Hoovix into a premium SaaS product. The focus on:

1. **Modern aesthetics** inspired by Linear, Notion, and Figma
2. **Delightful interactions** with thoughtful animations
3. **Accessibility first** ensuring WCAG compliance
4. **Mobile excellence** with touch-friendly designs
5. **Performance** with optimized animations and loading

Will position Hoovix as a competitive alternative to existing project management tools while providing a foundation for future growth and enterprise features.

---

## Appendix

### A. Reference Links
- [Linear App Design](https://linear.app)
- [Notion Interface](https://notion.so)
- [Figma Design System](https://figma.com)
- [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
- [Tailwind CSS Documentation](https://tailwindcss.com)

### B. Icon Library
- **Primary**: Lucide React
- **Secondary**: Custom icons for brand-specific elements

### C. Animation Libraries
- **Primary**: Framer Motion
- **Secondary**: CSS animations for simple transitions
- **Drag & Drop**: @dnd-kit/core

### D. Testing Checklist
- [ ] Cross-browser testing (Chrome, Firefox, Safari, Edge)
- [ ] Mobile testing (iOS Safari, Android Chrome)
- [ ] Accessibility audit (axe, Lighthouse)
- [ ] Performance testing (Lighthouse 90+)
- [ ] Theme switching testing
- [ ] Keyboard navigation testing
