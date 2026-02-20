# Symphony-IR Frontend - Component Specifications

## Quick Reference

### Color Tokens
```
Primary: #3B82F6 (Blue-500)
Accent: #06B6D4 (Cyan-500)
Gradient: Cyan → Purple (#06B6D4 → #8B5CF6)
Background: #0F172A (Slate-950)
Surface: #0F172A (Slate-950)
Card: #1E293B (Slate-800)
Text Primary: #E2E8F0 (Slate-200)
Text Secondary: #94A3B8 (Slate-400)
Border: #334155 (Slate-700)
```

---

## Page Layouts

### 1. Dashboard (Default View)

**Structure:**
```
┌─────────────────────────────────────────────────┐
│ Header (Logo, Nav, Profile)                     │
├──────────┬──────────────────────────────────────┤
│ Sidebar  │                                      │
│          │  Main Content Area                   │
│          │  ┌────────────────┬──────────────┐  │
│          │  │ Input Panel    │ Output Panel │  │
│          │  │ - Task Input   │ - Live Log   │  │
│          │  │ - Variables    │ - Copy BTN   │  │
│          │  │ - Options      │ - Download   │  │
│          │  └────────────────┴──────────────┘  │
│          │  ┌────────────────────────────────┐  │
│          │  │ Metrics Preview                │  │
│          │  └────────────────────────────────┘  │
└──────────┴──────────────────────────────────────┘
```

**Key Sections:**

**Input Panel (Left 45%)**
- Background: Slate-800 with border gradient (Cyan-500 to Purple-500)
- Border-radius: 12px
- Padding: 24px
- Elements:
  - Icon + Title: "🎼 Execute Orchestration"
  - Task input textarea (full width)
  - Variables section (collapsible)
  - Advanced options (accordion)
  - Execute button (full-width, primary)

**Output Panel (Right 50%)**
- Background: Slate-800
- Border: 1px Slate-700
- Border-radius: 12px
- Padding: 24px
- Elements:
  - Summary section (status, ledger ID, resources)
  - Real-time output log (monospace, scrollable)
  - Copy all button (top-right)
  - Download session button

**Metrics Section (Full Width Below)**
- 4 cards in a row (responsive to 2 on tablet, 1 on mobile)
- Each card:
  - Icon (32px, semantic color)
  - Metric name (small text, secondary color)
  - Large number (24px, bold)
  - Trend indicator (↑/↓ arrow)

---

### 2. Orchestrator Tab

**Hero Section**
- Background: Gradient from Slate-900 to Slate-800
- Content: Title, description, status indicator
- Height: 120px
- Padding: 32px

**Main Grid**
- 2-column layout on desktop
- Single column on tablet/mobile
- Gap: 24px
- Padding: 32px

**Left Column (Input)**
- Input panel (as described above)
- Advanced section (collapsible)
  - Verbose toggle
  - Dry-run checkbox
  - Custom options

**Right Column (Live Output)**
- Output panel (as described above)
- Tabs for Output / Raw output
- Timestamp on top-left

---

### 3. Flow Tab

**Header**
- Template selector dropdown
- Status indicator
- Start/reset buttons

**Two-Panel Layout**
- **Left Panel (40%):** Tree visualization
  - Nodes styled as cards
  - Active node highlighted (Blue-500)
  - Completed nodes: Green checkmark
  - Current node: Pulse animation

- **Right Panel (60%):** Step content
  - Step title (large)
  - Description (body text)
  - Options as buttons (2-4 options)
  - Execute button at bottom

---

### 4. History Tab

**Toolbar**
- Search input (left)
- Filters: Date range, Status, Cost
- Sort options
- View toggle (table/card)

**Table View**
- Columns:
  - Timestamp (14px, secondary)
  - Task snippet (16px, primary)
  - Status badge (semantic color)
  - Duration (14px, secondary)
  - Cost (14px, secondary)
  - Actions dropdown

- Row height: 56px
- Hover: Light background lift + shadow
- Striped: Alternate Slate-800/900

**Pagination**
- Position: Bottom-right
- Items per page: 20
- Navigation: Previous, page numbers, Next

---

### 5. Settings Tab

**Sidebar Categories** (Left 20%)
- API Configuration
- Models
- Appearance
- Data & Privacy
- Advanced

**Content Area** (Right 80%)
- Section title + description
- Form inputs with labels
- Validation messages
- Save button (sticky at bottom)

---

## Component Specifications

### Header Component

```
Height: 64px
Background: Slate-800 with border-bottom 1px Slate-700
Sticky: Yes
Padding: 0 32px

Layout: 3 sections
├─ Left: Logo + Brand name (32px)
├─ Center: Navigation (hidden on mobile)
└─ Right: Theme toggle + Profile menu (36px icons)

Navigation items:
├─ Orchestrator (active indicator)
├─ Flow
├─ History
└─ Settings
```

### Sidebar Component

```
Width: 280px (desktop) / 64px (collapsed) / hidden (mobile)
Background: Slate-900
Border-right: 1px Slate-700
Padding: 16px 8px

Sections:
├─ MAIN (icon: 🎼)
│  ├─ Orchestrator
│  ├─ Flow Templates
│  └─ History
├─ TOOLS (icon: ⚙️)
│  ├─ Settings
│  └─ Documentation
└─ Toggle collapse button (bottom)

Item height: 44px
Icon + Label (8px gap)
Hover: Background Slate-800 (20%)
Active: Border-left 3px Blue-500 + bg Slate-800 (30%)
```

### Task Input Panel

```
Structure:
┌────────────────────────────────────┐
│ 🎼 Execute Orchestration           │ ← Header
├────────────────────────────────────┤
│ Describe your task...              │
│ (textarea, full-width)             │
│ 4 rows minimum                     │
├────────────────────────────────────┤
│ + Variables (0/10)                 │ ← Collapsible section
│ ├─ [Key 1] [Value 1] [X]          │
│ ├─ [Key 2] [Value 2] [X]          │
│ └─ [+ Add variable]                │
├────────────────────────────────────┤
│ ⚙️ Advanced Options (collapsed)    │ ← Accordion
│ ├─ ☐ Verbose output               │
│ ├─ ☐ Dry run                      │
│ ├─ ☐ Disable compiler             │
│ └─ ☐ Disable IR pipeline          │
├────────────────────────────────────┤
│ [Execute Orchestration] (full-w)   │
└────────────────────────────────────┘

Input field:
- Background: Slate-700
- Border: 1px Slate-600
- Focus: Border Blue-500, shadow 0 0 0 3px rgba(59,130,246,0.1)
- Padding: 12px
- Border-radius: 8px
- Placeholder: Slate-500

Button (Execute):
- Width: 100%
- Height: 44px
- Background: Blue-500
- Hover: Blue-600, lift 2px
- Active: Blue-700, no lift
- Border-radius: 8px
```

### Output Panel

```
Structure:
┌─────────────────────────────────────┐
│ [Copy] [Download]                   │ ← Top actions
├─────────────────────────────────────┤
│ Status: ✓ Complete                  │ ← Summary
│ Ledger ID: [uuid] [copy icon]       │
│ Resources: 2,450 tokens | $0.0245   │
├─────────────────────────────────────┤
│ [Output] [Raw Output]               │ ← Tabs
├─────────────────────────────────────┤
│ $ Running phase: Analysis           │
│ ✓ Agent (architect) complete       │
│ ... (scrollable log)                │
│ [loading indicator] Processing...   │
└─────────────────────────────────────┘

Output style:
- Font: JetBrains Mono, 13px
- Line-height: 1.6
- Background: Slate-900 (inside)
- Color: Slate-200 (main), Green (success), Red (error)
- Padding: 16px
- Max-height: 600px, scrollable
```

### Metrics Card

```
Standard Metrics Card:
┌──────────────────────┐
│ 📊 Metric Name       │
│                      │
│ 2,450                │
│ tokens used          │
│                      │
│ ↑ +12% vs avg        │
└──────────────────────┘

Styles:
- Background: Slate-800
- Border: 1px Slate-700
- Border-radius: 12px
- Padding: 20px
- Icon: 32px, semantic color
- Metric name: 12px, Slate-400
- Big number: 28px bold, Slate-200
- Trend: 12px, Green if positive
- Hover: Lift 4px, shadow expand

Grid Layout:
- Desktop (>1024px): 4 columns
- Tablet (640-1024px): 2 columns
- Mobile (<640px): 1 column
- Gap: 16px
```

### Tabs Component

```
┌────────────────────────────────────┐
│ [Output] [Raw Output] [Metrics]    │
├────────────────────────────────────┤
│ Content for active tab             │
└────────────────────────────────────┘

Tab styles:
- Height: 48px (including content)
- Padding: 12px 16px
- Background: Transparent
- Text: Slate-400 (inactive), Slate-200 (active)
- Border-bottom: 2px Blue-500 (active), transparent (inactive)
- Hover: Slate-300
- Font-weight: 500
- Transition: All 200ms ease

Active indicator:
- 2px solid Blue-500 border-bottom
- Smooth slide animation between tabs
```

### Session History Table

```
┌─────────┬──────────┬────────┬────────┬───────┬────────┐
│ Time    │ Task     │ Status │ Duration│ Cost  │ Actions│
├─────────┼──────────┼────────┼────────┼───────┼────────┤
│ 2:45 PM │ Design   │ ✓Done  │ 2m 34s │ $0.02 │ ▼      │
│ 1:22 PM │ Review   │ ✓Done  │ 1m 12s │ $0.01 │ ▼      │
│ 12:51 AM│ Refactor │ ✗Error │ 45s    │ $0.00 │ ▼      │
└─────────┴──────────┴────────┴────────┴───────┴────────┘

Row height: 56px
Column widths: Flexible
Hover: Background Slate-800 (light), shadow 0 2px 8px
Striped: Alternate Slate-900/800

Cell padding: 12px 16px
Text sizes: 14px (main), 12px (secondary)
Status badge: Semantic colors with icons
Actions: Dropdown menu or inline buttons

Pagination:
- 20 items per page
- Bottom-right position
- Previous | 1 2 3 ... N | Next
```

### Status Badge

```
Success:
┌──────────┐
│ ✓ Done   │
└──────────┘
BG: Green-500/20%, Text: Green-500

Running:
┌──────────┐
│ ⟳ Running│
└──────────┘
BG: Blue-500/20%, Text: Blue-500
Animation: Rotate 360° / 2s

Error:
┌──────────┐
│ ✗ Error  │
└──────────┘
BG: Red-500/20%, Text: Red-500

Pending:
┌──────────┐
│ ⊙ Pending│
└──────────┘
BG: Amber-500/20%, Text: Amber-500
```

### Forms & Inputs

```
Text Input:
┌────────────────────────┐
│ Label                  │
│ [placeholder text]     │ ← Slate-700 bg, Slate-600 border
│ Helper text (optional) │
└────────────────────────┘

Height: 40px (medium)
Padding: 12px
Border: 1px Slate-600
Border-radius: 8px
Focus: Border Blue-500, shadow 0 0 0 3px rgba(59,130,246,0.1)
Disabled: Opacity 50%, cursor not-allowed

Textarea:
- Min-height: 120px
- Max-height: 600px
- Resize: Vertical only
- Same focus states as text input

Select/Dropdown:
- Same dimensions as text input
- Arrow icon right-aligned
- Hover: Border Slate-500
- Focus: Same as text input

Checkbox:
- Size: 20x20px
- Border-radius: 4px
- Checked: Background Blue-500
- Hover: Border Blue-400
- Accent color: Blue-500

Toggle Switch:
- Width: 44px, Height: 24px
- Border-radius: 12px
- Background: Slate-600 (off), Blue-500 (on)
- Circle: White, 20x20px, translates
- Transition: 200ms ease
```

### Modals & Dialogs

```
┌─────────────────────────────────────┐
│ Dialog Title                    [×]  │
├─────────────────────────────────────┤
│                                     │
│ Content area                        │
│                                     │
├─────────────────────────────────────┤
│              [Cancel]  [Confirm]    │
└─────────────────────────────────────┘

Overlay:
- Background: rgba(0, 0, 0, 0.7)
- Backdrop-filter: blur(2px) (optional)

Modal:
- Background: Slate-800
- Border: 1px Slate-700
- Border-radius: 12px
- Width: 90% (mobile), 600px (desktop)
- Max-height: 90vh, scrollable
- Padding: 24px
- Box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.5)

Animation:
- Backdrop: Fade in 200ms
- Modal: Scale 0.95 → 1.0, fade in 200ms
- Exit: Reverse, 150ms

Header:
- Font-size: 20px (H3)
- Font-weight: 600
- Close button: Icon only, 24px
- Margin-bottom: 16px

Footer:
- Margin-top: 24px
- Button gap: 12px
- Justify: flex-end
```

### Empty States

```
┌─────────────────────────┐
│                         │
│       📁               │
│                         │
│  No Results             │
│  Try adjusting filters  │
│                         │
│  [Clear Filters] button │
│                         │
└─────────────────────────┘

Icon: 64px, Slate-600
Title: 18px, bold, Slate-300
Description: 14px, Slate-400
CTA: Secondary button or link

Centered in container
Padding: 48px 24px
Background: Gradual from Slate-900 to Slate-800 (optional)
```

### Notifications/Toasts

```
┌────────────────────────────────────┐
│ ✓ Execution started successfully   │ [×]
└────────────────────────────────────┘

Styles by type:
- Success: Green-500 bg/20%, Green-500 text, Green-500 left border
- Error: Red-500 bg/20%, Red-500 text, Red-500 left border
- Warning: Amber-500 bg/20%, Amber-500 text, Amber-500 left border
- Info: Blue-500 bg/20%, Blue-500 text, Blue-500 left border

Position: Top-right corner
Margin: 16px from edge
Border-radius: 8px
Padding: 12px 16px
Icon + Text format (8px gap)
Left border: 4px
Auto-dismiss: 5 seconds (or manual)
Animation: Slide in from right 300ms, slide out 200ms

Stack: Max 3 visible, queue others
```

---

## Interaction Patterns

### Button Interactions
- Default → Hover (lift 2px, shadow expand)
- Hover → Active (no lift, shadow compress)
- Active → Released (smooth return to hover state)
- Disabled → No interaction, opacity 50%

### Form Interactions
- Focus: Immediate border color change + shadow
- Validation: Real-time feedback with icons
- Success: Green checkmark + confirmation message
- Error: Red outline + error message below

### Loading States
- Initial: Skeleton or spinner
- Loading: Pulse animation or spinning icon
- Complete: Fade out loader, fade in content
- Error: Show error message + retry button

### Modal Interactions
- Open: Backdrop fade + modal scale up
- Close: Reverse animation
- Click outside: Auto-close (optional for confirmation modals)
- Keyboard: ESC to close

---

## Accessibility Requirements

- All interactive elements: Keyboard accessible (Tab order)
- Focus indicators: Always visible (2px outline or ring)
- Color alone: Never sole indicator (use icons/text)
- Contrast: All text >= 4.5:1
- ARIA labels: On all form controls
- Semantic HTML: Proper headings, buttons, links
- Reduced motion: Respect prefers-reduced-motion

