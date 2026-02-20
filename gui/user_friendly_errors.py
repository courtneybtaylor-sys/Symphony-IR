"""
User-Friendly Error Messages for Symphony-IR

Converts technical errors into plain English with actionable suggestions and help links.
"""

import re
import logging
from typing import Dict, Tuple, Optional
from enum import Enum

logger = logging.getLogger(__name__)


class ErrorSeverity(Enum):
    """Error severity levels."""
    INFO = "ℹ️"
    WARNING = "⚠️"
    ERROR = "❌"
    CRITICAL = "🚨"


class UserFriendlyError:
    """User-friendly error with suggestions and help."""

    def __init__(
        self,
        title: str,
        message: str,
        severity: ErrorSeverity = ErrorSeverity.ERROR,
        suggestions: list = None,
        help_link: str = None,
        technical_details: str = None
    ):
        """
        Initialize user-friendly error.

        Args:
            title: Error title
            message: Plain English error message
            severity: Error severity
            suggestions: List of suggested fixes
            help_link: Link to documentation
            technical_details: Original technical error (for logging)
        """
        self.title = title
        self.message = message
        self.severity = severity
        self.suggestions = suggestions or []
        self.help_link = help_link
        self.technical_details = technical_details

    def __str__(self) -> str:
        """Format as user-friendly string."""
        result = f"{self.severity.value} {self.title}\n\n"
        result += f"{self.message}\n"

        if self.suggestions:
            result += "\n✓ What you can do:\n"
            for i, suggestion in enumerate(self.suggestions, 1):
                result += f"  {i}. {suggestion}\n"

        if self.help_link:
            result += f"\n📚 Learn more: {self.help_link}"

        return result

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "title": self.title,
            "message": self.message,
            "severity": self.severity.name,
            "suggestions": self.suggestions,
            "help_link": self.help_link,
        }


class ErrorTranslator:
    """Translate technical errors to user-friendly messages."""

    # Error patterns and their user-friendly equivalents
    ERROR_MAPPINGS = {
        # API Key errors
        r"ANTHROPIC_API_KEY": {
            "title": "API Key Not Found",
            "message": "Symphony-IR couldn't find your Anthropic API key.",
            "suggestions": [
                "Go to Settings and add your API key (get one at https://console.anthropic.com)",
                "Or switch to Ollama for free local AI models (Settings → Provider: Ollama)",
                "Click the help icon next to API Key for detailed instructions",
            ],
            "help_link": "https://console.anthropic.com/account/api-keys",
        },

        r"api_key.*invalid|invalid.*api|401|Unauthorized": {
            "title": "API Key Invalid",
            "message": "Your API key isn't working. It may be incorrect, expired, or disabled.",
            "suggestions": [
                "Double-check your API key (copy from https://console.anthropic.com)",
                "Make sure there are no extra spaces or characters",
                "Check that your account is active and not suspended",
                "Try getting a new key from the Anthropic console",
            ],
            "help_link": "https://console.anthropic.com/account/api-keys",
        },

        # Connection errors
        r"Connection refused|Failed to connect|ECONNREFUSED": {
            "title": "Can't Connect to AI Service",
            "message": "Symphony-IR couldn't reach the AI service.",
            "suggestions": [
                "If using Claude: Check your internet connection",
                "If using Ollama: Make sure Ollama is running (run 'ollama serve')",
                "Check that the service is running on the correct address",
                "Try restarting the service and try again",
            ],
            "help_link": "https://github.com/courtneybtaylor-sys/Symphony-IR/docs/TROUBLESHOOTING.md",
        },

        r"timeout|timed out|ETIMEDOUT": {
            "title": "Request Timed Out",
            "message": "The AI service took too long to respond.",
            "suggestions": [
                "The service might be overloaded - try again in a moment",
                "If using Ollama: Your computer might not be fast enough - try a smaller model",
                "If using Claude: Your internet connection might be slow",
                "Check that your internet connection is stable",
            ],
            "help_link": "https://docs.anthropic.com/troubleshooting",
        },

        # Ollama errors
        r"ollama|OLLAMA": {
            "title": "Ollama Connection Problem",
            "message": "Symphony-IR couldn't connect to your Ollama server.",
            "suggestions": [
                "Make sure Ollama is installed: https://ollama.ai",
                "Start Ollama by running: ollama serve",
                "Check the Ollama URL in Settings matches your setup",
                "If Ollama is on another computer, update the URL to that address",
                "If using default: Should be http://localhost:11434",
            ],
            "help_link": "https://github.com/courtneybtaylor-sys/Symphony-IR/docs/OLLAMA.md",
        },

        # Python/Environment errors
        r"ModuleNotFoundError|ImportError": {
            "title": "Missing Software",
            "message": "Some required software is not installed.",
            "suggestions": [
                "Run: pip install -r gui/requirements-desktop.txt",
                "Or run the Windows installer again",
                "If you built from source, reinstall dependencies",
            ],
            "help_link": "https://github.com/courtneybtaylor-sys/Symphony-IR#installation",
        },

        # File system errors
        r"No such file|FileNotFoundError|ENOENT": {
            "title": "File Not Found",
            "message": "Symphony-IR couldn't find a required file or directory.",
            "suggestions": [
                "Make sure the project directory is correct (Settings tab)",
                "Try reinitializing the project: python orchestrator.py init --project .",
                "Check that you have permission to access the file",
                "Restart Symphony-IR and try again",
            ],
            "help_link": "https://github.com/courtneybtaylor-sys/Symphony-IR#troubleshooting",
        },

        r"Permission denied|PermissionError|EACCES": {
            "title": "Permission Problem",
            "message": "Symphony-IR doesn't have permission to access a file or directory.",
            "suggestions": [
                "Try running Symphony-IR as Administrator",
                "Check that you own the .orchestrator directory",
                "Make sure the file isn't read-only",
                "Try saving to a different directory",
            ],
            "help_link": "https://github.com/courtneybtaylor-sys/Symphony-IR/docs/WINDOWS-SETUP.md",
        },

        # Model/Task errors
        r"model|not found|doesn't exist|invalid": {
            "title": "Model Not Found",
            "message": "The AI model you selected isn't available.",
            "suggestions": [
                "If using Ollama: Pull the model (ollama pull mistral)",
                "If using Claude: Make sure your API key is valid",
                "Try selecting a different model in Settings",
                "Check that the model name is spelled correctly",
            ],
            "help_link": "https://github.com/courtneybtaylor-sys/Symphony-IR/docs/OLLAMA.md#available-models",
        },

        # Memory/resource errors
        r"out of memory|OutOfMemory|MemoryError": {
            "title": "Not Enough Memory",
            "message": "Symphony-IR or the AI model ran out of memory.",
            "suggestions": [
                "Close other applications to free up memory",
                "If using Ollama: Use a smaller model (mistral instead of dolphin-mixtral)",
                "Try restarting your computer",
                "Upgrade to more RAM for better performance",
            ],
            "help_link": "https://github.com/courtneybtaylor-sys/Symphony-IR/docs/WINDOWS-SETUP.md#system-requirements",
        },

        # JSON/Parsing errors
        r"JSON|parse error|invalid.*format": {
            "title": "Data Format Problem",
            "message": "Symphony-IR had trouble reading or understanding data.",
            "suggestions": [
                "Try restarting Symphony-IR",
                "Check that your project directory isn't corrupted",
                "Try reinitializing the project",
                "Contact support if the problem persists",
            ],
            "help_link": "https://github.com/courtneybtaylor-sys/Symphony-IR/issues",
        },
    }

    @classmethod
    def translate(
        cls,
        technical_error: str,
        error_type: str = "generic"
    ) -> UserFriendlyError:
        """
        Translate a technical error to user-friendly format.

        Args:
            technical_error: Original technical error message
            error_type: Type of error (optional for better matching)

        Returns:
            UserFriendlyError object
        """
        technical_error = str(technical_error).strip()

        # Try to match against patterns
        for pattern, mapping in cls.ERROR_MAPPINGS.items():
            if re.search(pattern, technical_error, re.IGNORECASE):
                logger.debug(f"Matched error pattern: {pattern}")
                return UserFriendlyError(
                    title=mapping["title"],
                    message=mapping["message"],
                    suggestions=mapping["suggestions"],
                    help_link=mapping.get("help_link"),
                    technical_details=technical_error,
                )

        # Default error if no pattern matched
        return cls._create_default_error(technical_error)

    @classmethod
    def _create_default_error(cls, technical_error: str) -> UserFriendlyError:
        """Create default error for unknown errors."""
        return UserFriendlyError(
            title="Something Went Wrong",
            message=f"Symphony-IR encountered an unexpected error: {technical_error[:100]}",
            suggestions=[
                "Try restarting Symphony-IR",
                "Check that your configuration is correct (Settings tab)",
                "Try a different task or template",
                "Check the documentation for similar issues",
            ],
            help_link="https://github.com/courtneybtaylor-sys/Symphony-IR/issues",
            technical_details=technical_error,
        )


class ErrorHandler:
    """Global error handler for Symphony-IR."""

    @staticmethod
    def handle_error(
        error: Exception,
        context: str = None,
        show_technical: bool = False
    ) -> UserFriendlyError:
        """
        Handle an error and return user-friendly message.

        Args:
            error: Exception to handle
            context: Context where error occurred
            show_technical: Whether to include technical details

        Returns:
            UserFriendlyError with friendly message and suggestions
        """
        error_str = str(error)
        error_type = type(error).__name__

        logger.error(
            f"Error in {context or 'unknown context'}: {error_type}: {error_str}",
            exc_info=True
        )

        user_error = ErrorTranslator.translate(error_str, error_type)

        if show_technical:
            user_error.technical_details = f"{error_type}: {error_str}"

        return user_error

    @staticmethod
    def format_error_for_ui(user_error: UserFriendlyError) -> str:
        """
        Format error for display in UI.

        Args:
            user_error: UserFriendlyError object

        Returns:
            Formatted string for UI display
        """
        return str(user_error)


# Common error helpers
def get_api_key_error() -> UserFriendlyError:
    """Get API key error message."""
    return UserFriendlyError(
        title="API Key Required",
        message="You need to add your API key to use Claude.",
        suggestions=[
            "Get a free API key from https://console.anthropic.com",
            "Go to Settings tab and paste your key",
            "Or switch to Ollama for free local AI (Settings → Provider: Ollama)",
        ],
        help_link="https://console.anthropic.com/account/api-keys",
    )


def get_ollama_not_running_error() -> UserFriendlyError:
    """Get Ollama not running error message."""
    return UserFriendlyError(
        title="Ollama Not Running",
        message="Ollama server is not running.",
        suggestions=[
            "Open Command Prompt or PowerShell",
            "Run: ollama serve",
            "Wait for 'Listening on 127.0.0.1:11434' message",
            "Then try your task again in Symphony-IR",
        ],
        help_link="https://github.com/courtneybtaylor-sys/Symphony-IR/docs/OLLAMA.md",
    )


def get_model_not_available_error(model_name: str) -> UserFriendlyError:
    """Get model not available error message."""
    return UserFriendlyError(
        title=f"Model '{model_name}' Not Available",
        message=f"The model {model_name} is not currently available.",
        suggestions=[
            f"Run: ollama pull {model_name}" if model_name else "Pull a model with: ollama pull mistral",
            "Then try your task again",
            "Or select a different model in Settings",
        ],
        help_link="https://ollama.ai/library",
    )


def get_internet_error() -> UserFriendlyError:
    """Get internet connection error message."""
    return UserFriendlyError(
        title="Internet Connection Problem",
        message="Symphony-IR can't reach the internet.",
        suggestions=[
            "Check your internet connection",
            "Try connecting to WiFi or Ethernet",
            "Check if your firewall is blocking Symphony-IR",
            "Try again in a few moments",
        ],
        help_link="https://github.com/courtneybtaylor-sys/Symphony-IR/docs/TROUBLESHOOTING.md",
    )
