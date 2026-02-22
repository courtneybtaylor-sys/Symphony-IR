"""Design token loader for SaaS multi-tenant theming.

Loads design_tokens.json and provides:
- get_token(path: str) — e.g., get_token("color.primary.base")
- get_theme(theme_name: str) — e.g., get_theme("light") / get_theme("dark")
- apply_custom_tokens(overrides: dict) — for tenant branding
"""

import json
from pathlib import Path
from typing import Any, Dict, Optional


class TokenLoader:
    """Load and manage design tokens from JSON file."""

    def __init__(self, token_file: Optional[Path] = None):
        """Initialize TokenLoader with design tokens.

        Args:
            token_file: Path to design_tokens.json. If None, uses default location.
        """
        if token_file is None:
            token_file = Path(__file__).parent / "design_tokens.json"

        self.token_file = token_file
        self.tokens = self._load_tokens()
        self.custom_tokens: Dict[str, str] = {}

    def _load_tokens(self) -> Dict[str, Any]:
        """Load tokens from JSON file."""
        if not self.token_file.exists():
            raise FileNotFoundError(f"Design tokens file not found: {self.token_file}")

        with open(self.token_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    def get_token(self, path: str) -> Any:
        """Get token by dot-notation path.

        Examples:
            get_token("color.primary.base") → "#1f77b4"
            get_token("spacing.md") → "16px"
            get_token("typography.font_size.lg") → "18px"

        Args:
            path: Dot-separated path to token (e.g., "color.primary.base")

        Returns:
            Token value, or None if not found
        """
        # Check custom tokens first
        if path in self.custom_tokens:
            return self.custom_tokens[path]

        # Navigate through nested dict
        keys = path.split(".")
        value = self.tokens

        for key in keys:
            if isinstance(value, dict):
                value = value.get(key, {})
            else:
                return None

        # Return 'value' field if it's a token object, else return the value
        if isinstance(value, dict) and "value" in value:
            return value["value"]

        return value if value else None

    def get_theme(self, theme: str = "light") -> Dict[str, str]:
        """Get colors for 'light' or 'dark' theme.

        Returns a flat dict of color tokens with theme variants applied.
        For tokens with theme-specific values, uses the variant; otherwise
        uses the base 'value' field.

        Args:
            theme: Theme name ("light" or "dark")

        Returns:
            Dict mapping color token paths to their values for the theme
        """
        colors: Dict[str, str] = {}

        def flatten_colors(obj: Dict[str, Any], prefix: str = "") -> None:
            """Recursively flatten color tokens."""
            for key, config in obj.items():
                path = f"{prefix}_{key}" if prefix else key

                if isinstance(config, dict):
                    if "value" in config:
                        # Token object with 'value' field
                        if theme in config:
                            # Theme-specific value
                            colors[path] = config[theme]
                        else:
                            # Use default 'value'
                            colors[path] = config["value"]
                    else:
                        # Nested object, recurse
                        flatten_colors(config, path)

        if "color" in self.tokens:
            flatten_colors(self.tokens["color"])

        return colors

    def get_all_tokens(self) -> Dict[str, Any]:
        """Get all tokens (for admin/debug purposes)."""
        return self.tokens.copy()

    def apply_custom_tokens(self, overrides: Dict[str, str]) -> None:
        """Apply tenant-specific branding overrides.

        Allows SaaS deployments to customize colors per tenant.

        Args:
            overrides: Dict mapping token paths to custom values
                      e.g., {"color.primary.base": "#custom-color"}
        """
        self.custom_tokens.update(overrides)

    def reset_custom_tokens(self) -> None:
        """Clear all custom token overrides."""
        self.custom_tokens.clear()

    def get_css_variables(self, theme: str = "light") -> str:
        """Generate CSS custom properties from tokens.

        Returns a CSS :root selector with all token values as variables.
        Useful for injecting tokens into stylesheets dynamically.

        Args:
            theme: Theme name ("light" or "dark")

        Returns:
            CSS string with :root { --var-name: value; ... }
        """
        colors = self.get_theme(theme)
        css_lines = [":root {"]

        for key, value in colors.items():
            css_key = "--" + key.replace("_", "-")
            css_lines.append(f"  {css_key}: {value};")

        css_lines.append("}")
        return "\n".join(css_lines)


# Global instance for easy access
_loader: Optional[TokenLoader] = None


def get_loader() -> TokenLoader:
    """Get or create the global TokenLoader instance."""
    global _loader
    if _loader is None:
        _loader = TokenLoader()
    return _loader


def get_token(path: str) -> Any:
    """Shorthand to get a token from the global loader."""
    return get_loader().get_token(path)


def get_theme(theme: str = "light") -> Dict[str, str]:
    """Shorthand to get theme colors from the global loader."""
    return get_loader().get_theme(theme)
