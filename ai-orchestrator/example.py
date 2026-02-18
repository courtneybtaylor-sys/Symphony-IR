#!/usr/bin/env python3
"""Symphony-IR Demo — Runs without API keys using mock models.

This demonstrates the full compiler-grade orchestration architecture:
- State machine execution
- Multi-agent coordination
- Prompt IR (Intermediate Representation) pipeline
- Prompt compilation (token optimization + model adaptation)
- Schema validation (output format enforcement)
- Governance checks (Ma'aT + IR governance)
- A/B efficiency statistics
- Audit trail generation
"""

import json
import sys
from pathlib import Path

# Add the package root to sys.path
PACKAGE_DIR = Path(__file__).resolve().parent
if str(PACKAGE_DIR) not in sys.path:
    sys.path.insert(0, str(PACKAGE_DIR))

from core.orchestrator import Orchestrator, Phase, AgentResponse
from core.governance import MaaTGovernanceEngine, GovernanceDecision
from core.prompt_compiler import PromptCompiler
from core.schema_validator import SchemaValidator
from core.prompt_ir import (
    IR_SCHEMA_VERSION,
    PhaseType,
    PromptIR,
    PromptIRBuilder,
    PromptIRPipeline,
    ContextDigestPlugin,
    BudgetOptimizerPlugin,
    IRGovernanceChecker,
)
from core.efficiency_stats import EfficiencyCalculator, RunLedgerParser
from models.client import MockModelClient, ModelFactory
from agents.agent import Agent, AgentConfig, AgentRegistry


def create_mock_context():
    """Create mock context simulating a real project."""
    return {
        "filesystem": {
            "root": "/example/project",
            "key_files": {
                "README.md": "# Example Auth Project\nA demonstration authentication system.",
                "requirements.txt": "flask>=3.0\npyjwt>=2.8\nbcrypt>=4.1\n",
            },
            "file_tree": [
                {"name": "src", "type": "dir", "children": [
                    {"name": "app.py", "type": "file"},
                    {"name": "models.py", "type": "file"},
                    {"name": "routes.py", "type": "file"},
                ]},
                {"name": "tests", "type": "dir", "children": [
                    {"name": "test_auth.py", "type": "file"},
                ]},
                {"name": "README.md", "type": "file"},
                {"name": "requirements.txt", "type": "file"},
            ],
        },
        "git": {
            "branch": "main",
            "status": "M src/routes.py\n?? src/auth/",
            "recent_commits": (
                "a1b2c3d Add user registration endpoint\n"
                "d4e5f6g Initial project setup\n"
                "h7i8j9k Add README and requirements"
            ),
            "diff_summary": " src/routes.py | 15 +++++++++------",
        },
    }


def create_mock_agents():
    """Create a registry of mock agents."""
    registry = AgentRegistry()
    mock_client = MockModelClient()

    agents = [
        AgentConfig(
            name="architect",
            role="System Architect",
            system_prompt="You are the System Architect agent.",
            model_provider="mock",
        ),
        AgentConfig(
            name="researcher",
            role="Researcher",
            system_prompt="You are the Researcher agent.",
            model_provider="mock",
        ),
        AgentConfig(
            name="implementer",
            role="Implementer",
            system_prompt="You are the Implementer agent.",
            model_provider="mock",
        ),
        AgentConfig(
            name="reviewer",
            role="Reviewer",
            system_prompt="You are the Reviewer agent.",
            model_provider="mock",
        ),
        AgentConfig(
            name="integrator",
            role="Integrator",
            system_prompt="You are the Integrator agent.",
            model_provider="mock",
        ),
    ]

    for config in agents:
        agent = Agent(config=config, client=mock_client)
        registry.register_agent(agent)

    return registry


def demo_ir_standalone():
    """Demonstrate Prompt IR as a standalone component."""
    print("=" * 70)
    print("  PROMPT IR DEMO — Standalone (Schema v{})".format(IR_SCHEMA_VERSION))
    print("=" * 70)
    print()

    # 1. Build an IR using the fluent builder
    print("[IR-1] Building PromptIR with fluent builder...")
    ir = (
        PromptIRBuilder("architect", "Design auth system with JWT tokens")
        .phase(PhaseType.PLANNING)
        .add_context_ref("file:auth.py")
        .add_context_ref("file:user.py")
        .add_constraint("Use OAuth2")
        .add_constraint("Support MFA")
        .set_token_budget(3000)
        .set_priority(8)
        .set_model_hint("anthropic")
        .build()
    )
    print(f"  IR ID:       {ir.ir_id}")
    print(f"  Role:        {ir.role}")
    print(f"  Intent:      {ir.intent}")
    print(f"  Phase:       {ir.phase.value}")
    print(f"  Context:     {ir.context_refs}")
    print(f"  Constraints: {ir.constraints}")
    print(f"  Budget:      {ir.token_budget}")
    print(f"  Priority:    {ir.priority}")
    print(f"  IR Version:  {ir.ir_version}")
    print()

    # 2. Demonstrate IR governance
    print("[IR-2] Running IR governance check...")
    governance = IRGovernanceChecker()
    approved, violations = governance.check(ir)
    print(f"  Approved: {approved}")
    print(f"  Violations: {violations or 'none'}")
    print()

    # Test with a dangerous IR
    print("[IR-3] Testing governance with dangerous intent...")
    dangerous_ir = (
        PromptIRBuilder("implementer", "delete all user data and drop database")
        .phase(PhaseType.IMPLEMENTATION)
        .add_context_ref("file:/etc/passwd")
        .build()
    )
    approved, violations = governance.check(dangerous_ir)
    print(f"  Approved: {approved}")
    for v in violations:
        print(f"  Violation: {v}")
    print()

    # 3. Demonstrate plugins
    print("[IR-4] Running BudgetOptimizerPlugin...")
    budget_plugin = BudgetOptimizerPlugin()
    optimized_ir = budget_plugin.transform(ir)
    print(f"  Original budget: {ir.token_budget}")
    print(f"  Optimized budget: {optimized_ir.token_budget}")
    print(f"  Phase multiplier: {optimized_ir.metadata.get('budget_multiplier')}")
    print()

    # 4. Demonstrate context digest
    print("[IR-5] Running ContextDigestPlugin on large context...")
    large_ir = (
        PromptIRBuilder("researcher", "Analyze codebase for security issues")
        .phase(PhaseType.RESEARCH)
        .add_context_refs([f"file:src/module_{i}.py" for i in range(15)])
        .set_token_budget(4000)
        .build()
    )
    print(f"  Context refs before: {len(large_ir.context_refs)} files")
    digest_plugin = ContextDigestPlugin(config={"max_context_refs": 10})
    digested_ir = digest_plugin.transform(large_ir)
    print(f"  Context refs after:  {len(digested_ir.context_refs)} (digest)")
    print(f"  Original preserved:  {len(digested_ir.metadata.get('original_context_refs', []))} refs in metadata")
    print()

    # 5. Full pipeline
    print("[IR-6] Running full IR pipeline...")
    pipeline = PromptIRPipeline(
        plugins=[
            ContextDigestPlugin(config={"max_context_refs": 10}),
            BudgetOptimizerPlugin(),
        ],
        governance=IRGovernanceChecker(),
    )
    transformed_ir, approved, violations = pipeline.process(ir)
    print(f"  Approved: {approved}")
    print(f"  Original budget: {ir.token_budget} -> Transformed: {transformed_ir.token_budget}")
    stats = pipeline.get_pipeline_stats()
    print(f"  Pipeline runs: {stats['total_runs']}")
    print(f"  Transformations: {stats['total_transformations']}")
    print()

    return governance


def demo_efficiency_stats():
    """Demonstrate A/B efficiency statistics."""
    print("=" * 70)
    print("  A/B EFFICIENCY STATS DEMO")
    print("=" * 70)
    print()

    # Simulated run data
    compiled_runs = [
        {
            "run_id": f"compiled_{i}",
            "compile_enabled": True,
            "total_input_tokens": 5000 + (i * 100),
            "total_output_tokens": 2000 + (i * 50),
            "duration_seconds": 30.0 + (i * 0.5),
            "retry_count": 0 if i % 3 != 0 else 1,
            "repair_count": 0 if i % 4 != 0 else 1,
            "model": "claude-sonnet-4",
        }
        for i in range(12)
    ]

    raw_runs = [
        {
            "run_id": f"raw_{i}",
            "compile_enabled": False,
            "total_input_tokens": 12000 + (i * 200),
            "total_output_tokens": 4000 + (i * 100),
            "duration_seconds": 45.0 + (i * 1.0),
            "retry_count": 1 if i % 2 == 0 else 2,
            "repair_count": 1 if i % 3 != 0 else 2,
            "model": "claude-sonnet-4",
        }
        for i in range(12)
    ]

    calculator = EfficiencyCalculator()

    # Generate text report
    print("[EFF-1] A/B Comparison Report:")
    print()
    report = calculator.generate_roi_report(compiled_runs, raw_runs, format="text")
    print(report)
    print()

    # Show JSON format
    print("[EFF-2] JSON Report (first 10 lines):")
    json_report = calculator.generate_roi_report(compiled_runs, raw_runs, format="json")
    for line in json_report.split("\n")[:10]:
        print(f"  {line}")
    print("  ...")
    print()


def main():
    print("=" * 70)
    print("  SYMPHONY-IR — Full Architecture Demo")
    print("  Compiler-Grade Runtime for Multi-Model AI Orchestration")
    print("  IR Schema v{}".format(IR_SCHEMA_VERSION))
    print("=" * 70)
    print()

    # === Part 1: Standalone IR Demo ===
    ir_governance = demo_ir_standalone()

    # === Part 2: A/B Efficiency Stats Demo ===
    demo_efficiency_stats()

    # === Part 3: Full Orchestration with IR Pipeline ===
    print("=" * 70)
    print("  FULL ORCHESTRATION WITH IR PIPELINE")
    print("=" * 70)
    print()

    # Step 1: Create mock context
    print("[1/9] Creating mock project context...")
    context = create_mock_context()
    print(f"  - Filesystem context: {context['filesystem']['root']}")
    print(f"  - Git branch: {context['git']['branch']}")
    print()

    # Step 2: Set up agents
    print("[2/9] Initializing agent registry...")
    registry = create_mock_agents()
    print(f"  - Agents: {', '.join(registry.list_agents())}")
    print()

    # Step 3: Set up governance
    print("[3/9] Initializing Ma'aT governance engine...")
    governance = MaaTGovernanceEngine(user_trust_score=0.85)
    print(f"  - Principles: {', '.join(governance.get_principles().keys())}")
    print()

    # Step 4: Set up prompt compiler
    print("[4/9] Initializing prompt compiler...")
    config_path = PACKAGE_DIR / "config"
    compiler = PromptCompiler(templates_path=str(config_path))
    print(f"  - Templates: {', '.join(compiler.list_templates())}")
    print()

    # Step 5: Set up schema validator
    print("[5/9] Initializing schema validator...")
    validator = SchemaValidator(config={"auto_repair": True, "max_repair_attempts": 3})
    print(f"  - Auto-repair: enabled")
    print()

    # Step 6: Set up IR pipeline
    print("[6/9] Initializing IR pipeline (v{})...".format(IR_SCHEMA_VERSION))
    ir_pipeline = PromptIRPipeline(
        plugins=[
            ContextDigestPlugin(config={"max_context_refs": 10}),
            BudgetOptimizerPlugin(),
        ],
        governance=IRGovernanceChecker(),
    )
    print(f"  - Plugins: ContextDigestPlugin, BudgetOptimizerPlugin")
    print(f"  - Governance: IRGovernanceChecker (3 default policies)")
    print()

    # Step 7: Run orchestration
    task = "Design and implement a new authentication system with JWT tokens, " \
           "password hashing, and role-based access control"

    print("[7/9] Running orchestration with IR pipeline...")
    print(f"  Task: {task}")
    print("-" * 70)

    def agent_executor(agent_name, phase_brief, ctx):
        if registry.has_agent(agent_name):
            agent = registry.get_agent(agent_name)
            return agent.execute(phase_brief, ctx)
        return {
            "agent_name": agent_name,
            "role": "unknown",
            "output": f"Agent '{agent_name}' not available",
            "confidence": 0.0,
            "risk_flags": ["CRITICAL_missing_agent"],
            "reasoning": "Agent not found in registry",
        }

    def agent_provider_resolver(agent_name):
        if registry.has_agent(agent_name):
            return registry.get_agent(agent_name).config.model_provider
        return "mock"

    def governance_checker(action_type, details, ctx):
        return governance.evaluate_action(action_type, details, ctx)

    orchestrator = Orchestrator(
        config={
            "max_phases": 3,
            "confidence_threshold": 0.85,
            "enable_parallel_execution": True,
        },
        agent_executor=agent_executor,
        governance_checker=governance_checker,
        prompt_compiler=compiler,
        schema_validator=validator,
        agent_provider_resolver=agent_provider_resolver,
        ir_pipeline=ir_pipeline,
    )

    ledger = orchestrator.run(task, context)

    # Step 8: Display results
    print()
    print("[8/9] Results")
    print("=" * 70)
    print(f"  Run ID:        {ledger.run_id}")
    print(f"  Final State:   {ledger.state}")
    print(f"  Phases:        {len(ledger.phases)}")
    print(f"  Agent Calls:   {len(ledger.agent_responses)}")
    print(f"  Decisions:     {len(ledger.decisions)}")
    print(f"  Confidence:    {ledger.confidence:.2f}")
    print()

    # Show decision chain
    print("Decision Chain:")
    print("-" * 70)
    for i, d in enumerate(ledger.decisions, 1):
        print(f"  {i}. [{d.state:15s}] {d.action}")
        print(f"     Reason: {d.reason}")
    print()

    # Show agent responses summary
    print("Agent Responses:")
    print("-" * 70)
    for r in ledger.agent_responses:
        flags = ", ".join(r.risk_flags) if r.risk_flags else "none"
        compiled = "IR+compiled" if r.metadata.get("compiled") else "raw"
        print(f"  {r.agent_name:12s} ({r.role:18s}) conf={r.confidence:.2f}  flags={flags}  [{compiled}]")
    print()

    # Prompt compiler stats
    compiler_stats = compiler.get_compilation_stats()
    print("Prompt Compiler Stats:")
    print("-" * 70)
    print(f"  Compilations:     {compiler_stats['total_compilations']}")
    print(f"  Total tokens est: {compiler_stats['total_tokens_estimated']}")
    print(f"  Avg tokens/prompt:{compiler_stats['average_tokens_per_prompt']}")
    print(f"  Compression rate: {compiler_stats['compression_rate']:.1%}")
    print()

    # Schema validator stats
    validator_stats = validator.get_validation_stats()
    print("Schema Validator Stats:")
    print("-" * 70)
    print(f"  Validations:      {validator_stats['total_validations']}")
    print(f"  Success rate:     {validator_stats['success_rate']:.1%}")
    print(f"  Repair rate:      {validator_stats['repair_rate']:.1%}")
    print(f"  Errors by role:   {validator_stats['errors_by_role'] or 'none'}")
    print()

    # IR pipeline stats
    ir_stats = ir_pipeline.get_pipeline_stats()
    print("IR Pipeline Stats (v{}):".format(IR_SCHEMA_VERSION))
    print("-" * 70)
    print(f"  Pipeline runs:      {ir_stats['total_runs']}")
    print(f"  Transformations:    {ir_stats['total_transformations']}")
    print(f"  Avg transforms/run: {ir_stats['avg_transformations_per_run']:.1f}")
    print()

    # IR governance report
    ir_gov_report = ir_pipeline.governance.get_violations_report()
    print("IR Governance Report:")
    print("-" * 70)
    print(f"  Total checks:   {ir_gov_report['total_checks']}")
    print(f"  Approved:       {ir_gov_report['approved']}")
    print(f"  Denied:         {ir_gov_report['denied']}")
    print(f"  Approval rate:  {ir_gov_report['approval_rate']:.1%}")
    print()

    # Ma'aT governance audit
    audit_log = governance.get_audit_log()
    if audit_log:
        print("Ma'aT Governance Audit:")
        print("-" * 70)
        for entry in audit_log:
            print(f"  [{entry['decision']:14s}] {entry['action_type']}: {entry['reason'][:60]}")
        print()

    # Step 9: Architecture demonstration
    print("[9/9] Architecture Demonstrated:")
    print("-" * 70)
    print("  [x] Deterministic state machine (INIT -> PLAN -> EXECUTE -> SYNTHESIZE -> VALIDATE -> TERMINATE)")
    print("  [x] Model-agnostic abstraction (MockModelClient swappable for OpenAI/Anthropic/Ollama)")
    print("  [x] Conductor + Specialist pattern (5 specialist agents)")
    print("  [x] Structured output parsing (OUTPUT/CONFIDENCE/RISK_FLAGS/REASONING)")
    print("  [x] Prompt IR pipeline (PromptIR -> Governance -> Plugins -> CompiledPrompt)")
    print("  [x] IR schema v{} frozen with stability guarantees".format(IR_SCHEMA_VERSION))
    print("  [x] IR governance (policy-based intent inspection before token spend)")
    print("  [x] IR plugins (ContextDigestPlugin, BudgetOptimizerPlugin)")
    print("  [x] Prompt compiler (template selection, context pruning, model adaptation, token budgets)")
    print("  [x] Schema validator (output format enforcement, auto-repair, validation stats)")
    print("  [x] Ma'aT governance layer (constitutional principle checks)")
    print("  [x] A/B efficiency statistics (token/latency/cost reduction measurement)")
    print("  [x] Complete audit trail (RunLedger with all decisions)")
    print("  [x] Hard termination limits (max_phases=3)")
    print("  [x] Confidence threshold validation (threshold=0.85)")
    print("  [x] Risk flag detection (CRITICAL_ prefix detection)")
    print("  [x] Parallel agent execution support")
    print()

    # Save demo ledger
    demo_ledger_path = PACKAGE_DIR / "demo_run.json"
    orchestrator.save_ledger(str(demo_ledger_path))
    print(f"  Demo ledger saved to: {demo_ledger_path}")
    print()

    # Next steps
    print("Next Steps:")
    print("-" * 70)
    print("  1. Run 'symphony init' to set up your project")
    print("  2. Add API keys to .symphony/.env")
    print("  3. Customize agents in .symphony/agents.yaml")
    print("  4. Customize prompt templates in config/prompt_templates.yaml")
    print('  5. Run: symphony run "your task here"')
    print('  6. Run: symphony run --no-ir "task" (skip IR pipeline)')
    print('  7. Run: symphony efficiency (A/B report)')
    print()
    print("  Swap models by changing model_provider in agents.yaml:")
    print("    anthropic -> Anthropic/Claude")
    print("    openai    -> OpenAI/GPT")
    print("    ollama    -> Local models (Llama, Mistral, etc.)")
    print("    mock      -> Testing without API keys")
    print()

    return 0


if __name__ == "__main__":
    sys.exit(main())
