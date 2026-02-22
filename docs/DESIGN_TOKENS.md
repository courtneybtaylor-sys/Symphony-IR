# Design Tokens — SaaS Multi-Tenant Theming

## Overview

Design Tokens are a centralized system for managing design variables (colors, typography, spacing, etc.) across Symphony-IR. This enables:

- **Consistency** — Single source of truth for all design values
- **SaaS Customization** — Per-tenant branding without code changes
- **Maintainability** — Update colors globally across all interfaces
- **API Consumption** — Programmatic access to design values for integrations

## Token Structure

All design tokens are defined in [`gui/design_tokens.json`](../gui/design_tokens.json) following the [Design Tokens specification](https://design-tokens.github.io/community-group/format/).

### Categories

Tokens are organized into these categories:

| Category | Purpose | Examples |
|----------|---------|----------|
| **color** | Color palette (primary, accent, status, neutral) | `#1f77b4`, `#ff7f0e`, `#2ca02c` |
| **typography** | Font families and sizes | `Segoe UI, Roboto`, `16px`, `1.5` |
| **spacing** | Padding, margin, gaps | `4px`, `8px`, `16px`, `24px` |
| **border_radius** | Corner rounding | `4px`, `8px`, `12px` |
| **shadow** | Drop shadows | `0 4px 6px rgba(...)` |
| **animation** | Transitions and timing | `150ms`, `cubic-bezier(...)` |

## Using Tokens in Python

### Via TokenLoader (Recommended)

```python
from gui.token_loader import get_loader, get_token, get_theme

# Get a single token
loader = get_loader()
primary_color = loader.get_token("color.primary.base")
print(primary_color)  # Output: #1f77b4

# Get all colors for a theme
dark_colors = loader.get_theme("dark")
print(dark_colors["primary_base"])  # Output: #4ca3ff

# Get all tokens
all_tokens = loader.get_all_tokens()

# Apply custom tokens for tenant branding
loader.apply_custom_tokens({
    "color.primary.base": "#custom-brand-color",
    "color.accent": "#custom-accent"
})
```

### Shorthand Functions

```python
from gui.token_loader import get_token, get_theme

# These use the global loader instance
primary = get_token("color.primary.base")  # #1f77b4
dark_theme = get_theme("dark")
```

## Token Access Patterns

### Dot Notation

All tokens use dot notation for nested access:

```python
# Color tokens
get_token("color.primary.base")        # #1f77b4
get_token("color.primary.dark")        # #1557a0
get_token("color.status.success")      # #2ca02c
get_token("color.neutral.text_primary") # #1a1a1a

# Typography
get_token("typography.font_size.base")  # 16px
get_token("typography.font_family.mono") # Courier New, monospace

# Spacing
get_token("spacing.md")                 # 16px
get_token("spacing.lg")                 # 24px

# Animations
get_token("animation.duration_fast")    # 150ms
```

## Color Tokens

### Primary Colors (Brand)

```json
{
  "color.primary.base": "#1f77b4",      // Primary action color
  "color.primary.dark": "#1557a0",      // Hover/pressed state
  "color.primary.light": "#4ca3ff",     // Light backgrounds
  "color.primary.hover": "#2d7fcc"      // Hover state
}
```

### Accent Colors (Secondary)

```json
{
  "color.accent": "#ff7f0e"             // Secondary actions, highlights
}
```

### Status Colors

```json
{
  "color.status.success": "#2ca02c",    // Success/valid states
  "color.status.error": "#d62728",      // Error states
  "color.status.warning": "#ff9800",    // Warning states
  "color.status.info": "#17a2b8"        // Information states
}
```

### Neutral Colors (Theme-Aware)

Neutral colors have theme variants:

```json
{
  "color.neutral.background": {
    "value": "#ffffff",                 // Default
    "light": "#ffffff",                 // Light theme
    "dark": "#0d1117"                   // Dark theme
  },
  "color.neutral.text_primary": {
    "value": "#1a1a1a",
    "light": "#1a1a1a",
    "dark": "#e6edf3"
  }
}
```

## TypeScript/JavaScript Usage

For web applications using Symphony-IR API:

```typescript
// Fetch tokens from API endpoint (when deployed as SaaS)
const tokens = await fetch('/api/tokens').then(r => r.json());

// Access color token
const primaryColor = tokens.color.primary.base;

// Get theme-specific colors
const darkTheme = tokens.color.neutral.background.dark;

// Build CSS dynamically
const style = document.createElement('style');
style.textContent = `
  :root {
    --primary: ${tokens.color.primary.base};
    --accent: ${tokens.color.accent};
  }
`;
document.head.appendChild(style);
```

## SaaS Multi-Tenant Customization

For tenant branding, apply custom tokens:

```python
from gui.token_loader import get_loader

loader = get_loader()

# Customer-specific branding
tenant_id = "customer-123"
custom_colors = {
    "color.primary.base": "#e31e24",      # Acme Corp red
    "color.primary.dark": "#9d1111",
    "color.primary.light": "#ff4d4f",
    "color.accent": "#ffd700"             # Gold accents
}

loader.apply_custom_tokens(custom_colors)

# All subsequent get_token() calls use custom colors for this tenant
logo_color = loader.get_token("color.primary.base")  # #e31e24
```

## CSS Custom Properties

The token loader can generate CSS variables:

```python
from gui.token_loader import get_loader

loader = get_loader()

# Generate CSS :root with all tokens as variables
css = loader.get_css_variables(theme="light")
print(css)
```

Output:
```css
:root {
  --color-primary-base: #1f77b4;
  --color-primary-dark: #1557a0;
  --color-accent: #ff7f0e;
  --color-status-success: #2ca02c;
  ...
}
```

Then use in CSS:
```css
button {
  background-color: var(--color-primary-base);
}

button:hover {
  background-color: var(--color-primary-dark);
}
```

## Updating Tokens

### Modifying Token Values

1. Edit [`gui/design_tokens.json`](../gui/design_tokens.json)
2. Update the `"value"` field
3. Restart the application (tokens are loaded on startup)

Example:
```json
{
  "color": {
    "primary": {
      "base": {
        "value": "#new-color",  // Changed from #1f77b4
        "description": "..."
      }
    }
  }
}
```

### Adding New Tokens

Tokens follow a consistent structure:

```json
{
  "category": {
    "subcategory": {
      "name": {
        "value": "actual-value",
        "description": "What this token is used for",
        "light": "light-theme-value (optional)",
        "dark": "dark-theme-value (optional)"
      }
    }
  }
}
```

## Integration Points

### GUI Applications

- **PyQt6 Desktop:** `gui/main.py` can load tokens for stylesheets
- **Streamlit Web:** `gui/app.py` can apply tokens dynamically
- **CSS Styling:** `gui/styles.css` references tokens (see comments)

### Orchestrator Core

- **Flow Templates:** Can access tokens for UI consistency
- **Configuration:** Tokens can be part of `.orchestrator/config.yaml`

## Documentation

- Full token reference: [design_tokens.json](../gui/design_tokens.json)
- Token loader source: [token_loader.py](../gui/token_loader.py)
- CSS integration: [styles.css](../gui/styles.css)

## FAQ

**Q: Can I change tokens at runtime without restarting?**
A: Yes! Call `loader.apply_custom_tokens()` to override values dynamically.

**Q: Are tokens versioned?**
A: Yes, see `metadata.version` in design_tokens.json. Update this when making breaking changes.

**Q: Can I use tokens in configuration files?**
A: Yes, use dot-notation: `button-color: {theme_token: "color.primary.base"}`

**Q: How do I test token changes?**
A: Run the GUI and verify styling. Use `python3 -c "from gui.token_loader import get_token; print(get_token('color.primary.base'))"` to test loading.

---

**Last updated:** 2026-02-22
**Format:** Design Tokens Specification v1
**Status:** Production ready
