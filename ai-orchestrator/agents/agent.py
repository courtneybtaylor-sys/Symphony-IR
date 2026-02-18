"""Agent system with structured output parsing and YAML-driven configuration.

Agents are configured via YAML and execute using the model abstraction layer.
They never know which model they're using—swap models via config alone.
"""

import logging
import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from models.client import ModelClient, ModelFactory, Message

logger = logging.getLogger(__name__)


@dataclass
class AgentConfig:
    """Configuration for a single agent."""

    name: str
    role: str
    system_prompt: str
    model_provider: str = "mock"
    model_config: Dict[str, Any] = field(default_factory=dict)
    temperature: float = 0.7
    max_tokens: int = 2000
    constraints: Dict[str, str] = field(default_factory=dict)


class Agent:
    """An AI agent that executes tasks using a configured model.

    Agents use structured output format:
        OUTPUT: [main content]
        CONFIDENCE: [0.0-1.0]
        RISK_FLAGS: [comma-separated]
        REASONING: [explanation]
    """

    def __init__(self, config: AgentConfig, client: Optional[ModelClient] = None):
        """Initialize an agent with config and optional pre-built client.

        Args:
            config: Agent configuration
            client: Pre-built model client (if None, created from config)
        """
        self.config = config
        self.name = config.name
        self.role = config.role

        if client:
            self._client = client
        else:
            # Resolve environment variables in model_config
            resolved_config = self._resolve_env_vars(config.model_config)
            self._client = ModelFactory.create(
                config.model_provider, **resolved_config
            )

    def execute(
        self,
        phase_brief: str,
        shared_context: Optional[Dict[str, Any]] = None,
        memory: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Execute the agent on a task.

        Args:
            phase_brief: Description of what the agent should do
            shared_context: Shared context from context providers
            memory: Optional memory from previous executions

        Returns:
            Dict with output, confidence, risk_flags, reasoning
        """
        shared_context = shared_context or {}
        messages = self._build_messages(phase_brief, shared_context, memory)

        try:
            response = self._client.call(
                messages=messages,
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens,
            )
            return self._parse_response(response.content)
        except Exception as e:
            logger.error(f"Agent {self.name} execution failed: {e}")
            return {
                "agent_name": self.name,
                "role": self.role,
                "output": f"Agent execution failed: {e}",
                "confidence": 0.0,
                "risk_flags": ["CRITICAL_agent_error"],
                "reasoning": f"Exception during execution: {e}",
            }

    def _build_messages(
        self,
        phase_brief: str,
        context: Dict[str, Any],
        memory: Optional[Dict[str, Any]],
    ) -> List[Message]:
        """Build the message list for the model call."""
        messages = []

        # System prompt with constraints
        system = self.config.system_prompt
        if self.config.constraints:
            constraints_text = "\n".join(
                f"- {k}: {v}" for k, v in self.config.constraints.items()
            )
            system += f"\n\nConstraints:\n{constraints_text}"

        system += (
            "\n\nYou MUST format your response using this exact structure:\n"
            "OUTPUT: [your main content here]\n"
            "CONFIDENCE: [a number between 0.0 and 1.0]\n"
            "RISK_FLAGS: [comma-separated flags, or 'none']\n"
            "REASONING: [your reasoning here]"
        )

        messages.append(Message(role="system", content=system))

        # Context summary
        if context:
            context_text = self._format_context(context)
            if context_text:
                messages.append(
                    Message(role="user", content=f"Project Context:\n{context_text}")
                )

        # Memory from previous phases
        if memory:
            memory_text = "\n".join(f"- {k}: {v}" for k, v in memory.items())
            messages.append(
                Message(
                    role="user", content=f"Previous phase results:\n{memory_text}"
                )
            )

        # Phase brief (the actual task)
        messages.append(Message(role="user", content=f"Task:\n{phase_brief}"))

        return messages

    def _format_context(self, context: Dict[str, Any]) -> str:
        """Format context dictionary into readable text."""
        parts = []
        for key, value in context.items():
            if isinstance(value, dict):
                # Summarize nested dicts
                sub_parts = []
                for k, v in value.items():
                    if isinstance(v, str) and len(v) > 500:
                        sub_parts.append(f"  {k}: {v[:500]}...")
                    elif isinstance(v, (list, dict)):
                        sub_parts.append(f"  {k}: [{type(v).__name__}]")
                    else:
                        sub_parts.append(f"  {k}: {v}")
                parts.append(f"{key}:\n" + "\n".join(sub_parts))
            elif isinstance(value, str):
                if len(value) > 500:
                    parts.append(f"{key}: {value[:500]}...")
                else:
                    parts.append(f"{key}: {value}")
            else:
                parts.append(f"{key}: {value}")
        return "\n".join(parts)

    def _parse_response(self, content: str) -> Dict[str, Any]:
        """Parse structured response from model output."""
        result = {
            "agent_name": self.name,
            "role": self.role,
            "output": "",
            "confidence": 0.5,
            "risk_flags": [],
            "reasoning": "",
        }

        # Parse OUTPUT section
        output_match = re.search(
            r"OUTPUT:\s*(.*?)(?=\nCONFIDENCE:|\nRISK_FLAGS:|\nREASONING:|\Z)",
            content,
            re.DOTALL,
        )
        if output_match:
            result["output"] = output_match.group(1).strip()
        else:
            # If no structured format, use entire content as output
            result["output"] = content.strip()

        # Parse CONFIDENCE
        confidence_match = re.search(r"CONFIDENCE:\s*([\d.]+)", content)
        if confidence_match:
            try:
                result["confidence"] = max(0.0, min(1.0, float(confidence_match.group(1))))
            except ValueError:
                result["confidence"] = 0.5

        # Parse RISK_FLAGS
        flags_match = re.search(
            r"RISK_FLAGS:\s*(.*?)(?=\nREASONING:|\nOUTPUT:|\Z)", content, re.DOTALL
        )
        if flags_match:
            flags_text = flags_match.group(1).strip()
            if flags_text.lower() != "none" and flags_text:
                result["risk_flags"] = [
                    f.strip() for f in flags_text.split(",") if f.strip()
                ]

        # Parse REASONING
        reasoning_match = re.search(r"REASONING:\s*(.*?)$", content, re.DOTALL)
        if reasoning_match:
            result["reasoning"] = reasoning_match.group(1).strip()

        return result

    @staticmethod
    def _resolve_env_vars(config: Dict[str, Any]) -> Dict[str, Any]:
        """Replace ${VAR_NAME} patterns with environment variable values."""
        resolved = {}
        for key, value in config.items():
            if isinstance(value, str):
                # Replace ${VAR_NAME} with env var value
                def replace_var(match):
                    var_name = match.group(1)
                    return os.environ.get(var_name, "")

                resolved[key] = re.sub(r"\$\{(\w+)\}", replace_var, value)
            elif isinstance(value, dict):
                resolved[key] = Agent._resolve_env_vars(value)
            else:
                resolved[key] = value
        return resolved


class AgentRegistry:
    """Registry for loading and managing agents from YAML configuration."""

    def __init__(self):
        self._agents: Dict[str, Agent] = {}
        self._configs: Dict[str, AgentConfig] = {}
        self._conductor_config: Optional[Dict[str, Any]] = None

    def load_from_yaml(
        self, yaml_path: str, client_override: Optional[ModelClient] = None
    ):
        """Load agent configurations from a YAML file.

        Args:
            yaml_path: Path to agents.yaml
            client_override: If set, all agents use this client (useful for testing)
        """
        path = Path(yaml_path)
        if not path.exists():
            raise FileNotFoundError(f"Config file not found: {yaml_path}")

        with open(path) as f:
            config = yaml.safe_load(f)

        # Load agent configurations
        for agent_def in config.get("agents", []):
            agent_config = AgentConfig(
                name=agent_def["name"],
                role=agent_def.get("role", agent_def["name"]),
                system_prompt=agent_def.get("system_prompt", ""),
                model_provider=agent_def.get("model_provider", "mock"),
                model_config=agent_def.get("model_config", {}),
                temperature=agent_def.get("temperature", 0.7),
                max_tokens=agent_def.get("max_tokens", 2000),
                constraints=agent_def.get("constraints", {}),
            )
            self._configs[agent_config.name] = agent_config
            self._agents[agent_config.name] = Agent(
                config=agent_config, client=client_override
            )

        # Load conductor config
        if "conductor" in config:
            self._conductor_config = config["conductor"]

        logger.info(f"Loaded {len(self._agents)} agents from {yaml_path}")

    def get_agent(self, name: str) -> Agent:
        """Get an agent by name.

        Raises:
            KeyError: If agent not found
        """
        if name not in self._agents:
            raise KeyError(
                f"Agent '{name}' not found. Available: {list(self._agents.keys())}"
            )
        return self._agents[name]

    def list_agents(self) -> List[str]:
        """List all registered agent names."""
        return list(self._agents.keys())

    def has_agent(self, name: str) -> bool:
        """Check if an agent exists."""
        return name in self._agents

    def get_conductor_config(self) -> Optional[Dict[str, Any]]:
        """Get the conductor configuration."""
        return self._conductor_config

    def get_system_config(self) -> Dict[str, Any]:
        """Get system-level configuration (loaded from YAML)."""
        return {}

    def register_agent(self, agent: Agent):
        """Register an agent directly (not from YAML)."""
        self._agents[agent.name] = agent
        self._configs[agent.name] = agent.config
