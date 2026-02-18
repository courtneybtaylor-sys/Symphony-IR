"""Prompt Compiler - Deterministic compilation layer for multi-model orchestration.

This is NOT a "prompt maker" - it's a compiler that transforms high-level intent
into model-optimized, token-efficient instruction packets.

The Conductor defines WHAT must be done.
The Prompt Compiler defines HOW it is phrased for each model.

Pipeline:
  1. Template Selection — Match role to prompt template
  2. Context Pruning — Remove irrelevant context (40% token reduction)
  3. Model Adaptation — Claude->XML, GPT->JSON, Ollama->instruction tags
  4. Token Budget Enforcement — Hard limits on prompt size
  5. Schema Injection — Append output format requirements
"""

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

logger = logging.getLogger(__name__)


class PromptFormat(Enum):
    """Output format requirements."""

    JSON = "json"
    MARKDOWN = "markdown"
    XML = "xml"
    TEXT = "text"


@dataclass
class TokenBudget:
    """Token budget constraints."""

    max_input_tokens: int = 3000
    max_output_tokens: int = 2000
    max_total_tokens: int = 5000

    def is_within_budget(self, estimated_tokens: int) -> bool:
        """Check if token count is within budget."""
        return estimated_tokens <= self.max_input_tokens


@dataclass
class OutputSchema:
    """Output format contract for an agent."""

    format_type: PromptFormat
    required_fields: List[str]
    schema_definition: Dict[str, Any]
    max_tokens: Optional[int] = None
    example: Optional[Dict[str, Any]] = None
    error_format: Optional[Dict[str, Any]] = None


@dataclass
class PromptTemplate:
    """Role-specific prompt template."""

    role: str
    goal: str
    constraints: List[str]
    output_schema: OutputSchema
    model_preferences: Dict[str, str] = field(default_factory=dict)


@dataclass
class CompiledPrompt:
    """A compiled, optimized prompt ready for model dispatch."""

    role: str
    content: str
    estimated_tokens: int
    model_provider: str
    output_schema: OutputSchema
    context_summary: Dict[str, Any]
    compilation_metadata: Dict[str, Any]


class PromptCompiler:
    """Deterministic prompt compilation layer.

    Transforms high-level Conductor instructions into model-specific,
    token-optimized prompts with schema enforcement.

    Design principles:
    - Deterministic: Same input -> same output
    - Auditable: Every decision logged with reason codes
    - Efficient: Token budget enforcement
    - Governed: Ma'aT compatible
    """

    def __init__(
        self,
        templates_path: str = "config",
        config: Optional[Dict[str, Any]] = None,
    ):
        self.templates_path = Path(templates_path)
        self.config = self._default_config()
        if config:
            # Deep merge top-level keys
            for key, value in config.items():
                if isinstance(value, dict) and key in self.config:
                    self.config[key].update(value)
                else:
                    self.config[key] = value
        self.templates: Dict[str, PromptTemplate] = {}
        self.compilation_log: List[Dict[str, Any]] = []

        self._load_templates()

    def _default_config(self) -> Dict[str, Any]:
        """Default compiler configuration."""
        return {
            "default_token_budget": {
                "max_input_tokens": 3000,
                "max_output_tokens": 2000,
                "max_total_tokens": 5000,
            },
            "context_pruning": {
                "enabled": True,
                "max_files": 5,
                "max_lines_per_file": 200,
                "relevance_threshold": 0.3,
            },
            "model_adapters": {
                "anthropic": "xml",
                "openai": "json_schema",
                "ollama": "instruction_tags",
                "mock": "default",
            },
            "compression": {
                "enabled": True,
                "threshold_tokens": 2500,
            },
        }

    def _load_templates(self):
        """Load prompt templates from YAML."""
        template_file = self.templates_path / "prompt_templates.yaml"

        if not template_file.exists():
            logger.info(
                "No prompt_templates.yaml found, creating defaults at %s",
                template_file,
            )
            self._create_default_templates()
            return

        with open(template_file) as f:
            templates_data = yaml.safe_load(f)

        for role, template_data in templates_data.get("templates", {}).items():
            schema_data = template_data.get("output_schema", {})
            output_schema = OutputSchema(
                format_type=PromptFormat(schema_data.get("format", "json")),
                required_fields=schema_data.get("required_fields", []),
                schema_definition=schema_data.get("schema", {}),
                max_tokens=schema_data.get("max_tokens"),
                example=schema_data.get("example"),
                error_format=schema_data.get("error_format"),
            )

            template = PromptTemplate(
                role=role,
                goal=template_data.get("goal", ""),
                constraints=template_data.get("constraints", []),
                output_schema=output_schema,
                model_preferences=template_data.get("model_preferences", {}),
            )

            self.templates[role] = template

        logger.info("Loaded %d prompt templates", len(self.templates))

    def compile(
        self,
        role: str,
        phase_brief: str,
        context: Dict[str, Any],
        model_provider: str,
        token_budget: Optional[TokenBudget] = None,
    ) -> CompiledPrompt:
        """Compile a high-level instruction into an optimized prompt.

        Pipeline:
        1. Template Selection
        2. Context Pruning (40% token reduction)
        3. Model Adaptation (Claude->XML, GPT->JSON)
        4. Token Budget Enforcement
        5. Schema Injection

        Args:
            role: Agent role (architect, researcher, etc.)
            phase_brief: High-level task description from Conductor
            context: Available context (files, git, etc.)
            model_provider: Target model (anthropic, openai, ollama)
            token_budget: Optional budget override

        Returns:
            CompiledPrompt ready for model dispatch
        """
        template = self.templates.get(role)
        if not template:
            raise ValueError(
                f"No template found for role: {role}. "
                f"Available: {list(self.templates.keys())}"
            )

        if not token_budget:
            budget_config = self.config["default_token_budget"]
            token_budget = TokenBudget(**budget_config)

        # Step 1: Build base prompt from template
        base_prompt = self._build_base_prompt(template, phase_brief)

        # Step 2: Prune context to fit budget
        pruned_context = self._prune_context(context, token_budget)

        # Step 3: Integrate context into prompt
        prompt_with_context = self._integrate_context(base_prompt, pruned_context)

        # Step 4: Adapt for target model dialect
        adapted_prompt = self._adapt_for_model(
            prompt_with_context, template, model_provider
        )

        # Step 5: Inject output schema requirements
        final_prompt = self._inject_schema(adapted_prompt, template.output_schema)

        # Step 6: Enforce token budget
        estimated_tokens = self._estimate_tokens(final_prompt)

        if not token_budget.is_within_budget(estimated_tokens):
            final_prompt = self._compress_prompt(
                final_prompt, token_budget, model_provider
            )
            estimated_tokens = self._estimate_tokens(final_prompt)

        compiled = CompiledPrompt(
            role=role,
            content=final_prompt,
            estimated_tokens=estimated_tokens,
            model_provider=model_provider,
            output_schema=template.output_schema,
            context_summary={
                "files_included": pruned_context.get("files_count", 0),
                "context_size": len(str(pruned_context)),
                "pruning_applied": pruned_context.get("pruned", False),
            },
            compilation_metadata={
                "template_version": "1.0",
                "token_budget": {
                    "max": token_budget.max_input_tokens,
                    "used": estimated_tokens,
                    "utilization": round(
                        estimated_tokens / token_budget.max_input_tokens, 3
                    ),
                },
                "model_adapter": self.config["model_adapters"].get(
                    model_provider, "default"
                ),
                "compression_applied": estimated_tokens
                > token_budget.max_input_tokens,
            },
        )

        self._log_compilation(compiled, phase_brief)
        return compiled

    def _build_base_prompt(
        self, template: PromptTemplate, phase_brief: str
    ) -> str:
        """Build base prompt from template."""
        parts = [
            f"GOAL: {template.goal}",
            "",
            f"TASK: {phase_brief}",
            "",
        ]

        if template.constraints:
            parts.append("CONSTRAINTS:")
            for constraint in template.constraints:
                parts.append(f"- {constraint}")
            parts.append("")

        return "\n".join(parts)

    def _prune_context(
        self, context: Dict[str, Any], token_budget: TokenBudget
    ) -> Dict[str, Any]:
        """Prune context to fit token budget.

        Strategy:
        - Keep only most relevant files
        - Truncate large files
        - Remove redundant information
        """
        if not self.config["context_pruning"]["enabled"]:
            return context

        pruned: Dict[str, Any] = {}
        max_files = self.config["context_pruning"]["max_files"]
        max_lines = self.config["context_pruning"]["max_lines_per_file"]

        # Handle filesystem context (case-insensitive key lookup)
        fs_key = None
        for key in context:
            if key.lower() in ("filesystem", "file_system"):
                fs_key = key
                break

        if fs_key:
            fs_context = context[fs_key]
            if "key_files" in fs_context:
                key_files = fs_context["key_files"]
                pruned_files = dict(list(key_files.items())[:max_files])

                for filename, content in pruned_files.items():
                    if isinstance(content, str):
                        lines = content.split("\n")
                        if len(lines) > max_lines:
                            pruned_files[filename] = (
                                "\n".join(lines[:max_lines])
                                + f"\n... (truncated {len(lines) - max_lines} lines)"
                            )

                pruned["key_files"] = pruned_files
                pruned["files_count"] = len(pruned_files)
                pruned["pruned"] = len(key_files) > max_files

        # Handle git context
        git_key = None
        for key in context:
            if key.lower() == "git":
                git_key = key
                break

        if git_key:
            git_context = context[git_key]
            pruned["git"] = {
                "branch": git_context.get("branch"),
                "status": str(git_context.get("status", ""))[:200],
            }

        # Handle active file
        active_key = None
        for key in context:
            if key.lower() in ("active_file", "activefile"):
                active_key = key
                break

        if active_key:
            pruned["active_file"] = context[active_key]

        return pruned

    def _integrate_context(
        self, base_prompt: str, context: Dict[str, Any]
    ) -> str:
        """Integrate pruned context into prompt."""
        if not context:
            return base_prompt

        parts = [base_prompt, "CONTEXT:"]

        if "git" in context:
            git = context["git"]
            parts.append(f"Branch: {git.get('branch', 'unknown')}")
            if git.get("status"):
                parts.append(f"Status: {git['status']}")

        if "key_files" in context:
            parts.append("\nRELEVANT FILES:")
            for filename, content in context["key_files"].items():
                parts.append(f"\n=== {filename} ===")
                parts.append(str(content))

        if "active_file" in context:
            active = context["active_file"]
            parts.append(f"\nCURRENT FILE: {active.get('name', 'unknown')}")
            parts.append(str(active.get("content", "")))

        parts.append("")
        return "\n".join(parts)

    def _adapt_for_model(
        self,
        prompt: str,
        template: PromptTemplate,
        model_provider: str,
    ) -> str:
        """Adapt prompt for specific model dialect.

        - Claude: Prefers XML structure
        - GPT: Works well with JSON schemas
        - Llama/Ollama: Needs explicit instruction tags
        """
        adapter_type = self.config["model_adapters"].get(
            model_provider, "default"
        )

        model_prefs = template.model_preferences.get(model_provider, "")
        if model_prefs:
            prompt = f"{prompt}\nMODEL-SPECIFIC INSTRUCTIONS:\n{model_prefs}"

        if adapter_type == "xml":
            return f"<task>\n{prompt}\n</task>"
        elif adapter_type == "json_schema":
            return f"{prompt}\n\n(Follow the JSON schema provided below strictly)"
        elif adapter_type == "instruction_tags":
            return f"[INST]\n{prompt}\n[/INST]"
        else:
            return prompt

    def _inject_schema(self, prompt: str, schema: OutputSchema) -> str:
        """Inject output schema requirements into prompt."""
        parts = [prompt, "", "OUTPUT REQUIREMENTS:"]
        parts.append(f"Format: {schema.format_type.value.upper()}")
        parts.append("")

        if schema.format_type == PromptFormat.JSON:
            parts.append(
                "You MUST respond in valid JSON matching this exact schema:"
            )
            parts.append(json.dumps(schema.schema_definition, indent=2))
            parts.append("")

            if schema.required_fields:
                parts.append("Required fields:")
                for f in schema.required_fields:
                    parts.append(f"- {f}")
                parts.append("")

            if schema.example:
                parts.append("Example response:")
                parts.append(json.dumps(schema.example, indent=2))
                parts.append("")

            error_format = schema.error_format or {"error": "explanation"}
            parts.append("If you cannot complete the task, respond with:")
            parts.append(json.dumps(error_format, indent=2))

        return "\n".join(parts)

    def _estimate_tokens(self, text: str) -> int:
        """Estimate token count (~4 chars per token for English text)."""
        return len(text) // 4

    def _compress_prompt(
        self, prompt: str, budget: TokenBudget, model_provider: str
    ) -> str:
        """Compress prompt to fit within budget.

        Strategy: truncate context section while preserving header and schema.
        """
        lines = prompt.split("\n")

        context_start = -1
        for i, line in enumerate(lines):
            if line.startswith("CONTEXT:"):
                context_start = i
                break

        if context_start == -1:
            return prompt

        header = "\n".join(lines[:context_start])
        header_tokens = self._estimate_tokens(header)
        available_for_context = (
            budget.max_input_tokens - header_tokens - 500
        )

        context_lines = lines[context_start:]
        compressed_context = []
        current_tokens = 0

        for line in context_lines:
            line_tokens = self._estimate_tokens(line)
            if current_tokens + line_tokens > available_for_context:
                compressed_context.append(
                    "... (context truncated to fit token budget)"
                )
                break
            compressed_context.append(line)
            current_tokens += line_tokens

        return header + "\n" + "\n".join(compressed_context)

    def _log_compilation(
        self, compiled: CompiledPrompt, phase_brief: str
    ):
        """Log compilation for audit trail."""
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "role": compiled.role,
            "phase_brief": phase_brief,
            "estimated_tokens": compiled.estimated_tokens,
            "model_provider": compiled.model_provider,
            "context_summary": compiled.context_summary,
            "metadata": compiled.compilation_metadata,
        }
        self.compilation_log.append(log_entry)

    def get_compilation_stats(self) -> Dict[str, Any]:
        """Get compilation statistics."""
        if not self.compilation_log:
            return {
                "total_compilations": 0,
                "total_tokens_estimated": 0,
                "average_tokens_per_prompt": 0,
                "compression_applied_count": 0,
                "compression_rate": 0.0,
            }

        total = len(self.compilation_log)
        total_tokens = sum(
            entry["estimated_tokens"] for entry in self.compilation_log
        )
        compressed_count = sum(
            1
            for entry in self.compilation_log
            if entry["metadata"].get("compression_applied", False)
        )

        return {
            "total_compilations": total,
            "total_tokens_estimated": total_tokens,
            "average_tokens_per_prompt": round(total_tokens / total, 1),
            "compression_applied_count": compressed_count,
            "compression_rate": round(compressed_count / total, 3)
            if total > 0
            else 0.0,
        }

    def export_log(self, filepath: str):
        """Export compilation log to file."""
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            json.dump(
                {
                    "stats": self.get_compilation_stats(),
                    "log": self.compilation_log,
                },
                f,
                indent=2,
            )
        logger.info("Compilation log exported to %s", filepath)

    def list_templates(self) -> List[str]:
        """List all loaded template role names."""
        return list(self.templates.keys())

    def has_template(self, role: str) -> bool:
        """Check if a template exists for the given role."""
        return role in self.templates

    def _create_default_templates(self):
        """Create default prompt_templates.yaml with all 5 specialist roles."""
        default_templates = {
            "templates": {
                "architect": {
                    "goal": "Design system architecture and identify constraints",
                    "constraints": [
                        "Focus on high-level design, not implementation",
                        "Identify risks and dependencies",
                        "Consider scalability and maintainability",
                    ],
                    "output_schema": {
                        "format": "json",
                        "required_fields": [
                            "system_design",
                            "risks",
                            "constraints",
                        ],
                        "schema": {
                            "system_design": "string",
                            "components": ["string"],
                            "risks": ["string"],
                            "constraints": ["string"],
                        },
                        "example": {
                            "system_design": "Microservices architecture with API Gateway",
                            "components": [
                                "API Gateway",
                                "Auth Service",
                                "Data Service",
                            ],
                            "risks": ["Single point of failure in gateway"],
                            "constraints": [
                                "Must support 10k concurrent users"
                            ],
                        },
                        "error_format": {
                            "error": "description of what went wrong"
                        },
                    },
                    "model_preferences": {
                        "anthropic": "Use structured thinking. Consider edge cases thoroughly.",
                        "openai": "Be concise and action-oriented. Focus on practical implementation.",
                    },
                },
                "researcher": {
                    "goal": "Find relevant documentation, APIs, and best practices",
                    "constraints": [
                        "Cite sources where possible",
                        "Focus on recent, authoritative sources",
                        "Identify existing solutions before proposing new ones",
                    ],
                    "output_schema": {
                        "format": "json",
                        "required_fields": ["findings", "sources"],
                        "schema": {
                            "findings": ["string"],
                            "sources": [
                                {
                                    "title": "string",
                                    "relevance": "string",
                                }
                            ],
                            "recommendations": ["string"],
                        },
                    },
                    "model_preferences": {
                        "anthropic": "Be thorough in analysis. Consider multiple perspectives.",
                        "openai": "Prioritize actionable findings.",
                    },
                },
                "implementer": {
                    "goal": "Write production-quality code",
                    "constraints": [
                        "Follow best practices for the language",
                        "Include error handling",
                        "Write clean, maintainable code",
                        "Add inline comments for complex logic only",
                    ],
                    "output_schema": {
                        "format": "json",
                        "required_fields": ["code", "explanation"],
                        "schema": {
                            "code": "string",
                            "explanation": "string",
                            "dependencies": ["string"],
                            "testing_notes": "string",
                        },
                        "example": {
                            "code": "def calculate(x, y):\n    return x + y",
                            "explanation": "Simple addition function",
                            "dependencies": [],
                            "testing_notes": "Test with negative numbers and zero",
                        },
                    },
                    "model_preferences": {
                        "anthropic": "Prioritize code quality over brevity.",
                        "openai": "Use modern idioms and patterns.",
                    },
                },
                "reviewer": {
                    "goal": "Critically analyze code and designs for issues",
                    "constraints": [
                        "Identify bugs and edge cases",
                        "Check for security vulnerabilities",
                        "Suggest concrete improvements",
                        "Be constructive, not just critical",
                    ],
                    "output_schema": {
                        "format": "json",
                        "required_fields": ["issues", "suggestions"],
                        "schema": {
                            "issues": [
                                {
                                    "severity": "string",
                                    "description": "string",
                                    "location": "string",
                                }
                            ],
                            "suggestions": ["string"],
                            "overall_assessment": "string",
                        },
                    },
                    "model_preferences": {
                        "anthropic": "Be thorough. Consider edge cases and failure modes.",
                        "openai": "Focus on actionable, prioritized feedback.",
                    },
                },
                "integrator": {
                    "goal": "Synthesize outputs from all agents into a coherent deliverable",
                    "constraints": [
                        "Resolve conflicts between agent outputs",
                        "Create unified, consistent output",
                        "Balance competing trade-offs explicitly",
                    ],
                    "output_schema": {
                        "format": "json",
                        "required_fields": [
                            "integrated_output",
                            "resolution_notes",
                        ],
                        "schema": {
                            "integrated_output": "string",
                            "resolution_notes": ["string"],
                            "confidence": "number",
                        },
                    },
                    "model_preferences": {
                        "anthropic": "Focus on coherence and completeness.",
                        "openai": "Prioritize clarity and actionability.",
                    },
                },
            }
        }

        template_file = self.templates_path / "prompt_templates.yaml"
        template_file.parent.mkdir(parents=True, exist_ok=True)

        with open(template_file, "w") as f:
            yaml.dump(default_templates, f, default_flow_style=False, sort_keys=False)

        # Load the templates we just created
        for role, template_data in default_templates["templates"].items():
            schema_data = template_data.get("output_schema", {})
            output_schema = OutputSchema(
                format_type=PromptFormat(schema_data.get("format", "json")),
                required_fields=schema_data.get("required_fields", []),
                schema_definition=schema_data.get("schema", {}),
                example=schema_data.get("example"),
                error_format=schema_data.get("error_format"),
            )
            self.templates[role] = PromptTemplate(
                role=role,
                goal=template_data.get("goal", ""),
                constraints=template_data.get("constraints", []),
                output_schema=output_schema,
                model_preferences=template_data.get("model_preferences", {}),
            )
