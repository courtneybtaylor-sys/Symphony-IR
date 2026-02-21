"""
Symphony-IR CLI Setup Wizard

Terminal-based first-run configuration wizard — mirrors the desktop
gui/setup_wizard.py experience for users who prefer the CLI.

Usage:
    python orchestrator.py init           # auto-launches on first run
    python orchestrator.py init --wizard  # force wizard even if already set up
"""

import sys
import time
import threading
from typing import Optional

import config as cfg

# ---------------------------------------------------------------------------
# Try to import optional "rich" for styled output; fall back to plain text.
# ---------------------------------------------------------------------------
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.prompt import Prompt, Confirm
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich.table import Table
    from rich import print as rprint
    _RICH = True
    console = Console()
except ImportError:
    _RICH = False
    console = None  # type: ignore


# ---------------------------------------------------------------------------
# Output helpers
# ---------------------------------------------------------------------------

def _print(text: str = "", style: str = "") -> None:
    if _RICH and console:
        console.print(text, style=style or None)
    else:
        print(text)


def _print_panel(title: str, content: str) -> None:
    if _RICH and console:
        console.print(Panel(content, title=title, border_style="blue"))
    else:
        print(f"\n{'='*60}")
        print(f"  {title}")
        print(f"{'='*60}")
        print(content)
        print()


def _prompt(question: str, default: str = "", password: bool = False) -> str:
    if _RICH:
        return Prompt.ask(question, default=default, password=password)
    else:
        if password:
            import getpass
            value = getpass.getpass(f"{question} [hidden]: ").strip()
        else:
            suffix = f" [{default}]" if default else ""
            value = input(f"{question}{suffix}: ").strip()
        return value or default


def _confirm(question: str, default: bool = True) -> bool:
    if _RICH:
        return Confirm.ask(question, default=default)
    else:
        suffix = " [Y/n]" if default else " [y/N]"
        answer = input(f"{question}{suffix}: ").strip().lower()
        if not answer:
            return default
        return answer in ("y", "yes")


def _choose(prompt_text: str, options: dict) -> str:
    """Present a numbered menu and return the chosen key."""
    print()
    for key, label in options.items():
        _print(f"  [{key}] {label}")
    print()
    while True:
        choice = input(f"{prompt_text}: ").strip().upper()
        if choice in options:
            return choice
        _print(f"  Invalid choice '{choice}'. Choose from: {', '.join(options)}", style="red")


# ---------------------------------------------------------------------------
# Validation helpers (run in background thread)
# ---------------------------------------------------------------------------

class _ValidationResult:
    success: bool = False
    message: str = ""


def _validate_claude(api_key: str) -> _ValidationResult:
    result = _ValidationResult()
    if not api_key or len(api_key) < 10:
        result.message = "API key is too short."
        return result
    if not api_key.startswith("sk-ant-"):
        result.message = "API key should start with 'sk-ant-'."
        return result
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)
        client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1,
            messages=[{"role": "user", "content": "ping"}],
        )
        result.success = True
        result.message = "Claude API key validated successfully."
    except Exception as exc:
        err = str(exc)
        if "401" in err or "Unauthorized" in err:
            result.message = "API key is invalid or has been revoked."
        else:
            result.message = f"Validation failed: {err}"
    return result


def _validate_ollama(host: str) -> _ValidationResult:
    result = _ValidationResult()
    try:
        import requests
        resp = requests.get(f"{host}/api/tags", timeout=3)
        if resp.status_code == 200:
            result.success = True
            result.message = f"Ollama server reachable at {host}."
        else:
            result.message = f"Ollama returned HTTP {resp.status_code}."
    except Exception as exc:
        result.message = (
            f"Could not reach Ollama at {host}.\n"
            "Make sure Ollama is installed and running."
        )
    return result


def _run_validation_with_spinner(
    provider: str,
    api_key: Optional[str],
    ollama_host: str,
) -> _ValidationResult:
    """Run validation in a thread while showing a spinner."""
    result_holder: list[_ValidationResult] = []

    def _do():
        if provider in ("claude", "both"):
            r = _validate_claude(api_key or "")
            result_holder.append(r)
        elif provider == "ollama":
            r = _validate_ollama(ollama_host)
            result_holder.append(r)

    thread = threading.Thread(target=_do, daemon=True)
    thread.start()

    if _RICH and console:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
            console=console,
        ) as progress:
            progress.add_task(
                description=f"Validating {provider} connection...", total=None
            )
            thread.join(timeout=20)
    else:
        print(f"  Validating {provider}...", end="", flush=True)
        while thread.is_alive():
            print(".", end="", flush=True)
            time.sleep(0.4)
        thread.join()
        print()

    if not result_holder:
        r = _ValidationResult()
        r.message = "Validation timed out."
        return r
    return result_holder[0]


# ---------------------------------------------------------------------------
# Wizard steps
# ---------------------------------------------------------------------------

def _step_welcome() -> None:
    _print_panel(
        "Symphony-IR Setup Wizard",
        (
            "Welcome! This wizard will guide you through:\n\n"
            "  1. Choosing your AI provider (Claude or Ollama)\n"
            "  2. Configuring your API key or server URL\n"
            "  3. Validating the connection\n\n"
            "Estimated time: 2-3 minutes.\n\n"
            "What you'll need:\n"
            "  Claude  - Free API key from console.anthropic.com\n"
            "  Ollama  - Installed from ollama.ai (free, runs locally)"
        ),
    )
    input("Press Enter to continue...")


def _step_provider() -> str:
    _print("\n[bold]Step 1 of 4 — Choose Your AI Provider[/bold]" if _RICH
           else "\nStep 1 of 4 — Choose Your AI Provider")
    _print()

    choice = _choose(
        "Provider",
        {
            "1": "Claude  (Cloud API — best for production)",
            "2": "Ollama  (Local, free — best for privacy)",
            "3": "Both    (maximum flexibility)",
        },
    )
    return {"1": "claude", "2": "ollama", "3": "both"}[choice]


def _step_api_key(provider: str) -> tuple[Optional[str], str]:
    """Returns (api_key, ollama_host)."""
    api_key = None
    ollama_host = cfg.get("ollama_host") or "http://localhost:11434"

    _print(
        f"\n[bold]Step 2 of 4 — Configure {provider.title()} Connection[/bold]"
        if _RICH
        else f"\nStep 2 of 4 — Configure {provider.title()} Connection"
    )
    _print()

    if provider in ("claude", "both"):
        _print(
            "  Get a free API key:\n"
            "  1. Visit https://console.anthropic.com\n"
            "  2. Sign up and click 'Generate API Key'\n"
            "  3. Paste it below (input is hidden)\n"
        )
        raw = _prompt("Claude API key (sk-ant-...)", password=True)
        if raw.strip():
            api_key = raw.strip()
        else:
            _print("  API key skipped — you can add it later in the Settings.", style="yellow")

    if provider in ("ollama", "both"):
        _print(
            "  Ollama does not require an API key.\n"
            "  Download from https://ollama.ai, install, then run:\n"
            "    ollama pull llama3\n"
        )
        custom = _prompt("Ollama host URL", default=ollama_host)
        if custom.strip():
            ollama_host = custom.strip()

    return api_key, ollama_host


def _step_validate(provider: str, api_key: Optional[str], ollama_host: str) -> bool:
    _print(
        "\n[bold]Step 3 of 4 — Validating Configuration[/bold]"
        if _RICH
        else "\nStep 3 of 4 — Validating Configuration"
    )
    _print()

    result = _run_validation_with_spinner(provider, api_key, ollama_host)

    if result.success:
        _print(f"  OK  {result.message}", style="green" if _RICH else "")
        return True
    else:
        _print(f"  WARN  {result.message}", style="yellow" if _RICH else "")
        if not _confirm("\nValidation did not pass. Continue anyway?", default=True):
            return False
        return True   # allow proceeding with warnings


def _step_complete(provider: str, api_key: Optional[str], ollama_host: str) -> None:
    _print(
        "\n[bold]Step 4 of 4 — Setup Complete[/bold]"
        if _RICH
        else "\nStep 4 of 4 — Setup Complete"
    )
    _print()

    if _RICH and console:
        table = Table(show_header=False, box=None, padding=(0, 2))
        table.add_row("Provider",   f"[cyan]{provider.upper()}[/cyan]")
        table.add_row("Claude Key", "[green]Configured[/green]" if api_key else "[dim]Not set[/dim]")
        table.add_row("Ollama URL", f"[cyan]{ollama_host}[/cyan]" if provider in ("ollama", "both") else "[dim]N/A[/dim]")
        table.add_row("Config",     f"[dim]{cfg.CONFIG_FILE}[/dim]")
        console.print(
            Panel(table, title="[bold green]Configuration Summary[/bold green]", border_style="green")
        )
    else:
        print("\nConfiguration Summary:")
        print(f"  Provider   : {provider.upper()}")
        print(f"  Claude Key : {'Configured' if api_key else 'Not set'}")
        if provider in ("ollama", "both"):
            print(f"  Ollama URL : {ollama_host}")
        print(f"  Config     : {cfg.CONFIG_FILE}")

    _print("\nYou can update settings any time with: python orchestrator.py init --wizard")
    _print("Happy orchestrating!\n")


# ---------------------------------------------------------------------------
# Main wizard entry point
# ---------------------------------------------------------------------------

def run_wizard(force: bool = False) -> None:
    """
    Run the CLI setup wizard.

    Args:
        force: Run even if setup has already been completed.
    """
    if not force and cfg.is_setup_complete():
        return

    try:
        _step_welcome()

        provider  = _step_provider()
        api_key, ollama_host = _step_api_key(provider)

        ok = _step_validate(provider, api_key, ollama_host)
        if not ok:
            _print("\nSetup cancelled.", style="yellow" if _RICH else "")
            return

        # Persist configuration
        configuration = {
            "setup_complete": True,
            "setup_version":  "1.0",
            "provider":       provider,
            "claude_api_key": api_key,
            "ollama_host":    ollama_host,
        }
        cfg.save(configuration)

        # Apply to current env so this session can run immediately
        cfg.apply_to_env()

        _step_complete(provider, api_key, ollama_host)

    except KeyboardInterrupt:
        _print("\n\nSetup interrupted. Run 'python orchestrator.py init' to try again.",
               style="yellow" if _RICH else "")
        sys.exit(0)


if __name__ == "__main__":
    run_wizard(force=True)
