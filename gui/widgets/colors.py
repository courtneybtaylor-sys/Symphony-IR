"""
Color system and theme management for Symphony-IR desktop GUI.

Imports colors from design_tokens.py and provides PyQt6-compatible
color definitions for both light and dark modes.
"""

from __future__ import annotations

from PyQt6.QtGui import QColor
from dataclasses import dataclass
from typing import Dict


@dataclass
class ColorPalette:
    """Light/dark mode color palette for consistent theming."""

    # Primary colors
    primary: str
    primary_dark: str
    primary_light: str

    # Semantic colors
    success: str
    warning: str
    error: str
    info: str

    # Neutral colors
    background: str
    surface: str
    surface_variant: str
    text_primary: str
    text_secondary: str
    border: str
    border_light: str

    # Accent
    accent: str

    # Gradient colors
    gradient_start: str  # Cyan
    gradient_end: str    # Purple/Violet

    def to_qcolor(self, color_name: str) -> QColor:
        """Convert color name to QColor."""
        return QColor(getattr(self, color_name, "#000000"))

    def to_qcolor_rgba(self, color_name: str, alpha: int = 255) -> QColor:
        """Convert color to QColor with alpha."""
        color = self.to_qcolor(color_name)
        color.setAlpha(alpha)
        return color


# Light theme palette - extracted from design_tokens.py
LIGHT_PALETTE = ColorPalette(
    primary="#3B82F6",              # Blue-500
    primary_dark="#1D4ED8",         # Blue-700
    primary_light="#93C5FD",        # Blue-300
    success="#22C55E",              # Green-500
    warning="#F59E0B",              # Amber-500
    error="#EF4444",                # Red-500
    info="#06B6D4",                 # Cyan-500
    background="#FFFFFF",           # White
    surface="#F8FAFC",              # Slate-50
    surface_variant="#F1F5F9",      # Slate-100
    text_primary="#0F172A",         # Slate-900
    text_secondary="#475569",       # Slate-600
    border="#E2E8F0",               # Slate-200
    border_light="#F1F5F9",         # Slate-100
    accent="#8B5CF6",               # Violet-500
    gradient_start="#06B6D4",       # Cyan-500
    gradient_end="#8B5CF6",         # Violet-500
)

# Dark theme palette
DARK_PALETTE = ColorPalette(
    primary="#60A5FA",              # Blue-400
    primary_dark="#3B82F6",         # Blue-500
    primary_light="#BFDBFE",        # Blue-200
    success="#4ADE80",              # Green-400
    warning="#FBBF24",              # Amber-400
    error="#F87171",                # Red-400
    info="#06B6D4",                 # Cyan-500
    background="#0F172A",           # Slate-900
    surface="#1E293B",              # Slate-800
    surface_variant="#334155",      # Slate-700
    text_primary="#F8FAFC",         # Slate-50
    text_secondary="#CBD5E1",       # Slate-300
    border="#334155",               # Slate-700
    border_light="#475569",         # Slate-600
    accent="#A78BFA",               # Violet-400
    gradient_start="#06B6D4",       # Cyan-500
    gradient_end="#A78BFA",         # Violet-400
)


class ThemeManager:
    """Manages light/dark mode switching and color access."""

    def __init__(self, dark_mode: bool = False):
        self.dark_mode = dark_mode
        self._palette = DARK_PALETTE if dark_mode else LIGHT_PALETTE

    @property
    def palette(self) -> ColorPalette:
        """Get current color palette."""
        return self._palette

    def set_dark_mode(self, dark: bool):
        """Switch between light and dark themes."""
        self.dark_mode = dark
        self._palette = DARK_PALETTE if dark else LIGHT_PALETTE

    def get_color(self, color_name: str) -> QColor:
        """Get a color by name from current palette."""
        return self._palette.to_qcolor(color_name)

    def get_color_rgba(self, color_name: str, alpha: int = 255) -> QColor:
        """Get a color with alpha from current palette."""
        return self._palette.to_qcolor_rgba(color_name, alpha)

    def get_stylesheet_var(self, color_name: str) -> str:
        """Get stylesheet color variable for CSS injection."""
        color = getattr(self._palette, color_name, "#000000")
        return color


# Global theme manager instance
_theme_manager = ThemeManager(dark_mode=False)


def get_theme() -> ThemeManager:
    """Get the global theme manager."""
    return _theme_manager


def set_dark_mode(dark: bool):
    """Set global dark mode."""
    _theme_manager.set_dark_mode(dark)
