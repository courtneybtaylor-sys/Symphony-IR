"""
cli_error_handler.py — Human-friendly error messages for the Symphony-IR CLI.

No GUI or external dependencies — stdlib only.
"""

import os
import re
import sys
import platform

_OS = platform.system()

# ANSI colours: enabled on Linux/macOS; on Windows only if modern terminal
_USE_COLOUR = (
    _OS != "Windows"
    or os.environ.get("ANSICON")
    or os.environ.get("WT_SESSION")
    or os.environ.get("TERM_PROGRAM")
)

_C = {
    "red":    "\033[91m",
    "yellow": "\033[93m",
    "cyan":   "\033[96m",
    "green":  "\033[92m",
    "dim":    "\033[2m",
    "bold":   "\033[1m",
    "reset":  "\033[0m",
}


def _c(colour: str, text: str) -> str:
    return f"{_C.get(colour, '')}{text}{_C['reset']}" if _USE_COLOUR else text


# ── Error catalogue ──────────────────────────────────────────────────────────
#  Each entry: (regex_pattern, title, message, [suggestions], help_url_or_None)
#  Ordered most-specific → most-general (first match wins).

_CATALOGUE = [
    # ── API / Auth ─────────────────────────────────────────────────────────
    (
        r"ANTHROPIC_API_KEY",
        "API Key Not Set",
        "ANTHROPIC_API_KEY is missing from your environment.",
        [
            "Export it before running:  export ANTHROPIC_API_KEY=sk-...",
            "Or add it to .orchestrator/.env",
            "Get a key at https://console.anthropic.com",
            "Or switch to Ollama (free, local) — see docs/PROVIDERS.md",
        ],
        "https://console.anthropic.com/account/api-keys",
    ),
    (
        r"AuthenticationError|api_key.*invalid|invalid.*api_key|401|Unauthorized",
        "API Key Rejected",
        "The API key was rejected. It may be wrong, expired, or disabled.",
        [
            "Copy the key exactly from https://console.anthropic.com",
            "Remove any extra spaces around the key",
            "Check your account isn't suspended",
            "Create a replacement key if yours is expired",
        ],
        "https://console.anthropic.com/account/api-keys",
    ),
    (
        r"429|RateLimitError|rate.?limit|too many requests",
        "Rate Limit Hit",
        "Too many requests were sent in a short time.",
        [
            "Wait 30–60 seconds, then try again",
            "Use --no-compile to reduce API calls during debugging",
            "Check your plan limits at https://console.anthropic.com",
        ],
        "https://docs.anthropic.com/claude/reference/rate-limits",
    ),
    (
        r"402|insufficient_quota|billing|quota exceeded",
        "Billing / Quota Problem",
        "Your account has run out of credits or has a billing issue.",
        [
            "Add credits at https://console.anthropic.com/billing",
            "Check your usage limits",
            "Or switch to free local Ollama models",
        ],
        "https://console.anthropic.com/billing",
    ),

    # ── Network ────────────────────────────────────────────────────────────
    (
        r"Connection refused|ECONNREFUSED|ConnectionRefusedError",
        "Connection Refused",
        "Nothing is listening at the target address.",
        [
            "If using Claude: check your internet connection",
            "If using Ollama: start it with  ollama serve",
            "Verify the service URL in .orchestrator/agents.yaml",
        ],
        "https://github.com/courtneybtaylor-sys/Symphony-IR/blob/main/docs/TROUBLESHOOTING.md",
    ),
    (
        r"timeout|timed out|ETIMEDOUT|ReadTimeoutError|ConnectTimeout",
        "Request Timed Out",
        "The AI service took too long to respond.",
        [
            "The service may be busy — wait a moment and retry",
            "For Ollama: use a smaller/faster model (mistral vs dolphin-mixtral)",
            "Check your internet speed if using Claude",
        ],
        "https://github.com/courtneybtaylor-sys/Symphony-IR/blob/main/docs/TROUBLESHOOTING.md",
    ),
    (
        r"SSL|CERTIFICATE_VERIFY_FAILED",
        "SSL Certificate Error",
        "A TLS/SSL certificate verification failed.",
        [
            "Ensure your system clock is accurate",
            "Upgrade certificates:  pip install --upgrade certifi",
            "If behind a corporate proxy, ask IT to whitelist the AI service endpoint",
        ],
        "https://github.com/courtneybtaylor-sys/Symphony-IR/blob/main/docs/TROUBLESHOOTING.md#ssl",
    ),
    (
        r"Name or service not known|getaddrinfo|Name resolution",
        "DNS / Internet Unreachable",
        "Symphony-IR can't resolve the service hostname (DNS failure).",
        [
            "Check that your computer is connected to the internet",
            "Try: curl https://api.anthropic.com  to test connectivity",
            "Restart your router or switch networks",
            "Use Ollama for completely offline / local AI",
        ],
        None,
    ),

    # ── Ollama ─────────────────────────────────────────────────────────────
    (
        r"ollama.*not.*found|pull.*model|model.*not.*found",
        "Ollama Model Not Downloaded",
        "The selected Ollama model hasn't been pulled yet.",
        [
            "Download it:  ollama pull mistral",
            "List available models:  ollama list",
            "Browse models at https://ollama.ai/library",
        ],
        "https://ollama.ai/library",
    ),
    (
        r"ollama|localhost:11434|OLLAMA_BASE_URL",
        "Ollama Not Running",
        "Can't connect to Ollama at localhost:11434.",
        [
            "Start Ollama:  ollama serve",
            "Install Ollama from https://ollama.ai if not installed",
            "Verify OLLAMA_BASE_URL if you're using a custom port",
        ],
        "https://github.com/courtneybtaylor-sys/Symphony-IR/blob/main/docs/PROVIDERS.md#ollama",
    ),

    # ── Python Environment ─────────────────────────────────────────────────
    (
        r"No module named|ModuleNotFoundError",
        "Missing Python Package",
        "A required Python package is not installed.",
        [
            "Run:  pip install -r requirements.txt",
            "Or re-run the platform installer script",
            "If a specific package is named in the error, install it directly",
        ],
        "https://github.com/courtneybtaylor-sys/Symphony-IR/blob/main/docs/TROUBLESHOOTING.md#dependencies",
    ),
    (
        r"python.*version|requires python 3\.[0-8]",
        "Python Too Old",
        "Symphony-IR requires Python 3.9 or newer.",
        [
            "Download Python 3.11 from https://python.org",
            "Re-run the installer after upgrading",
            "Check your version:  python --version",
        ],
        "https://www.python.org/downloads/",
    ),

    # ── File System ────────────────────────────────────────────────────────
    (
        r"No such file or directory.*orchestrator|orchestrator.*not found",
        "Orchestrator Script Not Found",
        "orchestrator.py could not be found at the expected path.",
        [
            "Ensure you're running from the Symphony-IR root directory",
            "Re-clone or re-download the repository if files are missing",
        ],
        None,
    ),
    (
        r"agents\.yaml.*not found|No agents config|no agents.yaml",
        "Agents Not Configured",
        "No .orchestrator/agents.yaml file found.",
        [
            "Initialise the project first:  python orchestrator.py init --project .",
            "Then add your API key and run again",
        ],
        "https://github.com/courtneybtaylor-sys/Symphony-IR/blob/main/docs/CLI.md#configuration",
    ),
    (
        r"No such file|FileNotFoundError|ENOENT",
        "File Not Found",
        "A required file or directory doesn't exist.",
        [
            "Run  python orchestrator.py init --project .  to create missing files",
            "Check that the --project path is correct",
        ],
        None,
    ),
    (
        r"Permission denied|PermissionError|EACCES|Access is denied",
        "Permission Denied",
        "Symphony-IR doesn't have permission to read/write a file.",
        [
            "Run as Administrator (Windows) or with sudo (Mac/Linux)",
            "Check that .orchestrator/ isn't owned by another user",
            "Ensure the file isn't marked read-only",
        ],
        None,
    ),
    (
        r"no space left|ENOSPC|disk.*full",
        "Disk Full",
        "There's no disk space left to save files.",
        [
            "Delete old session files in .orchestrator/runs/",
            "Free up disk space and try again",
        ],
        None,
    ),

    # ── YAML / Config ──────────────────────────────────────────────────────
    (
        r"YAMLError|yaml.*error|could not.*load.*yaml",
        "YAML Configuration Error",
        "agents.yaml has a syntax error.",
        [
            "Check indentation — YAML uses spaces, not tabs",
            "Validate at https://yaml-online-parser.appspot.com/",
            "Restore defaults:  python orchestrator.py init --force",
        ],
        "https://github.com/courtneybtaylor-sys/Symphony-IR/blob/main/docs/CLI.md#configuration",
    ),

    # ── Context Length ─────────────────────────────────────────────────────
    (
        r"context.*length|maximum.*tokens|too long|exceeds.*limit",
        "Task Too Long for Model",
        "The task or context exceeds the model's context window.",
        [
            "Break the task into smaller pieces",
            "Reduce the number of context files with --file",
            "Lower max_context_refs in agents.yaml",
        ],
        None,
    ),

    # ── Governance ─────────────────────────────────────────────────────────
    (
        r"governance.*rejected|policy.*violation|BLOCKED|blocked by governance",
        "Task Blocked by Safety Policy",
        "The governance layer blocked this task.",
        [
            "Rephrase to avoid keywords like 'delete all', 'drop database', 'rm -rf'",
            "Review governance config in agents.yaml if this is a legitimate task",
            "Check .orchestrator/logs/symphony.log for the exact trigger",
        ],
        "https://github.com/courtneybtaylor-sys/Symphony-IR/blob/main/docs/ARCHITECTURE.md#governance",
    ),
]


def _format_error(title: str, message: str, suggestions: list, help_url: str | None) -> str:
    lines = [
        "",
        _c("red",  f"❌  {title}"),
        _c("bold", f"    {message}"),
    ]
    if suggestions:
        lines.append("")
        lines.append(_c("green", "    What you can do:"))
        for i, s in enumerate(suggestions, 1):
            lines.append(f"      {i}. {s}")
    if help_url:
        lines.append("")
        lines.append(_c("dim", f"    📚 Docs: {help_url}"))
    lines.append("")
    return "\n".join(lines)


def translate_and_print(technical_error: str, exit_code: int | None = None) -> None:
    """
    Translate a raw exception/error string to a friendly CLI message and
    print it to stderr.  Optionally call sys.exit(exit_code).
    """
    err_str = str(technical_error)

    for pattern, title, message, suggestions, help_url in _CATALOGUE:
        if re.search(pattern, err_str, re.IGNORECASE):
            print(_format_error(title, message, suggestions, help_url), file=sys.stderr)
            if exit_code is not None:
                sys.exit(exit_code)
            return

    # Default: unknown error
    short = err_str[:200] + ("…" if len(err_str) > 200 else "")
    print(
        _format_error(
            "Unexpected Error",
            short,
            [
                "Check .orchestrator/logs/symphony.log for details",
                "Try restarting Symphony-IR",
                "Report at https://github.com/courtneybtaylor-sys/Symphony-IR/issues",
            ],
            "https://github.com/courtneybtaylor-sys/Symphony-IR/issues",
        ),
        file=sys.stderr,
    )
    if exit_code is not None:
        sys.exit(exit_code)


def wrap_main(fn):
    """
    Decorator: wraps a CLI main() function and catches unhandled exceptions,
    printing a friendly message instead of a raw stack trace.

    Usage::

        @wrap_main
        def main():
            ...
    """
    import functools

    @functools.wraps(fn)
    def _wrapper(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except KeyboardInterrupt:
            print("\n\nTask cancelled.", file=sys.stderr)
            sys.exit(130)
        except SystemExit:
            raise
        except Exception as exc:
            translate_and_print(str(exc))
            sys.exit(1)

    return _wrapper
