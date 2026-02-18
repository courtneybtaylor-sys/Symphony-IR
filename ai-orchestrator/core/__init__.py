"""Symphony-IR core: orchestration engine, governance, prompt compiler, schema validator, IR pipeline, and efficiency stats."""

__version__ = "1.0.0a1"

from .orchestrator import (
    OrchestratorState,
    Phase,
    AgentResponse,
    RunLedger,
    Orchestrator,
)
from .governance import (
    GovernanceDecision,
    GovernanceResult,
    MaaTGovernanceEngine,
)
from .prompt_compiler import (
    PromptCompiler,
    PromptFormat,
    PromptTemplate,
    CompiledPrompt,
    OutputSchema,
    TokenBudget,
)
from .schema_validator import (
    SchemaValidator,
    ValidationResult,
    ValidationReport,
)
from .prompt_ir import (
    IR_SCHEMA_VERSION,
    PhaseType,
    PromptIR,
    PromptIRBuilder,
    PromptIRPlugin,
    ContextDigestPlugin,
    BudgetOptimizerPlugin,
    IRGovernanceChecker,
    PromptIRPipeline,
    IRTransformation,
)
from .efficiency_stats import (
    EfficiencyCalculator,
    RunStats,
    ABComparison,
    RunLedgerParser,
    MODEL_PRICING,
)

__all__ = [
    "OrchestratorState",
    "Phase",
    "AgentResponse",
    "RunLedger",
    "Orchestrator",
    "GovernanceDecision",
    "GovernanceResult",
    "MaaTGovernanceEngine",
    "PromptCompiler",
    "PromptFormat",
    "PromptTemplate",
    "CompiledPrompt",
    "OutputSchema",
    "TokenBudget",
    "SchemaValidator",
    "ValidationResult",
    "ValidationReport",
    "PhaseType",
    "PromptIR",
    "PromptIRBuilder",
    "PromptIRPlugin",
    "ContextDigestPlugin",
    "BudgetOptimizerPlugin",
    "IRGovernanceChecker",
    "PromptIRPipeline",
    "IRTransformation",
    "IR_SCHEMA_VERSION",
    "EfficiencyCalculator",
    "RunStats",
    "ABComparison",
    "RunLedgerParser",
    "MODEL_PRICING",
]
