"""Context providers for collecting project and environment information.

Providers gather filesystem, git, and file context to give agents
rich understanding of the project they're working on.
"""

import logging
import os
import subprocess
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# Directories to ignore when building file trees
IGNORE_DIRS = {
    "node_modules",
    ".git",
    "__pycache__",
    ".venv",
    "venv",
    "dist",
    "build",
    ".tox",
    ".mypy_cache",
    ".pytest_cache",
    ".eggs",
    "*.egg-info",
    ".next",
    ".nuxt",
    ".cache",
}

# Key files to read automatically
KEY_FILES = [
    "README.md",
    "README.rst",
    "README.txt",
    "package.json",
    "requirements.txt",
    "Pipfile",
    "pyproject.toml",
    "setup.py",
    "setup.cfg",
    "Cargo.toml",
    "go.mod",
    "Makefile",
    "Dockerfile",
    "docker-compose.yml",
    ".env.example",
]


class ContextProvider(ABC):
    """Abstract base class for context providers."""

    @abstractmethod
    def collect(self) -> Dict[str, Any]:
        """Collect context information."""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if this provider can collect data in the current environment."""
        pass

    @abstractmethod
    def get_name(self) -> str:
        """Return the provider name."""
        pass


class FileSystemContext(ContextProvider):
    """Collects file system structure and key file contents."""

    def __init__(self, root_path: str = ".", max_depth: int = 3):
        self.root_path = Path(root_path).resolve()
        self.max_depth = max_depth

    def collect(self) -> Dict[str, Any]:
        """Build file tree and read key files."""
        result = {
            "root": str(self.root_path),
            "file_tree": self._build_tree(self.root_path, depth=0),
            "key_files": {},
        }

        # Read key files
        for filename in KEY_FILES:
            filepath = self.root_path / filename
            if filepath.exists() and filepath.is_file():
                try:
                    content = filepath.read_text(encoding="utf-8", errors="replace")
                    # Truncate large files
                    if len(content) > 10000:
                        content = content[:10000] + "\n... [truncated]"
                    result["key_files"][filename] = content
                except Exception as e:
                    logger.warning(f"Could not read {filename}: {e}")

        return result

    def _build_tree(self, path: Path, depth: int) -> List[Dict[str, Any]]:
        """Recursively build a file tree representation."""
        if depth >= self.max_depth:
            return []

        entries = []
        try:
            for item in sorted(path.iterdir()):
                name = item.name

                # Skip ignored directories
                if item.is_dir() and name in IGNORE_DIRS:
                    continue

                # Skip hidden files/dirs (except key dotfiles)
                if name.startswith(".") and name not in {
                    ".env.example",
                    ".gitignore",
                    ".dockerignore",
                }:
                    continue

                entry = {"name": name, "type": "dir" if item.is_dir() else "file"}

                if item.is_dir():
                    children = self._build_tree(item, depth + 1)
                    if children:
                        entry["children"] = children

                entries.append(entry)
        except PermissionError:
            logger.warning(f"Permission denied: {path}")

        return entries

    def is_available(self) -> bool:
        return self.root_path.exists() and self.root_path.is_dir()

    def get_name(self) -> str:
        return "filesystem"


class GitContext(ContextProvider):
    """Collects git repository information."""

    def __init__(self, repo_path: str = "."):
        self.repo_path = Path(repo_path).resolve()

    def collect(self) -> Dict[str, Any]:
        """Gather git status, branch, recent commits, and diff summary."""
        result = {}

        result["branch"] = self._run_git("rev-parse", "--abbrev-ref", "HEAD")
        result["status"] = self._run_git("status", "--short")
        result["recent_commits"] = self._run_git("log", "-5", "--oneline")
        result["diff_summary"] = self._run_git("diff", "--stat")

        return result

    def _run_git(self, *args: str) -> str:
        """Run a git command and return output."""
        try:
            result = subprocess.run(
                ["git"] + list(args),
                cwd=str(self.repo_path),
                capture_output=True,
                text=True,
                timeout=10,
            )
            return result.stdout.strip()
        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            logger.warning(f"Git command failed: git {' '.join(args)}: {e}")
            return ""

    def is_available(self) -> bool:
        git_dir = self.repo_path / ".git"
        return git_dir.exists()

    def get_name(self) -> str:
        return "git"


class ActiveFileContext(ContextProvider):
    """Provides context for a specific file being worked on."""

    def __init__(self, file_path: Optional[str] = None):
        self.file_path = Path(file_path).resolve() if file_path else None

    def collect(self) -> Dict[str, Any]:
        """Read the active file and return its metadata and content."""
        if not self.file_path or not self.file_path.exists():
            return {}

        try:
            stat = self.file_path.stat()
            content = self.file_path.read_text(encoding="utf-8", errors="replace")
            line_count = content.count("\n") + 1

            # Truncate large files
            if len(content) > 10240:
                content = content[:10240] + "\n... [truncated at 10KB]"

            return {
                "path": str(self.file_path),
                "name": self.file_path.name,
                "extension": self.file_path.suffix,
                "line_count": line_count,
                "size_bytes": stat.st_size,
                "content": content,
            }
        except Exception as e:
            logger.warning(f"Could not read active file {self.file_path}: {e}")
            return {"path": str(self.file_path), "error": str(e)}

    def is_available(self) -> bool:
        return self.file_path is not None and self.file_path.exists()

    def get_name(self) -> str:
        return "active_file"


class ContextManager:
    """Manages multiple context providers and aggregates their output."""

    def __init__(self):
        self._providers: List[ContextProvider] = []

    def add_provider(self, provider: ContextProvider):
        """Register a context provider."""
        self._providers.append(provider)

    def collect_all(self) -> Dict[str, Any]:
        """Collect context from all available providers.

        Returns:
            Dictionary mapping provider names to their collected data.
        """
        result = {}
        for provider in self._providers:
            name = provider.get_name()
            if provider.is_available():
                try:
                    result[name] = provider.collect()
                except Exception as e:
                    logger.error(f"Provider {name} failed: {e}")
                    result[name] = {"error": str(e)}
            else:
                logger.debug(f"Provider {name} not available, skipping")

        return result

    def get_summary(self) -> str:
        """Return a text summary of provider availability."""
        lines = ["Context Providers:"]
        for provider in self._providers:
            status = "available" if provider.is_available() else "unavailable"
            lines.append(f"  - {provider.get_name()}: {status}")
        return "\n".join(lines)

    @property
    def providers(self) -> List[ContextProvider]:
        """Return the list of registered providers."""
        return list(self._providers)
