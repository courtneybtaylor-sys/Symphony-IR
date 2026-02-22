"""
Animation utilities for Symphony-IR desktop GUI.

Provides smooth transitions and effects matching "Deterministic Elegance" design.
"""

from __future__ import annotations

from PyQt6.QtCore import (
    QPropertyAnimation,
    QEasingCurve,
    QRect,
    Qt,
    QPoint,
    QAbstractAnimation,
)
from PyQt6.QtWidgets import QWidget, QPushButton
from PyQt6.QtGui import QColor
from typing import Optional, Callable


class SmoothColorAnimation:
    """Animate color changes smoothly over time."""

    @staticmethod
    def create_color_transition(
        widget: QWidget,
        property_name: str,
        start_color: QColor,
        end_color: QColor,
        duration: int = 200,
        on_finished: Optional[Callable] = None,
    ) -> QPropertyAnimation:
        """Create a smooth color transition animation.

        Args:
            widget: Widget to animate
            property_name: Property name (e.g., "backgroundColor")
            start_color: Starting QColor
            end_color: Ending QColor
            duration: Animation duration in milliseconds
            on_finished: Callback when animation finishes

        Returns:
            QPropertyAnimation instance (already running)
        """
        anim = QPropertyAnimation(widget, property_name.encode())
        anim.setStartValue(start_color)
        anim.setEndValue(end_color)
        anim.setDuration(duration)
        anim.setEasingCurve(QEasingCurve.Type.OutCubic)

        if on_finished:
            anim.finished.connect(on_finished)

        anim.start(QAbstractAnimation.DeletionPolicy.DeleteWhenStopped)
        return anim


class LiftButtonAnimation:
    """Button lift-on-hover animation (2-4px translateY effect)."""

    @staticmethod
    def apply_lift_animation(
        button: QPushButton,
        lift_distance: int = 3,
        duration: int = 150,
    ):
        """Apply hover lift animation to button.

        Args:
            button: QPushButton to animate
            lift_distance: Pixels to lift on hover (2-4 recommended)
            duration: Animation duration in milliseconds
        """
        # Store original position
        button._original_pos = button.pos()
        button._lift_distance = lift_distance
        button._lift_duration = duration
        button._lift_anim: Optional[QPropertyAnimation] = None

        # Connect hover events
        button.enterEvent = lambda e: _on_button_enter(button)
        button.leaveEvent = lambda e: _on_button_leave(button)

        # Update stored position on move
        button.moveEvent = lambda e: _on_button_move(button, e)


def _on_button_enter(button: QPushButton):
    """Handle button enter event for lift animation."""
    if button._lift_anim:
        button._lift_anim.stop()

    button._lift_anim = QPropertyAnimation(button, b"geometry")
    start_rect = button.geometry()
    end_rect = QRect(
        start_rect.x(),
        start_rect.y() - button._lift_distance,
        start_rect.width(),
        start_rect.height(),
    )

    button._lift_anim.setStartValue(start_rect)
    button._lift_anim.setEndValue(end_rect)
    button._lift_anim.setDuration(button._lift_duration)
    button._lift_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
    button._lift_anim.start(QAbstractAnimation.DeletionPolicy.KeepWhenStopped)


def _on_button_leave(button: QPushButton):
    """Handle button leave event for lift animation."""
    if button._lift_anim:
        button._lift_anim.stop()

    button._lift_anim = QPropertyAnimation(button, b"geometry")
    end_rect = button.geometry()
    start_rect = QRect(
        end_rect.x(),
        end_rect.y() + button._lift_distance,
        end_rect.width(),
        end_rect.height(),
    )

    button._lift_anim.setStartValue(start_rect)
    button._lift_anim.setEndValue(button._original_pos if hasattr(button, '_original_pos') else QRect(end_rect.x(), end_rect.y() + button._lift_distance, end_rect.width(), end_rect.height()))
    button._lift_anim.setDuration(button._lift_duration)
    button._lift_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
    button._lift_anim.start(QAbstractAnimation.DeletionPolicy.KeepWhenStopped)


def _on_button_move(button: QPushButton, event):
    """Track button position changes."""
    if not hasattr(button, '_original_pos'):
        button._original_pos = button.pos()
    else:
        button._original_pos = button.pos()


class PulseAnimation:
    """Pulse/breathing animation for badges and indicators."""

    @staticmethod
    def create_pulse_animation(
        widget: QWidget,
        min_opacity: float = 0.5,
        max_opacity: float = 1.0,
        duration: int = 2000,
    ) -> QPropertyAnimation:
        """Create a pulsing opacity animation.

        Args:
            widget: Widget to animate
            min_opacity: Minimum opacity (0.0-1.0)
            max_opacity: Maximum opacity (0.0-1.0)
            duration: Full pulse cycle duration in milliseconds

        Returns:
            QPropertyAnimation instance (already running, looping)
        """
        anim = QPropertyAnimation(widget, b"windowOpacity")
        anim.setStartValue(min_opacity)
        anim.setEndValue(max_opacity)
        anim.setDuration(duration // 2)
        anim.setEasingCurve(QEasingCurve.Type.InOutQuad)

        # Create loop by connecting finished signal
        def _restart():
            if anim.direction() == QPropertyAnimation.Direction.Forward:
                anim.setDirection(QPropertyAnimation.Direction.Backward)
            else:
                anim.setDirection(QPropertyAnimation.Direction.Forward)
            anim.start()

        anim.finished.connect(_restart)
        anim.start()
        return anim


class RotationAnimation:
    """Continuous rotation animation for spinners/progress indicators."""

    @staticmethod
    def create_rotation_animation(
        widget: QWidget,
        duration: int = 1500,
    ) -> QPropertyAnimation:
        """Create a continuous rotation animation.

        Args:
            widget: Widget to animate
            duration: Full rotation duration in milliseconds

        Returns:
            QPropertyAnimation instance (already running, looping)
        """
        anim = QPropertyAnimation(widget, b"rotation")
        anim.setStartValue(0)
        anim.setEndValue(360)
        anim.setDuration(duration)
        anim.setEasingCurve(QEasingCurve.Type.Linear)

        # Loop the animation
        anim.finished.connect(lambda: anim.start())
        anim.start()
        return anim


class FocusGlowAnimation:
    """Focus glow effect for input fields."""

    @staticmethod
    def create_focus_glow(
        widget: QWidget,
        glow_color: QColor,
        duration: int = 200,
    ):
        """Create a focus glow effect.

        Args:
            widget: Widget to apply glow to
            glow_color: Color of the glow
            duration: Animation duration in milliseconds
        """
        # Store original shadow/glow state
        if not hasattr(widget, '_original_shadow'):
            widget._original_shadow = None
        widget._glow_color = glow_color
        widget._glow_duration = duration


# Animation presets matching "Deterministic Elegance"
ANIMATION_PRESETS = {
    'button_hover': {
        'lift_distance': 3,
        'duration': 150,
    },
    'color_transition': {
        'duration': 200,
        'easing': QEasingCurve.Type.OutCubic,
    },
    'tab_switch': {
        'duration': 300,
        'easing': QEasingCurve.Type.OutCubic,
    },
    'focus_effect': {
        'duration': 200,
        'easing': QEasingCurve.Type.OutCubic,
    },
    'pulse_badge': {
        'duration': 2000,
        'min_opacity': 0.6,
        'max_opacity': 1.0,
    },
}
