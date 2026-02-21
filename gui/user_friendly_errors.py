"""
User-Friendly Error Messages for Symphony-IR

Converts technical errors into plain English with actionable suggestions and help links.
"""

import os
import re
import logging
import platform
from typing import Dict, Optional
from enum import Enum

logger = logging.getLogger(__name__)

_OS = platform.system()   # 'Windows', 'Darwin', 'Linux'


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

    # Error patterns and their user-friendly equivalents.
    # Ordered from most-specific to most-general — first match wins.
    ERROR_MAPPINGS = {
        # ── API Key ───────────────────────────────────────────────────────────
        r"ANTHROPIC_API_KEY": {
            "title": "API Key Not Set",
            "message": "Symphony-IR couldn't find your Anthropic API key.",
            "suggestions": [
                "Go to Settings and paste your API key",
                "Get a free key at https://console.anthropic.com",
                "Or switch to Ollama (Settings → Provider: Ollama) for free local AI",
            ],
            "help_link": "https://console.anthropic.com/account/api-keys",
            "severity": ErrorSeverity.ERROR,
        },
        r"api_key.*invalid|invalid.*api_key|AuthenticationError": {
            "title": "API Key Rejected",
            "message": "Your API key was rejected. It may be wrong, expired, or disabled.",
            "suggestions": [
                "Copy your key exactly from https://console.anthropic.com",
                "Make sure there are no extra spaces before or after the key",
                "Check that your account hasn't been suspended",
                "Create a new key if yours is expired",
            ],
            "help_link": "https://console.anthropic.com/account/api-keys",
            "severity": ErrorSeverity.ERROR,
        },
        r"401|Unauthorized": {
            "title": "Not Authorized",
            "message": "The AI service rejected the request — your credentials may be wrong.",
            "suggestions": [
                "Re-enter your API key in Settings",
                "Confirm the key has not expired",
                "If using a custom endpoint, verify the URL and credentials",
            ],
            "help_link": "https://console.anthropic.com/account/api-keys",
            "severity": ErrorSeverity.ERROR,
        },
        r"429|rate.?limit|RateLimitError|too many requests": {
            "title": "Rate Limit Hit",
            "message": "You've sent too many requests to the AI service in a short time.",
            "suggestions": [
                "Wait 30–60 seconds and try again",
                "Reduce the number of parallel agents in Settings",
                "Check your plan limits at https://console.anthropic.com",
                "Consider upgrading to a higher-tier plan for more capacity",
            ],
            "help_link": "https://docs.anthropic.com/claude/reference/rate-limits",
            "severity": ErrorSeverity.WARNING,
        },
        r"402|Payment Required|billing|quota exceeded|insufficient_quota": {
            "title": "Account Billing Issue",
            "message": "Your account has run out of credits or has a billing problem.",
            "suggestions": [
                "Add credits to your account at https://console.anthropic.com/billing",
                "Check your usage limits and billing status",
                "Or switch to Ollama (free, local) in Settings",
            ],
            "help_link": "https://console.anthropic.com/billing",
            "severity": ErrorSeverity.CRITICAL,
        },

        # ── Network / Connectivity ─────────────────────────────────────────────
        r"Connection refused|Failed to connect|ECONNREFUSED|ConnectionRefusedError": {
            "title": "Connection Refused",
            "message": "Symphony-IR couldn't reach the AI service — nothing is listening at that address.",
            "suggestions": [
                "If using Claude: Check your internet connection",
                "If using Ollama: Start it by running 'ollama serve'",
                "Confirm the service URL in Settings is correct",
                "Check your firewall isn't blocking the connection",
            ],
            "help_link": "https://github.com/courtneybtaylor-sys/Symphony-IR/blob/main/docs/TROUBLESHOOTING.md",
            "severity": ErrorSeverity.ERROR,
        },
        r"timeout|timed out|ETIMEDOUT|ReadTimeoutError|ConnectTimeout": {
            "title": "Request Timed Out",
            "message": "The AI service took too long to respond.",
            "suggestions": [
                "The service may be busy — wait a moment and try again",
                "If using Ollama: A smaller model (mistral) responds faster",
                "Check your internet connection speed",
                "Increase the timeout in Settings if you're running large tasks",
            ],
            "help_link": "https://github.com/courtneybtaylor-sys/Symphony-IR/blob/main/docs/TROUBLESHOOTING.md",
            "severity": ErrorSeverity.WARNING,
        },
        r"SSL|CERTIFICATE_VERIFY_FAILED|ssl.SSLError": {
            "title": "SSL / HTTPS Problem",
            "message": "There's a security certificate problem with the connection.",
            "suggestions": [
                "Check your system date and time are correct",
                "Update your Python SSL certificates: pip install --upgrade certifi",
                "If behind a corporate proxy, ask IT to whitelist the AI service",
                "Try connecting from a different network",
            ],
            "help_link": "https://github.com/courtneybtaylor-sys/Symphony-IR/blob/main/docs/TROUBLESHOOTING.md#ssl",
            "severity": ErrorSeverity.ERROR,
        },
        r"Name or service not known|Temporary failure in name resolution|getaddrinfo": {
            "title": "DNS / Internet Problem",
            "message": "Symphony-IR can't reach the internet — DNS lookup failed.",
            "suggestions": [
                "Check that your computer is connected to the internet",
                "Try opening a browser to test connectivity",
                "Restart your router or switch to a different network",
                "Or use Ollama (local AI) — no internet needed",
            ],
            "help_link": "https://github.com/courtneybtaylor-sys/Symphony-IR/blob/main/docs/TROUBLESHOOTING.md",
            "severity": ErrorSeverity.ERROR,
        },
        r"ProxyError|407|proxy": {
            "title": "Proxy Configuration Problem",
            "message": "The connection is failing because of a proxy server.",
            "suggestions": [
                "Configure HTTPS_PROXY environment variable if behind a corporate proxy",
                "Ask your IT team for the correct proxy settings",
                "Or connect directly without a proxy if possible",
                "Use Ollama for completely offline/local AI",
            ],
            "help_link": "https://github.com/courtneybtaylor-sys/Symphony-IR/blob/main/docs/TROUBLESHOOTING.md#proxy",
            "severity": ErrorSeverity.ERROR,
        },

        # ── Ollama ────────────────────────────────────────────────────────────
        r"ollama.*not.*found|pull.*model|model.*not.*found.*ollama": {
            "title": "Ollama Model Not Downloaded",
            "message": "The Ollama model you selected hasn't been downloaded yet.",
            "suggestions": [
                "Download it by running: ollama pull mistral",
                "Or: ollama pull llama2",
                "See available models at: https://ollama.ai/library",
                "After downloading, try your task again",
            ],
            "help_link": "https://ollama.ai/library",
            "severity": ErrorSeverity.ERROR,
        },
        r"ollama|OLLAMA_BASE_URL|localhost:11434": {
            "title": "Ollama Not Running",
            "message": "Symphony-IR couldn't connect to Ollama at localhost:11434.",
            "suggestions": [
                "Start Ollama: open a terminal and run 'ollama serve'",
                "Check Ollama is installed from https://ollama.ai",
                "Verify the Ollama URL in Settings (default: http://localhost:11434)",
                "If Ollama is on another machine, update the URL in Settings",
            ],
            "help_link": "https://github.com/courtneybtaylor-sys/Symphony-IR/blob/main/docs/PROVIDERS.md#ollama",
            "severity": ErrorSeverity.ERROR,
        },

        # ── Python / Environment ──────────────────────────────────────────────
        r"No module named '(.*)'|ModuleNotFoundError: No module": {
            "title": "Missing Python Package",
            "message": "A required Python package is not installed.",
            "suggestions": [
                "Run: pip install -r gui/requirements-desktop.txt",
                "Or run the platform installer script again",
                "If you see a specific package name in the error, install it: pip install <package>",
            ],
            "help_link": "https://github.com/courtneybtaylor-sys/Symphony-IR/blob/main/docs/TROUBLESHOOTING.md#dependencies",
            "severity": ErrorSeverity.CRITICAL,
        },
        r"ImportError|cannot import name": {
            "title": "Import Error",
            "message": "A Python module failed to load — the package may be the wrong version.",
            "suggestions": [
                "Run: pip install -r gui/requirements-desktop.txt --upgrade",
                "Try creating a fresh virtual environment",
                "Ensure you're using Python 3.9 or higher",
            ],
            "help_link": "https://github.com/courtneybtaylor-sys/Symphony-IR/blob/main/docs/TROUBLESHOOTING.md#dependencies",
            "severity": ErrorSeverity.CRITICAL,
        },
        r"python.*version|requires python|python 3\.[0-8]": {
            "title": "Python Version Too Old",
            "message": "Symphony-IR requires Python 3.9 or newer.",
            "suggestions": [
                "Download Python 3.11 from https://python.org",
                "Install it and re-run the Symphony-IR installer",
                "Check your version: python --version",
            ],
            "help_link": "https://www.python.org/downloads/",
            "severity": ErrorSeverity.CRITICAL,
        },

        # ── File System ───────────────────────────────────────────────────────
        r"No such file or directory.*orchestrator|orchestrator.*not found": {
            "title": "Orchestrator Not Found",
            "message": "The orchestrator.py script couldn't be found at the expected path.",
            "suggestions": [
                "Make sure you cloned or extracted Symphony-IR completely",
                "Check the 'Project Directory' in Settings points to your Symphony-IR folder",
                "Re-download Symphony-IR if files are missing",
            ],
            "help_link": "https://github.com/courtneybtaylor-sys/Symphony-IR/blob/main/docs/TROUBLESHOOTING.md",
            "severity": ErrorSeverity.CRITICAL,
        },
        r"No such file|FileNotFoundError|ENOENT": {
            "title": "File Not Found",
            "message": "Symphony-IR couldn't find a required file or directory.",
            "suggestions": [
                "Check the project directory in Settings is correct",
                "Initialize the project: python orchestrator.py init --project .",
                "Make sure the file path doesn't contain special characters",
                "Try restarting Symphony-IR",
            ],
            "help_link": "https://github.com/courtneybtaylor-sys/Symphony-IR/blob/main/docs/TROUBLESHOOTING.md",
            "severity": ErrorSeverity.ERROR,
        },
        r"Permission denied|PermissionError|EACCES|Access is denied": {
            "title": "Permission Denied",
            "message": "Symphony-IR doesn't have permission to read or write a file.",
            "suggestions": [
                "Run Symphony-IR as Administrator (Windows) or with sudo (Mac/Linux)",
                "Check that the .orchestrator folder isn't owned by a different user",
                "Make sure the file or folder isn't marked read-only",
                "Try moving your project to a folder you own (e.g. Documents)",
            ],
            "help_link": "https://github.com/courtneybtaylor-sys/Symphony-IR/blob/main/docs/TROUBLESHOOTING.md#permissions",
            "severity": ErrorSeverity.ERROR,
        },
        r"disk.*full|no space left|ENOSPC|DiskFull": {
            "title": "Disk Full",
            "message": "Your disk is full — Symphony-IR can't save files.",
            "suggestions": [
                "Free up disk space by deleting unused files",
                "Delete old session files in .orchestrator/runs/",
                "Move Symphony-IR to a drive with more space",
            ],
            "help_link": "https://github.com/courtneybtaylor-sys/Symphony-IR/blob/main/docs/TROUBLESHOOTING.md",
            "severity": ErrorSeverity.CRITICAL,
        },

        # ── YAML / Configuration ──────────────────────────────────────────────
        r"yaml.*error|YAMLError|could not.*load.*yaml|invalid yaml": {
            "title": "Configuration File Error",
            "message": "Symphony-IR couldn't read the agents.yaml configuration file.",
            "suggestions": [
                "Check .orchestrator/agents.yaml for syntax errors (incorrect indentation is common)",
                "Validate YAML at https://yaml-online-parser.appspot.com/",
                "Restore default config: python orchestrator.py init --project . --reset",
                "Make sure all strings with special characters are quoted",
            ],
            "help_link": "https://github.com/courtneybtaylor-sys/Symphony-IR/blob/main/docs/CLI.md#configuration",
            "severity": ErrorSeverity.ERROR,
        },
        r"agents\.yaml.*not found|No agents config": {
            "title": "Agents Not Configured",
            "message": "No agents.yaml configuration file found.",
            "suggestions": [
                "Run: python orchestrator.py init --project .",
                "This creates a default agents.yaml with Claude configuration",
                "Then add your API key and run again",
            ],
            "help_link": "https://github.com/courtneybtaylor-sys/Symphony-IR/blob/main/docs/CLI.md#configuration",
            "severity": ErrorSeverity.WARNING,
        },

        # ── Context Length / Model Limits ─────────────────────────────────────
        r"context.*length|maximum.*tokens|too long|exceeds.*limit|token.*limit": {
            "title": "Task Too Long for Model",
            "message": "Your task or context is longer than the AI model can handle at once.",
            "suggestions": [
                "Break your task into smaller pieces",
                "Reduce the number of context files included",
                "Use a model with a larger context window (e.g. claude-sonnet-4)",
                "Lower the max_context_refs setting in agents.yaml",
            ],
            "help_link": "https://github.com/courtneybtaylor-sys/Symphony-IR/blob/main/docs/TROUBLESHOOTING.md#context",
            "severity": ErrorSeverity.WARNING,
        },

        # ── Memory / Resources ────────────────────────────────────────────────
        r"out of memory|OutOfMemory|MemoryError|Cannot allocate|OOM": {
            "title": "Out of Memory",
            "message": "Symphony-IR or the AI model ran out of RAM.",
            "suggestions": [
                "Close other applications to free up memory",
                "If using Ollama: Switch to a smaller model (mistral ~5GB vs dolphin-mixtral ~45GB)",
                "Add more RAM to your system (8GB minimum, 16GB recommended)",
                "Restart your computer to clear memory",
            ],
            "help_link": "https://github.com/courtneybtaylor-sys/Symphony-IR/blob/main/docs/TROUBLESHOOTING.md#memory",
            "severity": ErrorSeverity.CRITICAL,
        },

        # ── Governance / Safety ───────────────────────────────────────────────
        r"governance.*rejected|policy.*violation|blocked by governance|BLOCKED": {
            "title": "Task Blocked by Safety Policy",
            "message": "Symphony-IR's governance layer blocked this task because it may be unsafe.",
            "suggestions": [
                "Rephrase your task to avoid keywords like 'delete all', 'drop database', or 'rm -rf'",
                "If this is a legitimate task, review governance settings in agents.yaml",
                "Check the governance policy in .orchestrator/logs/symphony.log for details",
            ],
            "help_link": "https://github.com/courtneybtaylor-sys/Symphony-IR/blob/main/docs/ARCHITECTURE.md#governance",
            "severity": ErrorSeverity.WARNING,
        },

        # ── JSON / Parsing ────────────────────────────────────────────────────
        r"JSONDecodeError|invalid.*json|json.*decode|Expecting.*value": {
            "title": "Invalid JSON Data",
            "message": "Symphony-IR received data it couldn't parse.",
            "suggestions": [
                "The AI may have returned malformed output — try the task again",
                "If loading a session file, make sure the file isn't corrupted",
                "Clear the .orchestrator/runs/ directory and try a fresh run",
            ],
            "help_link": "https://github.com/courtneybtaylor-sys/Symphony-IR/issues",
            "severity": ErrorSeverity.ERROR,
        },

        # ── Git ───────────────────────────────────────────────────────────────
        r"not a git repository|git.*error|GitCommandError": {
            "title": "Git Not Available",
            "message": "Git context collection failed — the project may not be a Git repository.",
            "suggestions": [
                "This is usually harmless — Symphony-IR will skip Git context",
                "To use Git context: run 'git init' in your project folder",
                "To suppress: remove GitContext from context providers in agents.yaml",
            ],
            "help_link": "https://github.com/courtneybtaylor-sys/Symphony-IR/blob/main/docs/CLI.md",
            "severity": ErrorSeverity.INFO,
        },

        # ── Process / Subprocess ──────────────────────────────────────────────
        r"Traceback|Segmentation fault|core dumped": {
            "title": "Unexpected Crash",
            "message": "Symphony-IR crashed unexpectedly.",
            "suggestions": [
                "Check the log file at .orchestrator/logs/symphony.log for details",
                "Try restarting Symphony-IR",
                "Report this at https://github.com/courtneybtaylor-sys/Symphony-IR/issues",
                "Include the log file when reporting",
            ],
            "help_link": "https://github.com/courtneybtaylor-sys/Symphony-IR/issues",
            "severity": ErrorSeverity.CRITICAL,
        },
        r"KeyboardInterrupt|SIGINT|cancelled": {
            "title": "Task Cancelled",
            "message": "The task was cancelled by the user.",
            "suggestions": [
                "Run the task again to restart",
                "Partial results may be saved in .orchestrator/runs/",
            ],
            "help_link": None,
            "severity": ErrorSeverity.INFO,
        },

        # ── Catch-all model errors ────────────────────────────────────────────
        r"model.*not found|no such model|pull model": {
            "title": "Model Not Available",
            "message": "The AI model you selected isn't available.",
            "suggestions": [
                "If using Ollama: download it with 'ollama pull mistral'",
                "If using Claude: verify your API key is valid",
                "Select a different model in Settings",
                "See available models at https://ollama.ai/library",
            ],
            "help_link": "https://github.com/courtneybtaylor-sys/Symphony-IR/blob/main/docs/PROVIDERS.md",
            "severity": ErrorSeverity.ERROR,
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
                    severity=mapping.get("severity", ErrorSeverity.ERROR),
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


class CLIErrorFormatter:
    """Format UserFriendlyError objects for terminal / CLI output."""

    # ANSI colour codes — disabled on Windows unless ANSICON or WT_SESSION is set
    _USE_COLOUR = (
        _OS != "Windows"
        or os.environ.get("ANSICON")
        or os.environ.get("WT_SESSION")
        or os.environ.get("TERM_PROGRAM")
    )

    _COLOURS = {
        "red":    "\033[91m",
        "yellow": "\033[93m",
        "cyan":   "\033[96m",
        "green":  "\033[92m",
        "dim":    "\033[2m",
        "bold":   "\033[1m",
        "reset":  "\033[0m",
    }

    @classmethod
    def _c(cls, colour: str, text: str) -> str:
        if not cls._USE_COLOUR:
            return text
        return f"{cls._COLOURS.get(colour, '')}{text}{cls._COLOURS['reset']}"

    @classmethod
    def format(cls, err: "UserFriendlyError", show_technical: bool = False) -> str:
        """Return a formatted multi-line CLI error string."""
        sev = err.severity
        if sev == ErrorSeverity.CRITICAL:
            colour, prefix = "red",    "🚨 CRITICAL"
        elif sev == ErrorSeverity.ERROR:
            colour, prefix = "red",    "❌ ERROR"
        elif sev == ErrorSeverity.WARNING:
            colour, prefix = "yellow", "⚠️  WARNING"
        else:
            colour, prefix = "cyan",   "ℹ️  INFO"

        lines = [
            "",
            cls._c(colour, f"{prefix}: {err.title}"),
            cls._c("bold",  err.message),
        ]

        if err.suggestions:
            lines.append("")
            lines.append(cls._c("green", "What you can do:"))
            for i, s in enumerate(err.suggestions, 1):
                lines.append(f"  {i}. {s}")

        if err.help_link:
            lines.append("")
            lines.append(cls._c("dim", f"📚 Docs: {err.help_link}"))

        if show_technical and err.technical_details:
            lines.append("")
            lines.append(cls._c("dim", f"Technical: {err.technical_details[:200]}"))

        lines.append("")
        return "\n".join(lines)

    @classmethod
    def print_error(cls, err: "UserFriendlyError", show_technical: bool = False) -> None:
        """Print a formatted error to stderr."""
        import sys
        print(cls.format(err, show_technical=show_technical), file=sys.stderr)

    @classmethod
    def translate_and_print(cls, technical_error: str, context: str = None) -> None:
        """Translate a raw technical error and print it to stderr."""
        err = ErrorTranslator.translate(str(technical_error), context or "")
        cls.print_error(err)


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
