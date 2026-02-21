# Symphony-IR SaaS Frontend - Design Vision & Roadmap

## Design Vision Statement

Symphony-IR is being reimagined as a **premium, enterprise-grade AI orchestration platform** with a modern SaaS aesthetic. The design emphasizes:

- **Clarity**: Information architecture is intuitive and scannable
- **Power**: Advanced features are accessible but not overwhelming
- **Sophistication**: Professional, polished interactions and visual hierarchy
- **Efficiency**: Workflows are optimized for developer productivity
- **Accessibility**: WCAG 2.1 AA compliant, keyboard-navigable

The visual language draws inspiration from enterprise platforms like Vercel, Supabase, and Braintrust, featuring:
- Deep slate/dark backgrounds (#0F172A, #1E293B)
- Vibrant primary blue (#3B82F6) with cyan accents (#06B6D4)
- Gradient highlights (Cyan → Purple) for premium feel
- Clean typography and generous whitespace
- Smooth, purposeful animations

---

## Color Palette Overview

### Primary Brand Colors

| Color | Hex | Use Case | Contrast |
|-------|-----|----------|----------|
| **Brand Blue** | #3B82F6 | Primary buttons, links, focus states, active indicators | 4.5:1 ✓ |
| **Cyan Accent** | #06B6D4 | Highlights, secondary accents, data vis | 5.2:1 ✓ |
| **Purple** | #8B5CF6 | Gradient partner, premium feel | 3.8:1 ✓ |

### Supporting Colors

| Color | Hex | Use Case |
|-------|-----|----------|
| **Success Green** | #10B981 | Completion, success badges, valid states |
| **Warning Amber** | #F59E0B | Warnings, caution states |
| **Error Red** | #EF4444 | Errors, destructive actions |
| **Info Blue** | #3B82F6 | Information alerts, secondary actions |

### Neutral Palette (Slate)

| Level | Light | Dark | Use Case |
|-------|-------|------|----------|
| **Darkest** | #0F172A | — | Primary background |
| **Dark 1** | #0F172A | — | Secondary surfaces |
| **Dark 2** | #1E293B | — | Card backgrounds |
| **Dark 3** | #334155 | — | Borders, dividers |
| **Light 1** | #94A3B8 | — | Secondary text |
| **Light 2** | #E2E8F0 | — | Primary text |
| **Lightest** | #FFFFFF | — | Maximum contrast, icons |

---

## Key Design Patterns

### 1. Gradient Borders (Premium Feel)
- Used on primary input panels and feature cards
- Gradient: Cyan (#06B6D4) → Purple (#8B5CF6)
- Adds premium, modern aesthetic without being distracting

### 2. Card Hierarchy
- **Primary cards**: Gradient border, elevated shadow, interactive
- **Secondary cards**: Solid border, subtle shadow, informational
- **Tertiary elements**: Border-less, minimal styling

### 3. Interactive Feedback
- **Hover**: Lift 2-4px, shadow expansion, slight color shift
- **Active**: Color intensification, no lift (pressed feeling)
- **Focus**: Ring outline (3px) with 10% opacity
- **Disabled**: 50% opacity, no pointer interaction

### 4. Data Visualization
- **Metrics**: Large bold numbers, semantic color indicators, trend arrows
- **Charts**: Cyan primary color, grid lines in Slate-700
- **Tables**: Striped rows (Slate-900/800), hover highlights, sortable headers

### 5. Empty States
- Large icon (64px, Slate-600)
- Primary message (18px, bold, Slate-300)
- Helper text (14px, Slate-400)
- Optional CTA button
- Centered in container with padding

---

## Layout Architecture

### Header Bar (64px)
```
[Logo]         [Navigation]          [Theme] [Profile]
Left           Center (hidden mobile) Right
```

### Sidebar (280px desktop / 64px collapsed)
```
MAIN
├─ 🎼 Orchestrator
├─ 🗺️  Flow
├─ 📋 History
TOOLS
├─ ⚙️  Settings
└─ 📖 Documentation

[Collapse icon] (bottom)
```

### Main Content (Responsive)
```
Desktop (>1024px):
┌────────────────────────────────────┐
│ Two-column grid                    │
│ ├─ Input Panel (45%)               │
│ └─ Output Panel (50%)              │
│ Full-width Metrics below           │

Tablet (640-1024px):
┌────────────────────────────────────┐
│ Stacked layout                     │
│ ├─ Input Panel (full)              │
│ ├─ Output Panel (full)             │
│ └─ Metrics (2-column grid)         │

Mobile (<640px):
┌──────────────────┐
│ Single column    │
│ ├─ Input Panel   │
│ ├─ Output Panel  │
│ └─ Metrics (1)   │
└──────────────────┘
```

---

## Component Library Overview

### Foundation Components
- **Button** (4 variants: primary, secondary, tertiary, ghost)
- **Input** (text, textarea, select)
- **Card** (with border options: default, gradient)
- **Badge** (5 semantic types)
- **Tabs** (with animated underline)
- **Modal** (with overlay, animations)

### Layout Components
- **Header** (sticky, with nav)
- **Sidebar** (collapsible, with icons)
- **Grid** (responsive, configurable columns)
- **Container** (max-width wrapper)

### Feature Components
- **TaskInputPanel** (textarea, variables, options)
- **OutputPanel** (streaming log viewer, copy/download)
- **MetricsCard** (icon, number, trend)
- **SessionTable** (with filters, pagination)
- **StatusBadge** (success/error/running/pending)

### Feedback Components
- **Toast** (auto-dismiss notifications)
- **Spinner** (loading indicator)
- **Skeleton** (content placeholders)
- **EmptyState** (no data fallback)

---

## Animation & Microinteractions

### Standard Timings
- **Quick**: 200ms (button hover, focus)
- **Standard**: 300ms (tab changes, modals)
- **Slow**: 500ms (page transitions, reveals)

### Animation Types
1. **Lift**: `translateY(-2px)` on hover for interactive elements
2. **Fade**: Opacity 0 → 1 for content reveals
3. **Slide**: `translateX/Y` for navigation, modals
4. **Scale**: Slight scale-up for focus/hover states
5. **Spin**: 360° rotate for loaders (2s, infinite)
6. **Pulse**: Opacity pulse for loading skeletons

### Accessibility
- Reduced motion: Respect `prefers-reduced-motion` media query
- All animations have matching transitions for reversals
- No animations block critical interactions

---

## Typography Hierarchy

### Font Stack
- **UI/Headings**: Inter (sans-serif) - modern, clean
- **Body**: Inter (sans-serif) - consistent readability
- **Code/Monospace**: JetBrains Mono - clear code display

### Scale
- **H1**: 48px / 700 Bold / Line 1.2
- **H2**: 32px / 600 SemiBold / Line 1.3
- **H3**: 24px / 600 SemiBold / Line 1.4
- **H4**: 16px / 600 SemiBold / Line 1.5
- **Body**: 14px / 400 Regular / Line 1.6
- **Small**: 12px / 400 Regular / Line 1.5
- **Mono**: 13px / 400 Regular / Line 1.5

---

## Responsive Breakpoints

| Device | Width | Layout | Sidebar |
|--------|-------|--------|---------|
| Mobile | <640px | Single column | Hidden, hamburger menu |
| Tablet | 640-1024px | 2-column grid | Toggle collapsed |
| Desktop | 1024-1920px | Full layout | Visible, 280px |
| Wide | >1920px | Optional collapse | Full |

---

## Accessibility Commitments

### WCAG 2.1 AA Standards
- ✓ Contrast ratio minimum 4.5:1 for all text
- ✓ Touch targets minimum 44x44px
- ✓ Keyboard navigation full support (Tab order)
- ✓ Focus indicators always visible
- ✓ Semantic HTML throughout
- ✓ ARIA labels on all form controls
- ✓ Reduced motion support
- ✓ Color not sole indicator

### Testing Requirements
- Screen reader testing (NVDA, JAWS, VoiceOver)
- Keyboard-only navigation
- Color contrast verification
- Mobile touch target testing

---

## Design Implementation Phases

### Phase 1: Foundation (Core UI Framework)
**Deliverables:**
- Design tokens CSS file (colors, spacing, typography)
- Base component library (Button, Input, Card, Badge)
- Layout components (Header, Sidebar, Container)
- Global styles (reset, base, utilities)
- Design system documentation

**Timeline:** Weeks 1-2

### Phase 2: Feature Components (Platform Features)
**Deliverables:**
- TaskInputPanel with variables support
- OutputPanel with real-time log streaming
- MetricsCard grid with indicators
- SessionTable with sorting/filtering
- StatusBadge component set
- Modal and notification system

**Timeline:** Weeks 3-4

### Phase 3: Page Templates (Full Pages)
**Deliverables:**
- Orchestrator page (complete layout)
- Flow tab (decision tree visualization)
- History page (session management)
- Settings page (configuration)
- Responsive mobile layouts

**Timeline:** Weeks 5-6

### Phase 4: Polish & Optimization (Refinement)
**Deliverables:**
- Animation refinement (smooth transitions)
- Performance optimization
- Accessibility audit and fixes
- Cross-browser testing
- Mobile responsiveness verification
- Dark mode final review

**Timeline:** Weeks 7-8

---

## File Structure for Implementation

```
src/
├── components/
│   ├── ui/
│   │   ├── button.tsx
│   │   ├── input.tsx
│   │   ├── card.tsx
│   │   ├── badge.tsx
│   │   ├── tabs.tsx
│   │   ├── modal.tsx
│   │   └── index.ts (barrel export)
│   ├── layout/
│   │   ├── header.tsx
│   │   ├── sidebar.tsx
│   │   ├── main.tsx
│   │   ├── container.tsx
│   │   └── index.ts
│   └── features/
│       ├── orchestrator/
│       │   ├── task-input-panel.tsx
│       │   ├── output-panel.tsx
│       │   └── index.ts
│       ├── history/
│       │   ├── session-table.tsx
│       │   └── index.ts
│       └── metrics/
│           ├── metrics-card.tsx
│           └── index.ts
├── styles/
│   ├── globals.css (Reset, base styles)
│   ├── design-tokens.css (Colors, spacing, typography)
│   ├── animations.css (Keyframes, transitions)
│   └── utilities.css (Custom utilities)
├── hooks/
│   ├── useToast.ts
│   ├── useTheme.ts
│   ├── useMediaQuery.ts
│   └── index.ts
├── pages/
│   ├── orchestrator.tsx
│   ├── flow.tsx
│   ├── history.tsx
│   ├── settings.tsx
│   └── layout.tsx
├── types/
│   ├── index.ts
│   ├── orchestrator.ts
│   ├── session.ts
│   └── component-props.ts
└── utils/
    ├── cn.ts (Class name utility)
    ├── constants.ts
    └── format.ts (Date, tokens, cost)
```

---

## Integration Points

### With Existing Codebase
- Replace Streamlit GUI with React/Next.js frontend
- Maintain same API endpoints (`orchestrator.py run`, etc.)
- Preserve all backend functionality
- Add new CSS variables without removing existing styles

### Deployment
- Deploy to Vercel for optimal Next.js performance
- CDN for static assets (images, fonts)
- Serverless functions for API routes
- Environment variables for API keys

---

## Success Metrics

### Design Quality
- ✓ All pages match design system specifications
- ✓ Component reusability > 80%
- ✓ Zero contrast accessibility violations
- ✓ Animations smooth at 60fps

### Performance
- ✓ Page load < 2 seconds (desktop)
- ✓ Page load < 3 seconds (mobile)
- ✓ Core Web Vitals all green
- ✓ Lighthouse score > 90

### User Experience
- ✓ Task execution < 1 click (from landing)
- ✓ Results visible within 1 second of completion
- ✓ Responsive on all breakpoints
- ✓ Keyboard navigation complete

---

## References & Inspiration

### Similar Platforms
- **Vercel Dashboard**: Enterprise UI, dark theme, clean typography
- **Supabase Dashboard**: Data-centric, vibrant accent colors, modular components
- **Braintrust**: Premium aesthetic, gradient accents, smooth animations
- **GitHub**: Clean tables, effective use of space, accessible design

### Design Resources
- **Color**: https://www.tailwindcss.com/docs/customizing-colors
- **Typography**: https://fonts.google.com/
- **Accessibility**: https://www.a11y-101.com/
- **Icons**: https://lucide.dev/ or https://heroicons.dev/

---

## Next Steps

1. **Stakeholder Review** (1-2 days)
   - Present design vision and color palette
   - Get approval on component styles
   - Confirm layout priorities

2. **Framework Selection** (1 day)
   - Finalize React/Next.js version
   - Select UI component library (if any)
   - Set up build/deployment pipeline

3. **Design Tokens Setup** (2-3 days)
   - Create design tokens CSS file
   - Document all spacing/typography scale
   - Test in Figma/prototype

4. **Component Library Build** (1-2 weeks)
   - Build foundation components
   - Document with Storybook (optional)
   - Set up testing suite

5. **Feature Implementation** (2-3 weeks)
   - Build page layouts
   - Integrate with backend APIs
   - Add real data

6. **Polish & Launch** (1 week)
   - Accessibility audit
   - Performance optimization
   - Cross-browser testing
   - Deploy to production

---

## Design System Maintenance

### Updates & Changes
- Document any new components in design system
- Version the design system (v1.0, v1.1, etc.)
- Maintain changelog
- Annual accessibility audit

### Team Coordination
- Daily standups for blockers
- Weekly design reviews
- Bi-weekly user feedback sessions
- Monthly retrospectives

---

## Conclusion

Symphony-IR's new SaaS frontend design represents a significant upgrade in visual sophistication and user experience. By following this design system, we ensure:

- **Consistency**: Every component follows the same principles
- **Scalability**: Easy to add new features without breaking design
- **Accessibility**: Built-in compliance with WCAG standards
- **Performance**: Optimized assets and animations
- **Maintainability**: Clear documentation and patterns

The design balances **power** (advanced features) with **simplicity** (clean interface), creating an enterprise-grade platform that developers will love using.

