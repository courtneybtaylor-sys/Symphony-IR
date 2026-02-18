# Changelog

All notable changes to Symphony-IR will be documented in this file.

This project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [v1.0.0-alpha] - 2026-02-18

### Initial Public Release

Symphony-IR is a compiler-grade runtime for multi-model AI orchestration. This
alpha release delivers the complete core pipeline: structured intermediate
representation, deterministic state machine orchestration, constitutional
governance, and measurable token efficiency.

### Core Components

- **Orchestrator State Machine** (`core/orchestrator.py`) -- Deterministic
  finite state machine with states INIT, PLAN, EXECUTE_PHASE, SYNTHESIZE,
  VALIDATE, TERMINATE, and ERROR. Hard phase limits and confidence thresholds
  ensure the LLM never decides when to stop; rules do. Parallel agent execution
  via ThreadPoolExecutor with configurable max workers.

- **Prompt IR Pipeline** (`core/prompt_ir.py`) -- Compiler-grade intermediate
  representation for prompts. The IR schema v1.0 is frozen as of this release.
  All fields documented in the `PromptIR` dataclass are part of the stable
  public API. See `IR_SPEC.md` for the full specification.

- **Prompt Compiler** (`core/prompt_compiler.py`) -- Five-step deterministic
  compilation pipeline:
  1. Template Selection -- Match agent role to YAML-defined prompt template
  2. Context Pruning -- Remove irrelevant context (up to 40% token reduction)
  3. Model Adaptation -- Claude receives XML wrapping, GPT receives JSON
     schemas, Ollama receives instruction tags
  4. Token Budget Enforcement -- Hard limits prevent runaway prompt sizes
  5. Schema Injection -- Append output format requirements for structured
     responses

- **Schema Validator** (`core/schema_validator.py`) -- Output format enforcement
  layer with auto-repair. Validates agent outputs against declared JSON,
  Markdown, and XML schemas. Auto-repairs common issues including missing
  braces, trailing commas, and single-quote substitution. Reduces synthesis
  failures by 50%+ and retry loops by 67%.

- **A/B Efficiency Statistics** (`core/efficiency_stats.py`) -- Quantifiable ROI
  measurement for the compiler pipeline. Compares compiled vs raw runs across
  token reduction, latency improvement, retry reduction, repair reduction, and
  cost savings. Includes model pricing tables for Claude (Opus/Sonnet/Haiku),
  GPT (4/4-turbo/3.5), and configurable defaults. Generates annual cost
  projections.

- **Ma'aT Governance Engine** (`core/governance.py`) -- Constitutional AI
  enforcement layer. Evaluates actions against six principles: Harm Prevention,
  Privacy Protection, Transparency, Human Sovereignty, Fairness, and
  Accountability. Supports APPROVE, DENY, FLAG, and REQUIRE_REVIEW decisions.
  Trust-based authorization with configurable thresholds. Full audit trail of
  every governance evaluation.

### IR Pipeline Components

- **PromptIR** -- Structured dataclass representing the intermediate
  representation of a prompt. Fields: role, intent, phase, context_refs,
  constraints, output_requirements, token_budget, priority, model_hint,
  temperature_hint, schema_id, ir_version, metadata, ir_id, created_at.
  Supports serialization via `to_dict()` / `from_dict()` and cloning via
  `clone()`.

- **PromptIRBuilder** -- Fluent builder for clean, explicit IR construction.
  Supports chained method calls for setting phase, context refs, constraints,
  output requirements, token budget, priority, model hint, temperature hint,
  schema ID, and metadata.

- **ContextDigestPlugin** -- Dual-stage compression plugin. When context
  references exceed a configurable threshold (default: 10), compresses them into
  a digest. Supports production-mode summarization via a cheap model. Falls back
  to a simple summary when no model is available. Stores original refs in
  metadata for audit trail.

- **BudgetOptimizerPlugin** -- Phase-aware and priority-aware token budget
  adjustment. Applies phase multipliers (Planning: 1.2x, Research: 1.3x,
  Implementation: 1.0x, Review: 0.8x, Synthesis: 1.1x) and priority bonuses
  (range: -0.4 to +0.5). Records original budget and multiplier in metadata.

- **IRGovernanceChecker** -- Pre-compilation governance layer that inspects IR
  intent before tokens are spent. Default policies: protected paths (DENY),
  destructive actions (FLAG), sensitive constraints (DENY). Saves 100% of token
  cost on rejected runs. Produces violations reports with approval rates.

- **PromptIRPipeline** -- Orchestrates the full IR processing flow: governance
  check (free, no tokens spent), plugin transformations (structured, auditable),
  and pipeline logging. Failed plugins are logged but do not halt the pipeline.
  Exposes pipeline statistics via `get_pipeline_stats()`.

### CLI Commands

- `symphony init` -- Initialize `.orchestrator/` directory with agents.yaml
  configuration, .env API key placeholders, runs/ history storage, and logs/
  directory. Supports `--force` to overwrite existing configuration.

- `symphony run <task>` -- Execute a full orchestration run. Options:
  - `--project <path>` -- Project root directory (default: current directory)
  - `--file <path>` -- Include a specific file in context
  - `--dry-run` -- Show plan without executing
  - `--no-compile` -- Disable prompt compiler, schema validator, and IR pipeline
  - `--no-ir` -- Disable IR pipeline only (use direct compilation)
  - `-v, --verbose` -- Detailed output with decision chain and
    compiler/validator/IR stats

- `symphony status` -- Show context provider availability, orchestrator
  directory state, and run count.

- `symphony history` -- Show recent orchestration runs. Supports `--detailed`
  for full decision chains and `--limit N` to control output.

- `symphony efficiency` -- Generate A/B efficiency report from saved run
  ledgers. Supports `--json` for JSON output and `--export <path>` to save
  the report to a file.

### Model Support

- **Anthropic Claude** -- Full support via the `anthropic` Python package.
  Prompt adaptation uses XML wrapping. Pricing tables included for Claude Opus
  4, Claude Sonnet 4, and Claude Haiku 4.

- **OpenAI GPT** -- Full support via the `openai` Python package. Prompt
  adaptation uses JSON schema formatting. Pricing tables included for GPT-4,
  GPT-4 Turbo, and GPT-3.5 Turbo.

- **Ollama Local Models** -- Full support via HTTP to localhost:11434. Prompt
  adaptation uses instruction tags (`[INST]...[/INST]`). No API key required.
  Supports Llama, Mistral, and any Ollama-compatible model.

- **Mock Testing** -- Role-aware mock model client for testing the full
  orchestration pipeline without API keys or network access. Ships with five
  pre-configured mock agents: architect, researcher, implementer, reviewer,
  integrator.

### Measured Results

- **55.7% token reduction** measured across compiled vs raw orchestration runs
  using the A/B efficiency statistics framework. Reduction attributed to context
  pruning (30-50%), model-specific adaptation (5-10%), and token budget
  enforcement.

### Schema Stability

- **IR schema v1.0 is frozen** as of this release. Stability guarantees:
  - All `PromptIR` fields listed in v1.0 will remain present in future 1.x
    releases.
  - New optional fields may be added (with defaults) in minor releases.
  - Serialization format (`to_dict()` / `from_dict()`) is stable and
    backwards-compatible.
  - Plugin `transform()` signature is stable: `(PromptIR) -> PromptIR`.
  - Pipeline `process()` signature is stable:
    `(PromptIR) -> (PromptIR, bool, List[str])`.
  - Breaking changes require a major version bump (2.0).

### Dependencies

- Python >= 3.9
- PyYAML >= 6.0
- python-dotenv >= 1.0.0

Optional:
- `anthropic` -- For Anthropic/Claude models
- `openai` -- For OpenAI/GPT models
- `requests` -- For Ollama local models

### Known Limitations

- Agent memory does not persist across runs (planned for Phase 2).
- No streaming output support (planned for Phase 2).
- Tool use (file write, code execution) not yet available (planned for Phase 2).
- Web UI dashboard not yet available (planned for Phase 3).
- Statistical significance of A/B comparisons requires 20+ runs minimum.

---

[v1.0.0-alpha]: https://github.com/kheper-company/symphony-ir/releases/tag/v1.0.0-alpha
