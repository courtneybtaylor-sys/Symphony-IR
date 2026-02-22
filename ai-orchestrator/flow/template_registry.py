"""
Symphony Flow Template Registry

Provides dynamic discovery, filtering, and metadata access for flow templates.
Both the CLI (orchestrator.py flow-list) and GUI flow tabs use this registry.

Usage:
    from flow.template_registry import TemplateRegistry
    registry = TemplateRegistry()

    # List all
    registry.list_templates()

    # Filter by domain
    registry.filter_by_domain("security")

    # Filter by tag
    registry.filter_by_tag("compliance")

    # Search
    registry.search("vulnerability")

    # Get metadata
    registry.get_metadata("security_audit")
"""

import yaml
from pathlib import Path
from typing import List, Optional, Dict, Any


TEMPLATES_DIR = Path(__file__).parent / "templates"

# Domains known to the registry (for validation and listing)
KNOWN_DOMAINS = {
    "security",
    "cloud",
    "data",
    "ml",
    "performance",
    "compliance",
    "development",   # generic dev templates
}


class TemplateMetadata:
    """Lightweight metadata parsed from a template YAML."""

    def __init__(self, path: Path, data: Dict[str, Any]):
        self.path             = path
        self.template_id      = data.get("template_id", path.stem)
        self.name             = data.get("name", path.stem)
        self.description      = data.get("description", "")
        self.domain           = data.get("domain", "development")
        self.industry         = data.get("industry", "cross-industry")
        self.difficulty_level = data.get("difficulty_level", "intermediate")
        self.estimated_duration = data.get("estimated_duration", "")
        self.tags             = data.get("tags", [])
        self.required_context = data.get("required_context", [])
        self.node_count       = len(data.get("nodes", {}))

    def matches_domain(self, domain: str) -> bool:
        return self.domain.lower() == domain.lower()

    def matches_tag(self, tag: str) -> bool:
        return any(tag.lower() in t.lower() for t in self.tags)

    def matches_search(self, query: str) -> bool:
        q = query.lower()
        return (
            q in self.name.lower()
            or q in self.description.lower()
            or q in self.domain.lower()
            or any(q in t.lower() for t in self.tags)
        )


class TemplateRegistry:
    """
    Discovers and indexes all .yaml templates in the templates/ directory.
    Supports filtering, searching, and metadata retrieval.
    """

    def __init__(self, templates_dir: Optional[Path] = None):
        self._dir  = templates_dir or TEMPLATES_DIR
        self._cache: Dict[str, TemplateMetadata] = {}
        self._load_all()

    # ------------------------------------------------------------------
    # Loading
    # ------------------------------------------------------------------

    def _load_all(self) -> None:
        """Scan templates dir and build metadata cache."""
        self._cache.clear()
        if not self._dir.exists():
            return
        for yaml_file in sorted(self._dir.glob("*.yaml")):
            meta = self._load_file(yaml_file)
            if meta:
                self._cache[meta.template_id] = meta

    def _load_file(self, path: Path) -> Optional[TemplateMetadata]:
        """Parse a single YAML template and return its metadata."""
        try:
            with open(path, encoding="utf-8") as f:
                data = yaml.safe_load(f)
            if not data:
                return None
            return TemplateMetadata(path, data)
        except (yaml.YAMLError, OSError):
            return None

    def reload(self) -> None:
        """Reload templates from disk (useful after adding new templates)."""
        self._load_all()

    # ------------------------------------------------------------------
    # Querying
    # ------------------------------------------------------------------

    def list_templates(self) -> List[TemplateMetadata]:
        """Return all templates sorted by name."""
        return sorted(self._cache.values(), key=lambda m: m.name)

    def filter_by_domain(self, domain: str) -> List[TemplateMetadata]:
        """Return templates matching a specific domain."""
        return [m for m in self._cache.values() if m.matches_domain(domain)]

    def filter_by_tag(self, tag: str) -> List[TemplateMetadata]:
        """Return templates that contain a specific tag."""
        return [m for m in self._cache.values() if m.matches_tag(tag)]

    def filter_by_difficulty(self, level: str) -> List[TemplateMetadata]:
        """Return templates by difficulty: 'beginner', 'intermediate', 'advanced'."""
        return [
            m for m in self._cache.values()
            if m.difficulty_level.lower() == level.lower()
        ]

    def search(self, query: str) -> List[TemplateMetadata]:
        """Full-text search across name, description, domain, and tags."""
        return [m for m in self._cache.values() if m.matches_search(query)]

    def get_metadata(self, template_id: str) -> Optional[TemplateMetadata]:
        """Get metadata for a specific template by ID."""
        return self._cache.get(template_id)

    def has_template(self, template_id: str) -> bool:
        """Check if a template exists."""
        return template_id in self._cache

    def list_domains(self) -> List[str]:
        """Return sorted list of all domains present in loaded templates."""
        return sorted({m.domain for m in self._cache.values()})

    def list_tags(self) -> List[str]:
        """Return sorted list of all tags present in loaded templates."""
        all_tags: set = set()
        for m in self._cache.values():
            all_tags.update(m.tags)
        return sorted(all_tags)

    def count(self) -> int:
        """Return the number of loaded templates."""
        return len(self._cache)

    # ------------------------------------------------------------------
    # Formatted output helpers (used by CLI)
    # ------------------------------------------------------------------

    def format_list(
        self,
        templates: Optional[List[TemplateMetadata]] = None,
        verbose: bool = False,
    ) -> str:
        """Return a formatted string listing templates."""
        items = templates if templates is not None else self.list_templates()
        if not items:
            return "No templates found."

        lines = [f"Available Symphony Flow Templates ({len(items)} total):\n"]
        for m in items:
            domain_tag = f"[{m.domain}]" if m.domain else ""
            lines.append(f"  {m.template_id:<30} {m.name}")
            if verbose:
                lines.append(f"    {m.description}")
                lines.append(f"    Domain: {m.domain}  |  Difficulty: {m.difficulty_level}"
                              f"  |  Duration: {m.estimated_duration}")
                if m.tags:
                    lines.append(f"    Tags: {', '.join(m.tags)}")
                lines.append(f"    Nodes: {m.node_count}")
                lines.append("")
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Module-level singleton
# ---------------------------------------------------------------------------

_registry: Optional[TemplateRegistry] = None


def get_registry() -> TemplateRegistry:
    """Return the module-level singleton registry."""
    global _registry
    if _registry is None:
        _registry = TemplateRegistry()
    return _registry
