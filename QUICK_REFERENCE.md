# Symphony-IR SaaS Design System - Quick Reference Card

## 🎨 Color Palette

```
PRIMARY BLUE      #3B82F6  ■■■■■■■■■■ Buttons, Links, Focus
CYAN ACCENT       #06B6D4  ■■■■■■■■■■ Highlights, Accents
PURPLE            #8B5CF6  ■■■■■■■■■■ Gradient (Cyan→Purple)

BACKGROUND        #0F172A  ■■■■■■■■■■ Primary BG
SURFACE           #1E293B  ■■■■■■■■■■ Cards, Containers
BORDER            #334155  ■■■■■■■■■■ Lines, Dividers

TEXT PRIMARY      #E2E8F0  ■■■■■■■■■■ Main Text (4.8:1)
TEXT SECONDARY    #94A3B8  ■■■■■■■■■■ Secondary (5.1:1)
TEXT TERTIARY     #64748B  ■■■■■■■■■■ Disabled (3.2:1)

SUCCESS           #10B981  ■■■■■■■■■■ Completion
WARNING           #F59E0B  ■■■■■■■■■■ Caution
ERROR             #EF4444  ■■■■■■■■■■ Errors
INFO              #3B82F6  ■■■■■■■■■■ Information
```

---

## 📏 Typography

| Element | Size | Weight | Line-Height | Example |
|---------|------|--------|-------------|---------|
| H1 | 48px | 700 | 1.2 | Page Titles |
| H2 | 32px | 600 | 1.3 | Section Headers |
| H3 | 24px | 600 | 1.4 | Subsections |
| H4 | 16px | 600 | 1.5 | Labels |
| Body | 14px | 400 | 1.6 | Main Content |
| Small | 12px | 400 | 1.5 | Captions |
| Mono | 13px | 400 | 1.5 | Code/Logs |

**Fonts:** Inter (UI), JetBrains Mono (Code)

---

## 📐 Spacing Scale (8px Grid)

```
0    → 0px
xs   → 4px
sm   → 8px
md   → 16px
lg   → 24px
xl   → 32px
2xl  → 48px
3xl  → 64px
```

**Common usage:**
- Section padding: 32px (2xl)
- Component padding: 24px (lg)
- Element gaps: 16px (md)
- Micro spacing: 8px (sm)

---

## 🔲 Component Sizes

| Component | Height | Width | Border-Radius |
|-----------|--------|-------|---------------|
| Button (md) | 44px | Auto | 8px |
| Input (md) | 40px | Auto | 8px |
| Card | Auto | Auto | 12px |
| Header | 64px | 100% | 0 |
| Sidebar | 100vh | 280px | 0 |
| Icon | 20-24px | 20-24px | 4px |
| Avatar | 40px | 40px | 50% |

---

## 🎯 Button Variants

```
PRIMARY (Blue)
┌──────────────────┐
│  Execute  Button │  Hover: Lift 2px, Blue-600
└──────────────────┘  Active: Blue-700, No lift

SECONDARY (Outlined)
┌──────────────────┐
│  Secondary Btn   │  Border: 2px Blue-500
└──────────────────┘  Hover: Blue-500 fill

TERTIARY (Text)
┌──────────────────┐
│  Tertiary Link   │  Blue-400, underline on hover
└──────────────────┘

GHOST (Icon)
┌──────┐
│  ⚙️   │  Hover: Slight bg, no border
└──────┘
```

---

## 🌊 Responsive Breakpoints

```
Mobile          <640px   │ Single Column, Hamburger Menu
Tablet          640-1024 │ 2-Column, Collapsed Sidebar
Desktop         1024+    │ Full Layout, 280px Sidebar
Wide            1920+    │ Optional Collapse
```

---

## ⚡ Animations

| Animation | Duration | Easing | Use Case |
|-----------|----------|--------|----------|
| Fade | 200ms | ease-out | Quick state changes |
| Slide | 300ms | ease-out | Modals, panels |
| Scale | 200ms | ease-out | Button press |
| Spin | 2s | linear | Loading spinner |
| Lift | 200ms | ease-out | Hover effects |

**Reduced motion:** Respect `prefers-reduced-motion` media query

---

## ✅ Component Checklist

### Essential Components
- [ ] Button (4 variants)
- [ ] Input (text, textarea, select)
- [ ] Card (default, gradient border)
- [ ] Badge (5 semantic types)
- [ ] Tabs (with indicator)
- [ ] Modal (with overlay)
- [ ] Toast (notifications)

### Layout Components
- [ ] Header (sticky, 64px)
- [ ] Sidebar (280px, collapsible)
- [ ] Container (max-width wrapper)
- [ ] Grid (responsive)

### Feature Components
- [ ] Task Input Panel
- [ ] Output Panel (streaming)
- [ ] Metrics Card
- [ ] Session Table
- [ ] Status Badge

---

## 🎮 Interaction States

```
DEFAULT
└─ Hover → Lift 2px, Shadow ↑
   └─ Active → Color ↓, No lift
      └─ Released → Return to hover

FOCUS
└─ Ring 2px Blue-500 (opacity 10%)

DISABLED
└─ Opacity 50%, No interaction

LOADING
└─ Spinner animation, Disabled state
```

---

## 🔒 Accessibility (WCAG 2.1 AA)

- ✅ Contrast: 4.5:1 minimum
- ✅ Touch targets: 44×44px
- ✅ Keyboard: Tab, Enter, Escape, Arrow keys
- ✅ Focus: Always visible
- ✅ Labels: All inputs labeled
- ✅ Reduced motion: Respected
- ✅ Screen readers: Semantic HTML + ARIA

---

## 📐 Common Layouts

### Two-Column (Desktop)
```
45% Input | 50% Output
├─ Task textarea (full height)
├─ Variables section
├─ Options accordion
└─ Execute button (full-width)
```

### Four Metrics (Desktop)
```
[Metric 1] [Metric 2] [Metric 3] [Metric 4]
32px icon, bold number, trend indicator
16px gap between cards
```

### Header Navigation
```
[Logo] [Nav Items] [Theme] [Profile]
64px height, sticky top, 32px left/right padding
```

---

## 📁 CSS Variables Setup

```css
:root {
  /* Colors */
  --color-primary: #3B82F6;
  --color-accent: #06B6D4;
  --bg-primary: #0F172A;
  --text-primary: #E2E8F0;
  
  /* Spacing */
  --space-2: 8px;
  --space-4: 16px;
  --space-6: 24px;
  
  /* Typography */
  --font-sans: 'Inter', sans-serif;
  --font-mono: 'JetBrains Mono', monospace;
  
  /* Radius */
  --radius-md: 8px;
  --radius-lg: 12px;
}
```

---

## 🚀 Development Quick Start

```tsx
// Import components
import { Button, Input, Card } from '@/components/ui';

// Use design tokens
<div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
  <h2 className="text-2xl font-semibold text-slate-200">
    Title
  </h2>
  <Button variant="primary">Execute</Button>
</div>
```

---

## 📋 Pre-Launch Checklist

- [ ] All components implemented
- [ ] Colors match palette exactly
- [ ] Typography matches scale
- [ ] Spacing on 8px grid
- [ ] Animations 200-300ms
- [ ] Responsive tested (mobile/tablet/desktop)
- [ ] Accessibility audit (WCAG AA)
- [ ] Cross-browser tested
- [ ] Performance optimized
- [ ] Documentation complete

---

## 🔗 Resource Links

- **Design System:** DESIGN_SYSTEM.md
- **Components:** COMPONENT_SPECS.md
- **Code Examples:** IMPLEMENTATION_GUIDE.md
- **Vision & Strategy:** DESIGN_VISION.md
- **Full Index:** DOCUMENTATION_INDEX.md

---

## 📞 Common Questions

**Q: What blue should I use for buttons?**  
A: #3B82F6 (Primary Blue)

**Q: How much padding for cards?**  
A: 24px (lg in spacing scale)

**Q: What's the sidebar width?**  
A: 280px desktop, 64px collapsed

**Q: How tall is the header?**  
A: 64px with sticky positioning

**Q: What font for code?**  
A: JetBrains Mono at 13px

**Q: How much spacing between elements?**  
A: 16px (md) default, 8px compact

**Q: What's the border radius for buttons?**  
A: 8px

**Q: What opacity for disabled states?**  
A: 50%

**Q: How long should animations be?**  
A: 200ms quick, 300ms standard, 500ms slow

---

## ⚙️ Customization Guide

### To change primary color:
1. Update all --color-primary instances
2. Update brand blue in palette
3. Test contrast ratios (need 4.5:1)
4. Test all interactive states

### To change spacing:
1. Never break 8px grid
2. Use multiples of 4px minimum
3. Update --space-* variables
4. Ensure touch targets stay 44px+

### To add new components:
1. Document in COMPONENT_SPECS.md
2. Add code example to IMPLEMENTATION_GUIDE.md
3. Use design tokens (no hardcoded colors)
4. Test accessibility
5. Update component inventory

---

**Last Updated:** February 20, 2026  
**Version:** 1.0  
**Status:** Ready for Development

Print this card and keep it nearby! 🎼

