#!/usr/bin/env python3
"""
Symphony-IR Design Token System

Canonical source of design tokens (colors, typography, spacing, shadows, animations).
Supports multi-tenant theme overrides and exports to CSS/JSON for web frontends.

Usage:
    from gui.design_tokens import DesignTokens
    tokens = DesignTokens()
    css = tokens.to_css()

    # With tenant override
    enterprise_theme = {"colors": {"primary": "#7c3aed"}}
    tokens = DesignTokens(overrides=enterprise_theme)

    # Export
    python gui/design_tokens.py --export css    -> gui/styles/theme.css
    python gui/design_tokens.py --export json   -> gui/styles/tokens.json
"""

import json
import argparse
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional, Dict, Any


# ---------------------------------------------------------------------------
# Color Palette
# ---------------------------------------------------------------------------

@dataclass
class ColorScale:
    """A single color with light/dark variants."""
    _50:  str = ""
    _100: str = ""
    _200: str = ""
    _300: str = ""
    _400: str = ""
    _500: str = ""   # default shade
    _600: str = ""
    _700: str = ""
    _800: str = ""
    _900: str = ""


@dataclass
class Colors:
    # Brand palette
    primary:  str = "#3B82F6"   # Blue-500
    primary_dark: str = "#1D4ED8"   # Blue-700
    primary_light: str = "#93C5FD"   # Blue-300

    accent:   str = "#8B5CF6"   # Violet-500
    accent_dark: str = "#6D28D9"
    accent_light: str = "#C4B5FD"

    # Semantic
    success:  str = "#22C55E"   # Green-500
    success_bg: str = "#F0FDF4"
    warning:  str = "#F59E0B"   # Amber-500
    warning_bg: str = "#FFFBEB"
    error:    str = "#EF4444"   # Red-500
    error_bg: str = "#FEF2F2"
    info:     str = "#06B6D4"   # Cyan-500
    info_bg:  str = "#ECFEFF"

    # Neutral (light mode)
    background: str = "#FFFFFF"
    surface:    str = "#F8FAFC"
    surface_alt: str = "#F1F5F9"
    border:     str = "#E2E8F0"
    text:       str = "#0F172A"
    text_muted: str = "#64748B"
    text_inverse: str = "#FFFFFF"

    # Dark mode equivalents
    dark_background: str = "#0D1117"
    dark_surface:    str = "#161B22"
    dark_surface_alt: str = "#21262D"
    dark_border:     str = "#30363D"
    dark_text:       str = "#E6EDF3"
    dark_text_muted: str = "#8B949E"

    # Elevation / overlays
    overlay:    str = "rgba(0, 0, 0, 0.5)"
    shadow_sm:  str = "rgba(0, 0, 0, 0.05)"
    shadow_md:  str = "rgba(0, 0, 0, 0.1)"
    shadow_lg:  str = "rgba(0, 0, 0, 0.15)"


# ---------------------------------------------------------------------------
# Typography
# ---------------------------------------------------------------------------

@dataclass
class FontSize:
    xs:   str = "0.75rem"    # 12px
    sm:   str = "0.875rem"   # 14px
    base: str = "1rem"       # 16px
    lg:   str = "1.125rem"   # 18px
    xl:   str = "1.25rem"    # 20px
    _2xl: str = "1.5rem"     # 24px
    _3xl: str = "1.875rem"   # 30px
    _4xl: str = "2.25rem"    # 36px


@dataclass
class FontWeight:
    light:    int = 300
    regular:  int = 400
    medium:   int = 500
    semibold: int = 600
    bold:     int = 700
    black:    int = 900


@dataclass
class LineHeight:
    tight:  str = "1.25"
    snug:   str = "1.375"
    normal: str = "1.5"
    relaxed: str = "1.625"
    loose:  str = "2"


@dataclass
class Typography:
    font_family_sans: str = (
        "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, "
        "'Helvetica Neue', Arial, sans-serif"
    )
    font_family_mono: str = (
        "'JetBrains Mono', 'Fira Code', 'Cascadia Code', "
        "Consolas, 'Courier New', monospace"
    )
    size:        FontSize   = field(default_factory=FontSize)
    weight:      FontWeight = field(default_factory=FontWeight)
    line_height: LineHeight = field(default_factory=LineHeight)


# ---------------------------------------------------------------------------
# Spacing
# ---------------------------------------------------------------------------

@dataclass
class Spacing:
    px:  str = "1px"
    _0:  str = "0"
    _1:  str = "0.25rem"   # 4px
    _2:  str = "0.5rem"    # 8px
    _3:  str = "0.75rem"   # 12px
    _4:  str = "1rem"      # 16px
    _5:  str = "1.25rem"   # 20px
    _6:  str = "1.5rem"    # 24px
    _8:  str = "2rem"      # 32px
    _10: str = "2.5rem"    # 40px
    _12: str = "3rem"      # 48px
    _16: str = "4rem"      # 64px
    _20: str = "5rem"      # 80px
    _24: str = "6rem"      # 96px


# ---------------------------------------------------------------------------
# Border Radius
# ---------------------------------------------------------------------------

@dataclass
class BorderRadius:
    none: str = "0"
    sm:   str = "0.25rem"    # 4px
    base: str = "0.375rem"   # 6px
    md:   str = "0.5rem"     # 8px
    lg:   str = "0.75rem"    # 12px
    xl:   str = "1rem"       # 16px
    _2xl: str = "1.5rem"     # 24px
    full: str = "9999px"


# ---------------------------------------------------------------------------
# Shadows (Box Shadow)
# ---------------------------------------------------------------------------

@dataclass
class Shadows:
    sm:  str = "0 1px 2px 0 rgba(0,0,0,0.05)"
    base: str = "0 1px 3px 0 rgba(0,0,0,0.1), 0 1px 2px -1px rgba(0,0,0,0.1)"
    md:  str = "0 4px 6px -1px rgba(0,0,0,0.1), 0 2px 4px -2px rgba(0,0,0,0.1)"
    lg:  str = "0 10px 15px -3px rgba(0,0,0,0.1), 0 4px 6px -4px rgba(0,0,0,0.1)"
    xl:  str = "0 20px 25px -5px rgba(0,0,0,0.1), 0 8px 10px -6px rgba(0,0,0,0.1)"
    inner: str = "inset 0 2px 4px 0 rgba(0,0,0,0.05)"
    none: str = "none"


# ---------------------------------------------------------------------------
# Transitions / Animation
# ---------------------------------------------------------------------------

@dataclass
class Transitions:
    fast:   str = "150ms cubic-bezier(0.4, 0, 0.2, 1)"
    base:   str = "200ms cubic-bezier(0.4, 0, 0.2, 1)"
    slow:   str = "300ms cubic-bezier(0.4, 0, 0.2, 1)"
    slower: str = "500ms cubic-bezier(0.4, 0, 0.2, 1)"


# ---------------------------------------------------------------------------
# Z-Index
# ---------------------------------------------------------------------------

@dataclass
class ZIndex:
    dropdown:  int = 1000
    sticky:    int = 1020
    fixed:     int = 1030
    overlay:   int = 1040
    modal:     int = 1050
    popover:   int = 1060
    tooltip:   int = 1070


# ---------------------------------------------------------------------------
# Breakpoints
# ---------------------------------------------------------------------------

@dataclass
class Breakpoints:
    sm:  str = "640px"
    md:  str = "768px"
    lg:  str = "1024px"
    xl:  str = "1280px"
    _2xl: str = "1536px"


# ---------------------------------------------------------------------------
# Main DesignTokens class
# ---------------------------------------------------------------------------

class DesignTokens:
    """
    Unified design token container.

    Supports per-tenant overrides for SaaS multi-tenancy:
        tokens = DesignTokens(overrides={
            "colors": {"primary": "#7c3aed", "primary_dark": "#5b21b6"},
        })
    """

    def __init__(self, overrides: Optional[Dict[str, Any]] = None):
        self.colors      = Colors()
        self.typography  = Typography()
        self.spacing     = Spacing()
        self.radius      = BorderRadius()
        self.shadows     = Shadows()
        self.transitions = Transitions()
        self.z_index     = ZIndex()
        self.breakpoints = Breakpoints()

        if overrides:
            self._apply_overrides(overrides)

    # ------------------------------------------------------------------
    # Override support
    # ------------------------------------------------------------------

    def _apply_overrides(self, overrides: Dict[str, Any]):
        """Shallow-merge tenant overrides into token groups."""
        for group_name, values in overrides.items():
            group = getattr(self, group_name, None)
            if group is None:
                continue
            for key, val in values.items():
                if hasattr(group, key):
                    setattr(group, key, val)

    # ------------------------------------------------------------------
    # Exports
    # ------------------------------------------------------------------

    def to_dict(self) -> Dict[str, Any]:
        """Serialize all tokens to a nested dict."""
        return {
            "colors":      asdict(self.colors),
            "typography":  asdict(self.typography),
            "spacing":     asdict(self.spacing),
            "radius":      asdict(self.radius),
            "shadows":     asdict(self.shadows),
            "transitions": asdict(self.transitions),
            "z_index":     asdict(self.z_index),
            "breakpoints": asdict(self.breakpoints),
        }

    def to_json(self, indent: int = 2) -> str:
        """Serialize tokens to JSON."""
        return json.dumps(self.to_dict(), indent=indent)

    def to_css(self) -> str:
        """
        Generate a CSS stylesheet with custom properties.
        Returns the full CSS string (light + dark modes).
        """
        c = self.colors
        t = self.typography
        s = self.spacing
        r = self.radius
        sh = self.shadows
        tr = self.transitions

        return f"""\
/* =============================================================================
   Symphony-IR Design Tokens — Auto-generated by gui/design_tokens.py
   Do not edit manually; modify DesignTokens and re-run:
       python gui/design_tokens.py --export css
   ============================================================================= */

/* ── Light Mode (default) ──────────────────────────────────────────────────── */
:root {{
  /* Brand */
  --color-primary:        {c.primary};
  --color-primary-dark:   {c.primary_dark};
  --color-primary-light:  {c.primary_light};
  --color-accent:         {c.accent};
  --color-accent-dark:    {c.accent_dark};
  --color-accent-light:   {c.accent_light};

  /* Semantic */
  --color-success:        {c.success};
  --color-success-bg:     {c.success_bg};
  --color-warning:        {c.warning};
  --color-warning-bg:     {c.warning_bg};
  --color-error:          {c.error};
  --color-error-bg:       {c.error_bg};
  --color-info:           {c.info};
  --color-info-bg:        {c.info_bg};

  /* Neutral */
  --color-background:     {c.background};
  --color-surface:        {c.surface};
  --color-surface-alt:    {c.surface_alt};
  --color-border:         {c.border};
  --color-text:           {c.text};
  --color-text-muted:     {c.text_muted};
  --color-text-inverse:   {c.text_inverse};

  /* Elevation */
  --color-overlay:        {c.overlay};
  --shadow-sm:            {sh.sm};
  --shadow-base:          {sh.base};
  --shadow-md:            {sh.md};
  --shadow-lg:            {sh.lg};
  --shadow-xl:            {sh.xl};

  /* Typography */
  --font-sans:            {t.font_family_sans};
  --font-mono:            {t.font_family_mono};
  --text-xs:              {t.size.xs};
  --text-sm:              {t.size.sm};
  --text-base:            {t.size.base};
  --text-lg:              {t.size.lg};
  --text-xl:              {t.size.xl};
  --text-2xl:             {t.size._2xl};
  --text-3xl:             {t.size._3xl};
  --text-4xl:             {t.size._4xl};
  --font-light:           {t.weight.light};
  --font-regular:         {t.weight.regular};
  --font-medium:          {t.weight.medium};
  --font-semibold:        {t.weight.semibold};
  --font-bold:            {t.weight.bold};
  --leading-tight:        {t.line_height.tight};
  --leading-normal:       {t.line_height.normal};
  --leading-relaxed:      {t.line_height.relaxed};

  /* Spacing */
  --space-1:              {s._1};
  --space-2:              {s._2};
  --space-3:              {s._3};
  --space-4:              {s._4};
  --space-5:              {s._5};
  --space-6:              {s._6};
  --space-8:              {s._8};
  --space-10:             {s._10};
  --space-12:             {s._12};
  --space-16:             {s._16};

  /* Border Radius */
  --radius-sm:            {r.sm};
  --radius-base:          {r.base};
  --radius-md:            {r.md};
  --radius-lg:            {r.lg};
  --radius-xl:            {r.xl};
  --radius-2xl:           {r._2xl};
  --radius-full:          {r.full};

  /* Transitions */
  --transition-fast:      all {tr.fast};
  --transition-base:      all {tr.base};
  --transition-slow:      all {tr.slow};
}}

/* ── Dark Mode ─────────────────────────────────────────────────────────────── */
@media (prefers-color-scheme: dark) {{
  :root {{
    --color-background:   {c.dark_background};
    --color-surface:      {c.dark_surface};
    --color-surface-alt:  {c.dark_surface_alt};
    --color-border:       {c.dark_border};
    --color-text:         {c.dark_text};
    --color-text-muted:   {c.dark_text_muted};
    --color-primary:      {c.primary_light};
    --color-primary-dark: {c.primary};
    --shadow-sm:          0 1px 2px 0 rgba(0,0,0,0.3);
    --shadow-md:          0 4px 6px -1px rgba(0,0,0,0.4);
  }}
}}

/* ── Base styles using design tokens ───────────────────────────────────────── */
body,
.main {{
  background-color: var(--color-background);
  color:            var(--color-text);
  font-family:      var(--font-sans);
  font-size:        var(--text-base);
  line-height:      var(--leading-normal);
}}

/* Buttons */
button {{
  border-radius:    var(--radius-md) !important;
  font-weight:      var(--font-medium) !important;
  letter-spacing:   0.3px !important;
  transition:       var(--transition-base) !important;
  border:           none !important;
  padding:          var(--space-2) var(--space-5) !important;
}}

[data-testid="baseButton-primary"] {{
  background-color: var(--color-primary) !important;
  color:            var(--color-text-inverse) !important;
  box-shadow:       var(--shadow-md) !important;
}}

[data-testid="baseButton-primary"]:hover {{
  background-color: var(--color-primary-dark) !important;
  transform:        translateY(-2px) !important;
  box-shadow:       var(--shadow-lg) !important;
}}

[data-testid="baseButton-secondary"] {{
  background-color: var(--color-surface) !important;
  color:            var(--color-primary) !important;
  border:           2px solid var(--color-primary) !important;
}}

[data-testid="baseButton-secondary"]:hover {{
  background-color: var(--color-primary) !important;
  color:            var(--color-text-inverse) !important;
}}

/* Tabs */
[data-baseweb="tab-list"] {{
  border-bottom: 2px solid var(--color-border) !important;
}}

[data-baseweb="tab"] {{
  color:        var(--color-text-muted) !important;
  font-weight:  var(--font-semibold) !important;
  padding:      var(--space-3) var(--space-6) !important;
  border-radius: var(--radius-md) var(--radius-md) 0 0 !important;
  transition:   var(--transition-base) !important;
}}

[data-baseweb="tab"]:hover {{
  color:            var(--color-primary) !important;
  background-color: var(--color-surface) !important;
}}

[data-baseweb="tab"][aria-selected="true"] {{
  color:        var(--color-primary) !important;
  border-bottom: 3px solid var(--color-primary) !important;
}}

/* Inputs */
textarea,
input {{
  border-radius: var(--radius-base) !important;
  border:        1px solid var(--color-border) !important;
  transition:    var(--transition-base) !important;
}}

textarea:focus,
input:focus {{
  border-color: var(--color-primary) !important;
  box-shadow:   0 0 0 3px rgba(59, 130, 246, 0.15) !important;
}}

/* Cards / Metric Containers */
[data-testid="stMetricContainer"] {{
  background:    var(--color-surface) !important;
  border-radius: var(--radius-xl) !important;
  padding:       var(--space-4) !important;
  border:        1px solid var(--color-border) !important;
  transition:    var(--transition-base) !important;
  box-shadow:    var(--shadow-sm) !important;
}}

[data-testid="stMetricContainer"]:hover {{
  box-shadow: var(--shadow-md) !important;
  transform:  translateY(-2px) !important;
}}

/* Alerts */
[data-testid="stSuccess"] {{
  border-radius:    var(--radius-md) !important;
  border-left:      4px solid var(--color-success) !important;
  background-color: var(--color-success-bg) !important;
  padding:          var(--space-3) var(--space-4) !important;
}}

[data-testid="stError"] {{
  border-radius:    var(--radius-md) !important;
  border-left:      4px solid var(--color-error) !important;
  background-color: var(--color-error-bg) !important;
  padding:          var(--space-3) var(--space-4) !important;
}}

[data-testid="stWarning"] {{
  border-radius:    var(--radius-md) !important;
  border-left:      4px solid var(--color-warning) !important;
  background-color: var(--color-warning-bg) !important;
  padding:          var(--space-3) var(--space-4) !important;
}}

[data-testid="stInfo"] {{
  border-radius:    var(--radius-md) !important;
  border-left:      4px solid var(--color-info) !important;
  background-color: var(--color-info-bg) !important;
  padding:          var(--space-3) var(--space-4) !important;
}}

/* Expanders */
[data-testid="stExpander"] {{
  border:        1px solid var(--color-border) !important;
  border-radius: var(--radius-md) !important;
  margin-bottom: var(--space-3) !important;
  transition:    var(--transition-base) !important;
}}

[data-testid="stExpander"]:hover {{
  border-color: var(--color-primary) !important;
  box-shadow:   var(--shadow-md) !important;
}}

/* Code */
code {{
  font-family:      var(--font-mono) !important;
  background-color: var(--color-surface-alt) !important;
  border-radius:    var(--radius-sm) !important;
  padding:          2px var(--space-1) !important;
  color:            var(--color-accent) !important;
  font-size:        var(--text-sm) !important;
}}

/* File uploader */
[data-testid="stFileUploader"] {{
  border:        2px dashed var(--color-border) !important;
  border-radius: var(--radius-md) !important;
  padding:       var(--space-4) !important;
  transition:    var(--transition-base) !important;
}}

[data-testid="stFileUploader"]:hover {{
  border-color:     var(--color-primary) !important;
  background-color: var(--color-surface) !important;
}}

/* Sidebar */
[data-testid="stSidebar"] {{
  border-right: 1px solid var(--color-border) !important;
}}

/* Download button */
[data-testid="stDownloadButton"] > button {{
  background: linear-gradient(
    135deg,
    var(--color-success),
    var(--color-info)
  ) !important;
  color: var(--color-text-inverse) !important;
}}

/* Typography */
h1, h2, h3, h4, h5, h6 {{
  letter-spacing: 0.3px !important;
  font-weight:    var(--font-semibold) !important;
}}

h1 {{ color: var(--color-text) !important; margin-bottom: var(--space-6) !important; }}
h2 {{ color: var(--color-text) !important; margin-top: var(--space-6) !important; }}
h3 {{ color: var(--color-text-muted) !important; margin-top: var(--space-4) !important; }}

/* Global smooth transitions */
*, *::before, *::after {{
  transition: background-color var(--transition-base),
              color var(--transition-base),
              border-color var(--transition-base);
}}
"""

    def save_css(self, path: Optional[str] = None) -> Path:
        """Write CSS to a file and return the path."""
        if path is None:
            out = Path(__file__).parent / "styles" / "theme.css"
        else:
            out = Path(path)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(self.to_css(), encoding="utf-8")
        return out

    def save_json(self, path: Optional[str] = None) -> Path:
        """Write token JSON to a file and return the path."""
        if path is None:
            out = Path(__file__).parent / "styles" / "tokens.json"
        else:
            out = Path(path)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(self.to_json(), encoding="utf-8")
        return out

    # ------------------------------------------------------------------
    # PyQt6 stylesheet helper (Qt CSS subset)
    # ------------------------------------------------------------------

    def to_qt_stylesheet(self) -> str:
        """
        Generate a Qt stylesheet string from design tokens.
        Useful for applying the design system to the PyQt6 desktop app.
        """
        c = self.colors
        return f"""
QWidget {{
    background-color: {c.background};
    color: {c.text};
    font-family: "Segoe UI", Arial, sans-serif;
    font-size: 13px;
}}

QPushButton {{
    background-color: {c.primary};
    color: {c.text_inverse};
    border: none;
    border-radius: 6px;
    padding: 8px 16px;
    font-weight: 600;
}}

QPushButton:hover {{
    background-color: {c.primary_dark};
}}

QPushButton:disabled {{
    background-color: {c.border};
    color: {c.text_muted};
}}

QLineEdit, QTextEdit {{
    background-color: {c.surface};
    color: {c.text};
    border: 1px solid {c.border};
    border-radius: 4px;
    padding: 6px 10px;
}}

QLineEdit:focus, QTextEdit:focus {{
    border-color: {c.primary};
}}

QTabWidget::pane {{
    border: 1px solid {c.border};
    border-radius: 6px;
}}

QTabBar::tab {{
    background: {c.surface};
    color: {c.text_muted};
    padding: 8px 16px;
    border-radius: 4px 4px 0 0;
}}

QTabBar::tab:selected {{
    background: {c.background};
    color: {c.primary};
    border-bottom: 2px solid {c.primary};
}}

QProgressBar {{
    background-color: {c.surface};
    border: 1px solid {c.border};
    border-radius: 4px;
    height: 8px;
}}

QProgressBar::chunk {{
    background-color: {c.primary};
    border-radius: 4px;
}}
"""


# ---------------------------------------------------------------------------
# CLI export support
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Export Symphony-IR design tokens to CSS or JSON"
    )
    parser.add_argument(
        "--export",
        choices=["css", "json", "both"],
        default="both",
        help="Output format (default: both)"
    )
    parser.add_argument(
        "--out-dir",
        default=None,
        help="Output directory (default: gui/styles/)"
    )
    args = parser.parse_args()

    tokens = DesignTokens()
    out_dir = args.out_dir

    if args.export in ("css", "both"):
        path = tokens.save_css(
            str(Path(out_dir) / "theme.css") if out_dir else None
        )
        print(f"CSS tokens written to: {path}")

    if args.export in ("json", "both"):
        path = tokens.save_json(
            str(Path(out_dir) / "tokens.json") if out_dir else None
        )
        print(f"JSON tokens written to: {path}")


if __name__ == "__main__":
    main()
