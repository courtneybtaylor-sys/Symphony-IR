# Symphony-IR SaaS Frontend Design System

## Executive Overview

Symphony-IR is being redesigned as a premium SaaS platform with a focus on **enterprise-grade AI orchestration**. The new design emphasizes clarity, power, and sophistication while maintaining accessibility and usability for developers and technical teams.

**Target Audience:** Developers, DevOps engineers, AI researchers, enterprises

**Design Philosophy:** Professional, modular, data-centric with subtle elegance

---

## Color Palette

### Primary Colors
- **Brand Blue (Primary):** `#3B82F6` - Primary actions, focus states, brand identity
- **Electric Cyan (Accent):** `#06B6D4` - Highlights, data visualization, active states
- **Gradient Accent:** `#06B6D4` → `#8B5CF6` (Cyan to Purple) - Backgrounds, feature highlights

### Neutrals
- **Off-Black (Background):** `#0F172A` - Dark theme primary background
- **Slate-900 (Surface):** `#0F172A` - Secondary surfaces
- **Slate-800 (Cards):** `#1E293B` - Card backgrounds, containers
- **Slate-700 (Border):** `#334155` - Borders, dividers
- **Slate-400 (Secondary Text):** `#94A3B8` - Secondary content
- **Slate-200 (Primary Text):** `#E2E8F0` - Primary text
- **White:** `#FFFFFF` - Maximum contrast text, icons

### Semantic Colors
- **Success (Green):** `#10B981` - Completion, success states
- **Warning (Amber):** `#F59E0B` - Warnings, caution states
- **Error (Red):** `#EF4444` - Errors, critical alerts
- **Info (Blue):** `#3B82F6` - Information, secondary actions

---

## Typography

### Font Stack
- **Headings & UI:** Inter (sans-serif)
- **Body Text:** Inter (sans-serif)
- **Monospace:** JetBrains Mono or Fira Code (for code/technical content)

### Typographic Scale

| Element | Font Size | Font Weight | Line Height | Letter Spacing |
|---------|-----------|------------|-----------|----------------|
| H1 (Page Title) | 48px / 3rem | 700 Bold | 1.2 | -0.02em |
| H2 (Section) | 32px / 2rem | 600 SemiBold | 1.3 | -0.01em |
| H3 (Subsection) | 24px / 1.5rem | 600 SemiBold | 1.4 | 0 |
| H4 (Label) | 16px / 1rem | 600 SemiBold | 1.5 | 0.01em |
| Body Large | 16px / 1rem | 400 Regular | 1.6 | 0 |
| Body | 14px / 0.875rem | 400 Regular | 1.6 | 0 |
| Body Small | 12px / 0.75rem | 400 Regular | 1.5 | 0.01em |
| Caption | 12px / 0.75rem | 500 Medium | 1.4 | 0.02em |
| Mono | 13px / 0.8125rem | 400 Regular | 1.5 | 0 |

---

## Layout & Spacing

### 8px Grid System
All spacing follows an 8px grid for consistency and scalability.

**Spacing Scale:**
- xs: 4px
- sm: 8px
- md: 16px
- lg: 24px
- xl: 32px
- 2xl: 48px
- 3xl: 64px

### Components Spacing
- **Section padding:** 32px horizontal, 24px vertical
- **Card padding:** 24px
- **Button padding:** 12px 16px (touch target: 44px minimum)
- **Gap between elements:** 16px default
- **Group gaps:** 8px

---

## Component Architecture

### 1. **Header & Navigation**
- **Height:** 64px
- **Background:** Slate-800 with subtle border bottom
- **Content:** Logo left, nav items center, profile/settings right
- **Sticky:** Yes, with glass morphism effect on scroll

### 2. **Sidebar Navigation**
- **Width:** 280px (collapsible to 64px)
- **Background:** Slate-900 with gradient accent on active items
- **Border:** Right border 1px Slate-700
- **Sections:** Orchestrator, Flow, History, Settings
- **Item height:** 44px
- **Icon + Label format**

### 3. **Main Content Area**
- **Max-width:** Full with sidebar
- **Padding:** 32px
- **Background:** Slate-900
- **Grid system:** Flex for vertical, CSS Grid for complex layouts

### 4. **Task Execution Panel**
- **Background:** Gradient card (Slate-800 to Slate-800 with border)
- **Border:** 1px gradient (Cyan to Purple)
- **Rounded:** 12px
- **Shadow:** 0 20px 25px -5px rgba(0, 0, 0, 0.3)
- **Padding:** 24px
- **Elements:**
  - Title + Icon (top)
  - Textarea for task description
  - Variable input section
  - Options accordion
  - Execute button (full-width, primary)

### 5. **Output Panel**
- **Background:** Slate-800
- **Monospace display:** Code blocks with syntax highlighting
- **Real-time streaming:** Gradient left border indicator (Cyan to Purple)
- **Copy button:** Top-right corner
- **Download option:** For session JSON

### 6. **Metrics Dashboard**
- **Grid layout:** 2-4 columns (responsive)
- **Card style:** Minimal borders, subtle shadows
- **Icons:** Color-coded by metric type
- **Stat display:** Large number + small label
- **Trend indicator:** Up/down arrow with color
- **Background:** Slate-800
- **Border:** 1px Slate-700

### 7. **Session History**
- **Table/List view:** Clean rows with hover states
- **Columns:** Timestamp, Task snippet, Status, Duration, Cost, Actions
- **Filters:** Top toolbar with date range, status
- **Pagination:** 20 items per page
- **Row height:** 56px
- **Hover effect:** Slight background lift + shadow

### 8. **Buttons**

**Primary Button**
- Background: Blue-500 (#3B82F6)
- Text: White
- Height: 44px
- Padding: 12px 20px
- Border-radius: 8px
- Hover: Blue-600, slight lift, enhanced shadow
- Active: Blue-700, pressed state
- Disabled: Slate-500, opacity 50%

**Secondary Button**
- Background: Transparent
- Border: 1px Slate-600
- Text: Slate-200
- Hover: Background Slate-700
- Active: Border color Blue-500

**Tertiary Button**
- Background: Transparent
- Text: Blue-400
- Hover: Underline + lighter
- Active: Blue-300

**Ghost/Icon Button**
- Background: Transparent
- Icon-only: 36px x 36px
- Hover: Background Slate-700/20%
- Rounded: 8px

### 9. **Input Fields**
- **Background:** Slate-700
- **Border:** 1px Slate-600
- **Border-radius:** 8px
- **Padding:** 12px 12px
- **Focus:** Border Blue-500, box-shadow 0 0 0 3px rgba(59, 130, 246, 0.1)
- **Placeholder:** Slate-500
- **Text:** Slate-200
- **Height:** 40px (md), 36px (sm)

### 10. **Cards**
- **Background:** Slate-800
- **Border:** 1px Slate-700
- **Border-radius:** 12px
- **Padding:** 24px
- **Box-shadow:** 0 4px 6px -1px rgba(0, 0, 0, 0.2)
- **Hover:** Slight lift, enhanced shadow

### 11. **Tabs**
- **Background:** Slate-800
- **Border-bottom:** 2px Slate-700
- **Active indicator:** Blue-500 underline
- **Padding:** 16px 24px
- **Text:** Slate-400 → Slate-200 on active
- **Hover:** Slate-300

### 12. **Badges**
- **Padding:** 6px 12px
- **Border-radius:** 6px
- **Font-size:** 12px
- **Font-weight:** 500
- **Success:** Green bg, Green text darker
- **Warning:** Amber bg, Amber text darker
- **Error:** Red bg, Red text white
- **Info:** Blue bg, Blue text white
- **Default:** Slate-700 bg, Slate-300 text

### 13. **Modals & Dialogs**
- **Background:** Slate-800
- **Border:** 1px Slate-700
- **Border-radius:** 12px
- **Shadow:** 0 20px 25px -5px rgba(0, 0, 0, 0.5)
- **Backdrop:** rgba(0, 0, 0, 0.7)
- **Padding:** 24px
- **Max-width:** 600px (responsive)

---

## Visual Hierarchy

### Emphasis Levels
1. **High Emphasis:** Blue-500 text, large 32px+, bold weight
2. **Medium Emphasis:** Slate-200 text, 16px, semi-bold
3. **Low Emphasis:** Slate-400 text, 14px, regular
4. **Disabled:** Slate-500 text, opacity 50%

### Interactive States
- **Default:** Base color
- **Hover:** Lighter shade + subtle lift (1-2px)
- **Active/Pressed:** Darker shade, no lift
- **Disabled:** Reduced opacity, no pointer
- **Focus:** Outline or box-shadow (accessibility)

---

## Animations & Transitions

### Timing
- **Quick interactions:** 200ms ease-out (buttons, hovers)
- **Medium transitions:** 300ms ease-in-out (panels, modals)
- **Slow animations:** 500ms ease-in-out (page transitions, major reveals)

### Effects
- **Fade:** Opacity 0 → 1
- **Slide:** Transform translateY/X
- **Scale:** Transform scale
- **Lift:** Transform translateY(-2px)
- **Color shift:** Background-color transitions

### Specific Animations
- **Button hover:** Lift 2px + shadow expand
- **Card hover:** Lift 4px + shadow expand
- **Tab change:** Fade + slide underline
- **Modal appear:** Fade backdrop + scale content
- **Toast messages:** Slide in from top + fade out

---

## Icons & Imagery

### Icon System
- **Size scale:** 16px, 20px, 24px, 32px
- **Stroke width:** 2px (consistent)
- **Colors:** Inherit from text color, can be override with semantic colors
- **Library:** Lucide React or Heroicons
- **Spacing:** 8px gap between icon and text

### Illustrations
- **Style:** Minimalist line-art or geometric
- **Accent colors:** Cyan and Purple gradients
- **Usage:** Empty states, error pages, feature highlights
- **Positioning:** Centered or aligned left/right

---

## Responsive Design

### Breakpoints
- **Mobile:** < 640px
- **Tablet:** 640px - 1024px
- **Desktop:** 1024px - 1920px
- **Wide:** > 1920px

### Layout Adjustments
- **Mobile:** Single column, sidebar collapse to hamburger
- **Tablet:** 2-column grids, sidebar toggleable
- **Desktop:** Full sidebar, 3+ column grids, expanded modals
- **Wide:** Optional sidebar collapse, 4+ column grids

### Touch Targets
- **Minimum:** 44px x 44px
- **Optimal:** 48px x 48px
- **Spacing:** 8px minimum between interactive elements

---

## Dark Theme Implementation

### Approach
- **Default:** Dark theme (Slate palette)
- **Toggle:** Settings menu or system preference
- **Contrast:** All text meets WCAG AA standards (4.5:1)
- **Semantic tokens:** CSS variables for easy switching

### CSS Variables (In globals.css)
```css
:root {
  --color-primary: #3B82F6;
  --color-accent: #06B6D4;
  --color-success: #10B981;
  --color-warning: #F59E0B;
  --color-error: #EF4444;
  --color-info: #3B82F6;
  --color-background: #0F172A;
  --color-surface: #0F172A;
  --color-card: #1E293B;
  --color-border: #334155;
  --color-text-primary: #E2E8F0;
  --color-text-secondary: #94A3B8;
  --color-text-tertiary: #64748B;
}
```

---

## Accessibility Standards

### WCAG 2.1 AA Compliance
- **Contrast:** Minimum 4.5:1 for text
- **Touch targets:** 44px minimum
- **Focus indicators:** Always visible
- **Keyboard navigation:** Full support
- **Screen readers:** Proper ARIA labels

### Specific Requirements
- **Form labels:** Associated with inputs
- **Error messages:** Clear, linked to fields
- **Images:** Alt text for all non-decorative
- **Color:** Not sole indicator (use icons/text)
- **Motion:** Reduced motion support

---

## Component States

### Data Loading
- **Initial:** Empty state with icon + message
- **Loading:** Skeleton loaders or spinner
- **Success:** Data display + optional toast
- **Error:** Error state with retry option
- **Empty:** Empty state specific to context

### Execution States
- **Idle:** Default state, action buttons enabled
- **Running:** Disabled input, spinner, progress indicator
- **Complete:** Results display, copy/export options
- **Error:** Error message, retry button
- **Cancelled:** Message + history link

---

## Page-Specific Layouts

### Orchestrator Tab
- **Header:** Title + description
- **Layout:** 2-column (Input panel left, Live output right)
- **Input Panel:** Task description, variables, options
- **Output Panel:** Real-time streaming, copy button
- **Bottom:** Metrics preview

### Flow Tab
- **Header:** Title + template selector
- **Layout:** Decision tree visualization
- **Left Panel:** Step descriptions, options
- **Center:** Visual flow diagram
- **Right Panel:** Step details, execute button

### History Tab
- **Header:** Title + filters
- **Layout:** Table/list of sessions
- **Filters:** Date range, status, cost range
- **Row actions:** View, download, delete, retry
- **Detail view:** Modal with full session data

### Settings Tab
- **Header:** Title
- **Layout:** Vertical sections
- **Sections:** API keys, Models, Appearance, Data
- **Inputs:** Text fields, toggles, dropdowns
- **Action:** Save button at bottom

---

## Brand Consistency

### Logo & Wordmark
- **Primary:** Full logo (icon + Symphony-IR text)
- **Icon:** Music notation symbol
- **Color:** Blue-500 on dark backgrounds
- **Minimum size:** 32px
- **Clear space:** Logo width on all sides

### Brand Voice
- **Professional:** Technical, authoritative
- **Approachable:** Clear, understandable explanations
- **Innovative:** Modern, forward-thinking language

### Copywriting Guidelines
- **Call-to-action:** Action-oriented verbs (Execute, Deploy, Analyze)
- **Errors:** Helpful, non-blaming language
- **Success:** Celebratory, confirmatory tone
- **Microcopy:** Concise, helpful hints in labels and placeholders

---

## Implementation Priority

### Phase 1 (Core UI)
- [ ] Header & navigation
- [ ] Sidebar
- [ ] Main content area
- [ ] Button components
- [ ] Input fields
- [ ] Cards

### Phase 2 (Features)
- [ ] Task execution panel
- [ ] Output panel
- [ ] Metrics dashboard
- [ ] Session history
- [ ] Tabs

### Phase 3 (Polish)
- [ ] Animations & transitions
- [ ] Responsive design
- [ ] Accessibility audit
- [ ] Dark mode refinement
- [ ] Performance optimization

---

## Testing Checklist

- [ ] **Visual**: All colors meet contrast requirements
- [ ] **Responsive**: Works on all breakpoints
- [ ] **Accessibility**: Keyboard navigation, screen readers
- [ ] **Performance**: Fast load times, smooth animations
- [ ] **Browser**: Chrome, Firefox, Safari, Edge
- [ ] **Mobile**: iOS Safari, Android Chrome
- [ ] **A11y**: WCAG 2.1 AA compliance

---

## Future Enhancements

1. **Light theme variant** with adjusted palette
2. **Custom theme builder** in settings
3. **Data visualization library** integration (Recharts)
4. **Real-time collaboration** indicators
5. **AI-powered suggestions** in UI

