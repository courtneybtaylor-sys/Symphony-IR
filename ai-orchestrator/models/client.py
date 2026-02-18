"""Model abstraction layer with adapters for OpenAI, Anthropic, Ollama, and Ma'aT.

All agents interact with models through the unified ModelClient interface.
Swap models via config, not code.
"""

import json
import logging
import os
import random
import string
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class ModelProvider(Enum):
    """Supported model providers."""

    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    OLLAMA = "ollama"
    MAAT = "maat"
    MOCK = "mock"


@dataclass
class Message:
    """A single message in a conversation."""

    role: str  # "system", "user", "assistant"
    content: str


@dataclass
class ModelResponse:
    """Unified response from any model provider."""

    content: str
    provider: ModelProvider
    model: str
    usage: Dict[str, int] = field(default_factory=dict)
    raw_response: Optional[Any] = None


class ModelClient(ABC):
    """Abstract base class for all model clients."""

    @abstractmethod
    def call(
        self,
        messages: List[Message],
        temperature: float = 0.7,
        max_tokens: int = 2000,
        tools: Optional[List[Dict]] = None,
    ) -> ModelResponse:
        """Send messages to the model and get a response."""
        pass

    @abstractmethod
    def get_provider(self) -> ModelProvider:
        """Return the model provider enum."""
        pass

    @abstractmethod
    def get_model_name(self) -> str:
        """Return the model name string."""
        pass


class OpenAIClient(ModelClient):
    """Client for OpenAI API (GPT models)."""

    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o", **kwargs):
        self._model = model
        self._api_key = api_key or os.environ.get("OPENAI_API_KEY", "")
        self._client = None

    def _get_client(self):
        if self._client is None:
            try:
                from openai import OpenAI

                self._client = OpenAI(api_key=self._api_key)
            except ImportError:
                raise ImportError(
                    "openai package required. Install with: pip install openai"
                )
        return self._client

    def call(
        self,
        messages: List[Message],
        temperature: float = 0.7,
        max_tokens: int = 2000,
        tools: Optional[List[Dict]] = None,
    ) -> ModelResponse:
        client = self._get_client()
        msg_dicts = [{"role": m.role, "content": m.content} for m in messages]

        kwargs = {
            "model": self._model,
            "messages": msg_dicts,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        if tools:
            kwargs["tools"] = tools

        response = client.chat.completions.create(**kwargs)
        choice = response.choices[0]

        return ModelResponse(
            content=choice.message.content or "",
            provider=ModelProvider.OPENAI,
            model=self._model,
            usage={
                "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
                "completion_tokens": response.usage.completion_tokens
                if response.usage
                else 0,
                "total_tokens": response.usage.total_tokens if response.usage else 0,
            },
            raw_response=response,
        )

    def get_provider(self) -> ModelProvider:
        return ModelProvider.OPENAI

    def get_model_name(self) -> str:
        return self._model


class AnthropicClient(ModelClient):
    """Client for Anthropic API (Claude models)."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "claude-sonnet-4-20250514",
        **kwargs,
    ):
        self._model = model
        self._api_key = api_key or os.environ.get("ANTHROPIC_API_KEY", "")
        self._client = None

    def _get_client(self):
        if self._client is None:
            try:
                import anthropic

                self._client = anthropic.Anthropic(api_key=self._api_key)
            except ImportError:
                raise ImportError(
                    "anthropic package required. Install with: pip install anthropic"
                )
        return self._client

    def call(
        self,
        messages: List[Message],
        temperature: float = 0.7,
        max_tokens: int = 2000,
        tools: Optional[List[Dict]] = None,
    ) -> ModelResponse:
        client = self._get_client()

        # Anthropic uses system as a separate parameter
        system_prompt = ""
        conversation = []
        for m in messages:
            if m.role == "system":
                system_prompt += m.content + "\n"
            else:
                conversation.append({"role": m.role, "content": m.content})

        # Ensure conversation starts with user message
        if not conversation or conversation[0]["role"] != "user":
            conversation.insert(0, {"role": "user", "content": "Begin."})

        kwargs = {
            "model": self._model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": conversation,
        }
        if system_prompt.strip():
            kwargs["system"] = system_prompt.strip()
        if tools:
            kwargs["tools"] = tools

        response = client.messages.create(**kwargs)

        content = ""
        for block in response.content:
            if hasattr(block, "text"):
                content += block.text

        return ModelResponse(
            content=content,
            provider=ModelProvider.ANTHROPIC,
            model=self._model,
            usage={
                "input_tokens": response.usage.input_tokens if response.usage else 0,
                "output_tokens": response.usage.output_tokens if response.usage else 0,
            },
            raw_response=response,
        )

    def get_provider(self) -> ModelProvider:
        return ModelProvider.ANTHROPIC

    def get_model_name(self) -> str:
        return self._model


class OllamaClient(ModelClient):
    """Client for local Ollama models via HTTP API."""

    def __init__(
        self,
        model: str = "llama3.2",
        base_url: str = "http://localhost:11434",
        **kwargs,
    ):
        self._model = model
        self._base_url = base_url.rstrip("/")

    def call(
        self,
        messages: List[Message],
        temperature: float = 0.7,
        max_tokens: int = 2000,
        tools: Optional[List[Dict]] = None,
    ) -> ModelResponse:
        try:
            import requests
        except ImportError:
            raise ImportError(
                "requests package required. Install with: pip install requests"
            )

        msg_dicts = [{"role": m.role, "content": m.content} for m in messages]

        payload = {
            "model": self._model,
            "messages": msg_dicts,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            },
        }

        response = requests.post(
            f"{self._base_url}/api/chat",
            json=payload,
            timeout=120,
        )
        response.raise_for_status()
        data = response.json()

        return ModelResponse(
            content=data.get("message", {}).get("content", ""),
            provider=ModelProvider.OLLAMA,
            model=self._model,
            usage={
                "prompt_tokens": data.get("prompt_eval_count", 0),
                "completion_tokens": data.get("eval_count", 0),
            },
            raw_response=data,
        )

    def get_provider(self) -> ModelProvider:
        return ModelProvider.OLLAMA

    def get_model_name(self) -> str:
        return self._model


class MaaTClient(ModelClient):
    """Placeholder client for Ma'aT governance engine.

    This will be expanded as the governance engine matures.
    Currently delegates to a backing model with governance wrapping.
    """

    def __init__(self, model: str = "maat-v1", **kwargs):
        self._model = model

    def call(
        self,
        messages: List[Message],
        temperature: float = 0.7,
        max_tokens: int = 2000,
        tools: Optional[List[Dict]] = None,
    ) -> ModelResponse:
        # Placeholder: return a governance-aware response
        combined = "\n".join(m.content for m in messages if m.role == "user")
        return ModelResponse(
            content=(
                f"OUTPUT: Ma'aT governance review of: {combined[:200]}\n"
                f"CONFIDENCE: 0.9\n"
                f"RISK_FLAGS: none\n"
                f"REASONING: Governance review placeholder - real implementation pending"
            ),
            provider=ModelProvider.MAAT,
            model=self._model,
            usage={},
        )

    def get_provider(self) -> ModelProvider:
        return ModelProvider.MAAT

    def get_model_name(self) -> str:
        return self._model


class MockModelClient(ModelClient):
    """Mock client for testing and demos without API keys."""

    def __init__(self, model: str = "mock-v1", responses: Optional[Dict] = None, **kwargs):
        self._model = model
        self._responses = responses or {}
        self._call_count = 0

    def call(
        self,
        messages: List[Message],
        temperature: float = 0.7,
        max_tokens: int = 2000,
        tools: Optional[List[Dict]] = None,
    ) -> ModelResponse:
        self._call_count += 1

        # Check if there's a custom response for the system prompt role
        system_content = ""
        user_content = ""
        for m in messages:
            if m.role == "system":
                system_content = m.content
            elif m.role == "user":
                user_content = m.content

        # Try to match a custom response by role keywords
        content = None
        for key, resp in self._responses.items():
            if key.lower() in system_content.lower():
                content = resp
                break

        if content is None:
            content = self._generate_mock_response(system_content, user_content)

        return ModelResponse(
            content=content,
            provider=ModelProvider.MOCK,
            model=self._model,
            usage={"prompt_tokens": 100, "completion_tokens": 200, "total_tokens": 300},
        )

    def _generate_mock_response(self, system_content: str, user_content: str) -> str:
        """Generate a structured mock response based on the role detected in system prompt."""
        role = "general"
        role_map = {
            "conductor": "conductor",
            "planner": "conductor",
            "architect": "architect",
            "researcher": "researcher",
            "implementer": "implementer",
            "reviewer": "reviewer",
            "integrator": "integrator",
        }
        for keyword, r in role_map.items():
            if keyword in system_content.lower():
                role = r
                break

        responses = {
            "conductor": (
                "PHASES:\n"
                "1. Analysis Phase: Analyze requirements and constraints\n"
                "   Agents: [architect, researcher]\n"
                "   Termination: Requirements documented with confidence > 0.8\n"
                "2. Design Phase: Create system architecture\n"
                "   Agents: [architect, implementer]\n"
                "   Termination: Architecture approved with no CRITICAL flags\n"
                "3. Implementation Phase: Build the solution\n"
                "   Agents: [implementer, reviewer]\n"
                "   Termination: Code complete with tests passing\n"
                "4. Integration Phase: Synthesize and validate\n"
                "   Agents: [integrator, reviewer]\n"
                "   Termination: All components integrated with confidence > 0.85"
            ),
            "architect": (
                "OUTPUT: System architecture analysis complete.\n"
                "- Component decomposition: 4 core modules identified\n"
                "- Data flow: Event-driven with message queue\n"
                "- Security: OAuth2 + JWT token rotation\n"
                "- Scalability: Horizontal scaling via stateless services\n"
                "- Risk: Database migration complexity is medium\n"
                "CONFIDENCE: 0.88\n"
                "RISK_FLAGS: MODERATE_complexity_migration\n"
                "REASONING: Architecture follows microservices best practices "
                "with clear separation of concerns."
            ),
            "researcher": (
                "OUTPUT: Research findings summary.\n"
                "- Prior art: 3 similar implementations reviewed\n"
                "- Best practices: OWASP guidelines applicable\n"
                "- Dependencies: 2 well-maintained libraries identified\n"
                "- Documentation: API specs available for integration\n"
                "CONFIDENCE: 0.92\n"
                "RISK_FLAGS: none\n"
                "REASONING: Sufficient prior art exists. Recommended approach "
                "aligns with industry standards."
            ),
            "implementer": (
                "OUTPUT: Implementation plan and code structure.\n"
                "- Core module: Authentication service with JWT\n"
                "- Database: PostgreSQL with migration scripts\n"
                "- API endpoints: 5 RESTful routes defined\n"
                "- Tests: Unit and integration test scaffolding\n"
                "CONFIDENCE: 0.85\n"
                "RISK_FLAGS: none\n"
                "REASONING: Implementation follows architect's design. "
                "Standard patterns used for maintainability."
            ),
            "reviewer": (
                "OUTPUT: Code review and quality assessment.\n"
                "- Code quality: Follows project conventions\n"
                "- Edge cases: 3 identified, 2 handled\n"
                "- Security: No vulnerabilities detected\n"
                "- Performance: O(n) complexity acceptable\n"
                "- Suggestion: Add rate limiting to auth endpoints\n"
                "CONFIDENCE: 0.87\n"
                "RISK_FLAGS: MODERATE_missing_rate_limiting\n"
                "REASONING: Implementation is solid with minor improvements needed. "
                "No critical issues found."
            ),
            "integrator": (
                "OUTPUT: Integration synthesis complete.\n"
                "- All components verified for compatibility\n"
                "- API contracts validated between services\n"
                "- End-to-end flow tested successfully\n"
                "- Documentation updated with integration notes\n"
                "CONFIDENCE: 0.90\n"
                "RISK_FLAGS: none\n"
                "REASONING: All specialist outputs are consistent and compatible. "
                "System is ready for deployment."
            ),
            "general": (
                "OUTPUT: Analysis complete for the given task.\n"
                "- Key findings documented\n"
                "- Recommendations provided\n"
                "CONFIDENCE: 0.85\n"
                "RISK_FLAGS: none\n"
                "REASONING: Standard analysis applied to the task."
            ),
        }

        return responses.get(role, responses["general"])

    def get_provider(self) -> ModelProvider:
        return ModelProvider.MOCK

    def get_model_name(self) -> str:
        return self._model


class ModelFactory:
    """Factory for creating model clients from configuration."""

    _registry: Dict[str, type] = {
        "openai": OpenAIClient,
        "anthropic": AnthropicClient,
        "ollama": OllamaClient,
        "maat": MaaTClient,
        "mock": MockModelClient,
    }

    @staticmethod
    def create(provider: str, **kwargs) -> ModelClient:
        """Create a model client by provider name.

        Args:
            provider: Provider name (openai, anthropic, ollama, maat, mock)
            **kwargs: Provider-specific configuration (api_key, model, etc.)

        Returns:
            Configured ModelClient instance

        Raises:
            ValueError: If provider is not recognized
        """
        provider_lower = provider.lower()
        if provider_lower not in ModelFactory._registry:
            raise ValueError(
                f"Unknown provider: {provider}. "
                f"Available: {list(ModelFactory._registry.keys())}"
            )

        client_class = ModelFactory._registry[provider_lower]
        return client_class(**kwargs)

    @staticmethod
    def register(name: str, client_class: type):
        """Register a custom model client.

        Args:
            name: Provider name to register
            client_class: ModelClient subclass
        """
        ModelFactory._registry[name.lower()] = client_class

    @staticmethod
    def available_providers() -> List[str]:
        """List all registered provider names."""
        return list(ModelFactory._registry.keys())
