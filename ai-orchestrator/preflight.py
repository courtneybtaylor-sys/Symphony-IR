"""
preflight.py — Environment validation for Symphony-IR.

Run before any orchestration job to catch misconfigurations early
instead of failing 30 seconds into a run.

Usage (CLI):
    python orchestrator.py preflight

Usage (Python):
    from preflight import run_checks, print_report, CheckStatus
    results = run_checks(project_root, provider="claude", api_key="sk-...")
    ok = print_report(results)
"""

from __future__ import annotations

import os
import shutil
import socket
import subprocess
import sys
import platform
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional


# ── Status levels ────────────────────────────────────────────────────────────

class CheckStatus(Enum):
    PASS    = "PASS"
    WARN    = "WARN"
    FAIL    = "FAIL"
    SKIP    = "SKIP"


@dataclass
class CheckResult:
    name:    str
    status:  CheckStatus
    message: str
    fix:     str = ""       # one-line action the user should take

    @property
    def icon(self) -> str:
        return {"PASS": "✅", "WARN": "⚠️ ", "FAIL": "❌", "SKIP": "⏭️ "}[self.status.value]


# ── Individual checks ────────────────────────────────────────────────────────

def _check_python_version() -> CheckResult:
    major, minor = sys.version_info[:2]
    ver = f"{major}.{minor}.{sys.version_info.micro}"
    if major < 3 or (major == 3 and minor < 9):
        return CheckResult(
            "Python version",
            CheckStatus.FAIL,
            f"Python {ver} detected — Symphony-IR requires 3.9+",
            "Download Python 3.11 from https://python.org and re-install",
        )
    if minor < 11:
        return CheckResult(
            "Python version",
            CheckStatus.WARN,
            f"Python {ver} — works, but 3.11+ is recommended for best performance",
            "Consider upgrading to Python 3.11: https://python.org/downloads",
        )
    return CheckResult("Python version", CheckStatus.PASS, f"Python {ver} ✓")


def _check_package(pkg: str, import_name: str | None = None) -> CheckResult:
    name = import_name or pkg
    try:
        __import__(name)
        return CheckResult(f"Package: {pkg}", CheckStatus.PASS, f"{pkg} installed ✓")
    except ImportError:
        return CheckResult(
            f"Package: {pkg}",
            CheckStatus.FAIL,
            f"{pkg} is not installed",
            f"Run:  pip install {pkg}",
        )


def _check_project_structure(project_root: Path) -> CheckResult:
    orch_dir = project_root / ".orchestrator"
    if not orch_dir.exists():
        return CheckResult(
            "Project structure",
            CheckStatus.WARN,
            ".orchestrator/ directory not found",
            f"Run:  python orchestrator.py init --project {project_root}",
        )
    agents_yaml = orch_dir / "agents.yaml"
    if not agents_yaml.exists():
        return CheckResult(
            "Project structure",
            CheckStatus.WARN,
            ".orchestrator/ found but agents.yaml is missing",
            f"Run:  python orchestrator.py init --project {project_root}  to recreate it",
        )
    return CheckResult("Project structure", CheckStatus.PASS, ".orchestrator/agents.yaml present ✓")


def _check_agents_yaml(project_root: Path) -> CheckResult:
    yaml_path = project_root / ".orchestrator" / "agents.yaml"
    if not yaml_path.exists():
        return CheckResult(
            "agents.yaml syntax",
            CheckStatus.SKIP,
            "agents.yaml not found — skipped",
        )
    try:
        import yaml
        with open(yaml_path) as f:
            data = yaml.safe_load(f)
        if not isinstance(data, dict):
            return CheckResult(
                "agents.yaml syntax",
                CheckStatus.FAIL,
                "agents.yaml is empty or not a valid YAML mapping",
                "Run:  python orchestrator.py init --force  to regenerate",
            )
        return CheckResult("agents.yaml syntax", CheckStatus.PASS, "agents.yaml is valid YAML ✓")
    except Exception as exc:
        return CheckResult(
            "agents.yaml syntax",
            CheckStatus.FAIL,
            f"YAML parse error: {exc}",
            "Fix the indentation/syntax — YAML uses spaces, not tabs",
        )


def _check_write_permission(project_root: Path) -> CheckResult:
    orch_dir = project_root / ".orchestrator"
    test_dir = orch_dir if orch_dir.exists() else project_root
    test_file = test_dir / ".symphony_write_test"
    try:
        test_file.write_text("ok")
        test_file.unlink()
        return CheckResult(
            "Write permissions",
            CheckStatus.PASS,
            f"Can write to {test_dir} ✓",
        )
    except PermissionError:
        return CheckResult(
            "Write permissions",
            CheckStatus.FAIL,
            f"No write permission to {test_dir}",
            "Run as Administrator (Windows) or fix ownership: chown -R $USER .orchestrator",
        )
    except Exception as exc:
        return CheckResult(
            "Write permissions",
            CheckStatus.WARN,
            f"Write test inconclusive: {exc}",
            "Ensure you own the project directory",
        )


def _check_disk_space(project_root: Path, min_mb: int = 200) -> CheckResult:
    try:
        usage = shutil.disk_usage(project_root)
        free_mb = usage.free // (1024 * 1024)
        if free_mb < min_mb:
            return CheckResult(
                "Disk space",
                CheckStatus.FAIL,
                f"Only {free_mb} MB free — at least {min_mb} MB recommended",
                "Delete unused files or move to a drive with more space",
            )
        if free_mb < min_mb * 5:
            return CheckResult(
                "Disk space",
                CheckStatus.WARN,
                f"{free_mb} MB free — running low",
                "Consider freeing up disk space",
            )
        return CheckResult("Disk space", CheckStatus.PASS, f"{free_mb} MB free ✓")
    except Exception:
        return CheckResult("Disk space", CheckStatus.SKIP, "Disk space check unavailable")


def _check_api_key(api_key: str | None) -> CheckResult:
    if not api_key:
        return CheckResult(
            "Anthropic API key",
            CheckStatus.FAIL,
            "ANTHROPIC_API_KEY is not set",
            "Export it:  export ANTHROPIC_API_KEY=sk-ant-...  or add to .orchestrator/.env",
        )
    if not api_key.startswith("sk-"):
        return CheckResult(
            "Anthropic API key",
            CheckStatus.WARN,
            "API key format looks unusual (expected 'sk-ant-...')",
            "Verify the key at https://console.anthropic.com/account/api-keys",
        )
    if len(api_key) < 20:
        return CheckResult(
            "Anthropic API key",
            CheckStatus.FAIL,
            "API key is too short to be valid",
            "Copy the full key from https://console.anthropic.com/account/api-keys",
        )
    # Format looks ok; skip live validation here (avoid spending tokens)
    return CheckResult(
        "Anthropic API key",
        CheckStatus.PASS,
        f"Key present and format OK (sk-...{api_key[-4:]}) ✓",
    )


def _check_internet(host: str = "api.anthropic.com", port: int = 443, timeout: float = 3.0) -> CheckResult:
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return CheckResult("Internet / Anthropic API", CheckStatus.PASS, f"Reachable: {host}:{port} ✓")
    except socket.timeout:
        return CheckResult(
            "Internet / Anthropic API",
            CheckStatus.WARN,
            f"Connection to {host}:{port} timed out",
            "Check your internet connection or firewall settings",
        )
    except OSError as exc:
        return CheckResult(
            "Internet / Anthropic API",
            CheckStatus.FAIL,
            f"Cannot reach {host}: {exc}",
            "Check your internet connection — or use Ollama for offline AI",
        )


def _check_ollama(ollama_url: str = "http://localhost:11434") -> CheckResult:
    try:
        import urllib.request
        import json as _json
        req = urllib.request.urlopen(f"{ollama_url}/api/tags", timeout=3)
        data = _json.loads(req.read())
        models = [m.get("name", "") for m in data.get("models", [])]
        if not models:
            return CheckResult(
                "Ollama",
                CheckStatus.WARN,
                f"Ollama running at {ollama_url} but no models downloaded",
                "Download a model:  ollama pull mistral",
            )
        return CheckResult(
            "Ollama",
            CheckStatus.PASS,
            f"Ollama running, {len(models)} model(s) available: {', '.join(models[:3])} ✓",
        )
    except Exception as exc:
        err = str(exc)
        if "Connection refused" in err or "ECONNREFUSED" in err:
            return CheckResult(
                "Ollama",
                CheckStatus.FAIL,
                f"Ollama not running at {ollama_url}",
                "Start it:  ollama serve",
            )
        return CheckResult(
            "Ollama",
            CheckStatus.FAIL,
            f"Cannot reach Ollama at {ollama_url}: {err[:80]}",
            "Verify Ollama is installed (https://ollama.ai) and running",
        )


def _check_orchestrator_script(project_root: Path) -> CheckResult:
    candidates = [
        project_root / "ai-orchestrator" / "orchestrator.py",
        project_root / "orchestrator.py",
        Path(__file__).parent / "orchestrator.py",
    ]
    for p in candidates:
        if p.exists():
            return CheckResult("Orchestrator script", CheckStatus.PASS, f"Found at {p} ✓")
    return CheckResult(
        "Orchestrator script",
        CheckStatus.FAIL,
        "orchestrator.py not found",
        "Re-clone Symphony-IR or check the project directory path",
    )


# ── Public API ────────────────────────────────────────────────────────────────

def run_checks(
    project_root: Path,
    provider: str = "claude",
    api_key: Optional[str] = None,
    ollama_url: str = "http://localhost:11434",
    skip: list[str] | None = None,
) -> list[CheckResult]:
    """
    Run all pre-flight checks and return a list of CheckResult objects.

    Parameters
    ----------
    project_root:
        Root of the Symphony-IR project (contains .orchestrator/).
    provider:
        'claude', 'openai', or 'ollama' — controls which checks run.
    api_key:
        Anthropic API key.  Falls back to ANTHROPIC_API_KEY env var.
    ollama_url:
        Ollama base URL (default http://localhost:11434).
    skip:
        List of check names to skip (e.g. ['internet', 'disk_space']).
    """
    skip = [s.lower() for s in (skip or [])]
    results: list[CheckResult] = []

    def _add(check_fn, *args, skip_key: str = ""):
        if skip_key and skip_key in skip:
            return
        results.append(check_fn(*args))

    # Always-run checks
    _add(_check_python_version)
    _add(_check_package, "yaml", "yaml")
    _add(_check_package, "requests")
    _add(_check_project_structure, project_root)
    _add(_check_agents_yaml,       project_root)
    _add(_check_write_permission,  project_root)
    _add(_check_disk_space,        project_root, skip_key="disk_space")
    _add(_check_orchestrator_script, project_root)

    prov = provider.lower()

    # Claude-specific
    if "claude" in prov or "anthropic" in prov:
        key = api_key or os.environ.get("ANTHROPIC_API_KEY", "")
        _add(_check_api_key, key)
        _add(_check_package, "anthropic")
        _add(_check_internet, skip_key="internet")

    # OpenAI-specific
    elif "openai" in prov:
        key = api_key or os.environ.get("OPENAI_API_KEY", "")
        _add(_check_api_key, key)
        _add(_check_package, "openai")
        _add(_check_internet, "api.openai.com", 443, skip_key="internet")

    # Ollama-specific
    elif "ollama" in prov:
        _add(_check_package, "requests")
        _add(_check_ollama, ollama_url, skip_key="ollama")

    return results


def passed(results: list[CheckResult]) -> bool:
    """Return True only if there are no FAIL results."""
    return all(r.status != CheckStatus.FAIL for r in results)


def summary(results: list[CheckResult]) -> tuple[int, int, int]:
    """Return (n_pass, n_warn, n_fail)."""
    p = sum(1 for r in results if r.status == CheckStatus.PASS)
    w = sum(1 for r in results if r.status == CheckStatus.WARN)
    f = sum(1 for r in results if r.status == CheckStatus.FAIL)
    return p, w, f


# ── CLI output ────────────────────────────────────────────────────────────────

_OS = platform.system()
_USE_COLOUR = (
    _OS != "Windows"
    or os.environ.get("ANSICON")
    or os.environ.get("WT_SESSION")
    or os.environ.get("TERM_PROGRAM")
)
_C = {
    "green":  "\033[92m", "yellow": "\033[93m",
    "red":    "\033[91m", "dim":    "\033[2m",
    "bold":   "\033[1m",  "reset":  "\033[0m",
}

def _c(colour: str, text: str) -> str:
    return f"{_C.get(colour,'')}{text}{_C['reset']}" if _USE_COLOUR else text


def print_report(results: list[CheckResult], verbose: bool = False) -> bool:
    """
    Print a formatted pre-flight report to stdout.

    Returns True if all checks passed (no FAILs).
    """
    n_pass, n_warn, n_fail = summary(results)
    width = 56

    print()
    print(_c("bold", f"{'─' * width}"))
    print(_c("bold", "  Symphony-IR  Pre-flight Check"))
    print(_c("bold", f"{'─' * width}"))

    for r in results:
        colour = {"PASS": "green", "WARN": "yellow", "FAIL": "red", "SKIP": "dim"}[r.status.value]
        status_str = _c(colour, f"[{r.status.value:<4}]")
        print(f"  {r.icon}  {status_str}  {r.name}")
        if verbose or r.status in (CheckStatus.WARN, CheckStatus.FAIL):
            print(f"          {r.message}")
            if r.fix:
                print(_c("dim", f"          → {r.fix}"))

    print(_c("bold", f"{'─' * width}"))
    totals = (
        _c("green",  f"{n_pass} passed") + "  " +
        _c("yellow", f"{n_warn} warnings") + "  " +
        _c("red",    f"{n_fail} failed")
    )
    print(f"  {totals}")
    print(_c("bold", f"{'─' * width}"))
    print()

    if n_fail > 0:
        print(_c("red", "  Fix the issues above before running Symphony-IR."))
        print()
        return False
    if n_warn > 0:
        print(_c("yellow", "  Warnings found — Symphony-IR will work but may be limited."))
        print()
    else:
        print(_c("green", "  All checks passed! Ready to run."))
        print()

    return True


def run_and_print(
    project_root: Path,
    provider: str = "claude",
    api_key: Optional[str] = None,
    ollama_url: str = "http://localhost:11434",
    verbose: bool = False,
) -> bool:
    """Convenience wrapper: run checks + print report + return pass/fail bool."""
    results = run_checks(
        project_root=project_root,
        provider=provider,
        api_key=api_key,
        ollama_url=ollama_url,
    )
    return print_report(results, verbose=verbose)
