"""
Symphony-IR Desktop GUI Widgets Library

Custom PyQt6 widgets with "Deterministic Elegance" design system.
Includes styling, animations, and theme support.
"""

from .colors import (
    ColorPalette,
    ThemeManager,
    get_theme,
    set_dark_mode,
    LIGHT_PALETTE,
    DARK_PALETTE,
)

from .animations import (
    SmoothColorAnimation,
    LiftButtonAnimation,
    PulseAnimation,
    RotationAnimation,
    FocusGlowAnimation,
    ANIMATION_PRESETS,
)

from .base import (
    StyledWidget,
    PrimaryButton,
    SecondaryButton,
    DangerButton,
    StyledLineEdit,
    StyledTextEdit,
    StyledCheckBox,
    StyledLabel,
    GradientBorder,
    GlassmorphicPanel,
)

from .buttons import (
    SuccessButton,
    WarningButton,
    CopyButton,
    IconButton,
    ToggleButton,
)

from .cards import (
    GradientCard,
    GlassmorphicCard,
    MetricsCard,
    StatusCard,
)

from .inputs import (
    GradientBorderedInput,
    VariableInputGroup,
    StyledComboBox,
    StyledSpinBox,
)

from .displays import (
    SyntaxHighlightedLog,
    StatusBadge,
    JsonViewer,
    ProgressCard,
    HeaderLabel,
    SubtitleLabel,
)

from .layouts import (
    SplitViewPanel,
    TabPanel,
    CollapsibleSection,
    ResponsiveGrid,
)

from .interactive import (
    InteractiveFlowTree,
    Breadcrumb,
    ProgressIndicator,
)

__all__ = [
    # Colors & Theme
    "ColorPalette",
    "ThemeManager",
    "get_theme",
    "set_dark_mode",
    "LIGHT_PALETTE",
    "DARK_PALETTE",

    # Animations
    "SmoothColorAnimation",
    "LiftButtonAnimation",
    "PulseAnimation",
    "RotationAnimation",
    "FocusGlowAnimation",
    "ANIMATION_PRESETS",

    # Base Components
    "StyledWidget",
    "PrimaryButton",
    "SecondaryButton",
    "DangerButton",
    "StyledLineEdit",
    "StyledTextEdit",
    "StyledCheckBox",
    "StyledLabel",
    "GradientBorder",
    "GlassmorphicPanel",

    # Button Variants
    "SuccessButton",
    "WarningButton",
    "CopyButton",
    "IconButton",
    "ToggleButton",

    # Cards
    "GradientCard",
    "GlassmorphicCard",
    "MetricsCard",
    "StatusCard",

    # Inputs
    "GradientBorderedInput",
    "VariableInputGroup",
    "StyledComboBox",
    "StyledSpinBox",

    # Displays
    "SyntaxHighlightedLog",
    "StatusBadge",
    "JsonViewer",
    "ProgressCard",
    "HeaderLabel",
    "SubtitleLabel",

    # Layouts
    "SplitViewPanel",
    "TabPanel",
    "CollapsibleSection",
    "ResponsiveGrid",

    # Interactive
    "InteractiveFlowTree",
    "Breadcrumb",
    "ProgressIndicator",
]
