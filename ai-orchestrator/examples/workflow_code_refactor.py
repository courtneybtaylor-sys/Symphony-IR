#!/usr/bin/env python3
"""Symphony-IR Workflow Example: Code Refactoring Pipeline.

Demonstrates a 4-phase code refactoring workflow through the full IR pipeline:
  Phase 1 - Analysis:       Architect inspects legacy code structure
  Phase 2 - Refactoring Plan: Researcher identifies patterns and best practices
  Phase 3 - Implementation:  Implementer drafts refactored code
  Phase 4 - Review:          Reviewer validates the refactored output

Key features demonstrated:
  - PromptIR builder with per-phase configuration
  - IR pipeline with governance + plugins
  - Schema validation on agent outputs
  - Token savings measurement (compiled vs raw)
  - Full decision chain audit trail

Runs without API keys using MockModelClient.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.orchestrator import Orchestrator
from core.prompt_ir import (
    PromptIRBuilder,
    PhaseType,
    PromptIRPipeline,
    ContextDigestPlugin,
    BudgetOptimizerPlugin,
    IRGovernanceChecker,
)
from core.prompt_compiler import PromptCompiler
from core.schema_validator import SchemaValidator
from core.efficiency_stats import EfficiencyCalculator
from core.governance import MaaTGovernanceEngine
from models.client import MockModelClient
from agents.agent import Agent, AgentConfig, AgentRegistry


# ---------------------------------------------------------------------------
# Mock context: a Python project with legacy code that needs refactoring
# ---------------------------------------------------------------------------
LEGACY_CONTEXT = {
    "filesystem": {
        "root": "/projects/legacy-billing",
        "key_files": {
            "billing/processor.py": (
                "class BillingProcessor:\n"
                "    def process(self, data):\n"
                "        # 400-line monolith, no type hints, bare excepts\n"
                "        try:\n"
                "            result = data['amount'] * 1.1  # magic number\n"
                "            return result\n"
                "        except:\n"
                "            return -1\n"
            ),
            "billing/models.py": (
                "# No dataclasses, raw dicts everywhere\n"
                "def make_invoice(customer, items):\n"
                "    return {'customer': customer, 'items': items, 'total': 0}\n"
            ),
            "tests/test_billing.py": (
                "import unittest\n"
                "class TestBilling(unittest.TestCase):\n"
                "    def test_placeholder(self):\n"
                "        pass  # no real tests\n"
            ),
            "requirements.txt": "flask==1.1.4\nSQLAlchemy==1.3.0\n",
        },
    },
    "git": {
        "branch": "refactor/billing-v2",
        "status": "M billing/processor.py\nM billing/models.py",
    },
}


def build_agents():
    """Register the four specialist agents needed for this workflow."""
    registry = AgentRegistry()
    client = MockModelClient()
    roles = [
        ("architect", "System Architect"),
        ("researcher", "Researcher"),
        ("implementer", "Implementer"),
        ("reviewer", "Reviewer"),
    ]
    for name, role in roles:
        cfg = AgentConfig(
            name=name, role=role,
            system_prompt=f"You are the {role} agent.",
            model_provider="mock",
        )
        registry.register_agent(Agent(config=cfg, client=client))
    return registry


def build_phase_irs():
    """Build one PromptIR per refactoring phase."""
    phases = [
        PromptIRBuilder("architect", "Analyze legacy billing code for structural issues")
            .phase(PhaseType.PLANNING)
            .add_context_ref("file:billing/processor.py")
            .add_context_ref("file:billing/models.py")
            .add_constraint("Identify code smells and anti-patterns")
            .add_constraint("Classify severity of each issue")
            .set_output_requirements({"issues": "array", "severity_summary": "string"})
            .set_token_budget(3000)
            .set_priority(7)
            .build(),

        PromptIRBuilder("researcher", "Create a refactoring plan with best-practice references")
            .phase(PhaseType.RESEARCH)
            .add_context_ref("file:billing/processor.py")
            .add_context_ref("file:requirements.txt")
            .add_constraint("Reference PEP8, typing, and dataclass patterns")
            .set_output_requirements({"plan_steps": "array", "references": "array"})
            .set_token_budget(2500)
            .set_priority(6)
            .build(),

        PromptIRBuilder("implementer", "Implement refactored billing module with type hints")
            .phase(PhaseType.IMPLEMENTATION)
            .add_context_ref("file:billing/processor.py")
            .add_context_ref("file:billing/models.py")
            .add_context_ref("file:tests/test_billing.py")
            .add_constraint("Use dataclasses for models")
            .add_constraint("Replace bare excepts with specific exceptions")
            .add_constraint("Extract magic numbers into named constants")
            .set_output_requirements({"code": "string", "explanation": "string"})
            .set_token_budget(4000)
            .set_priority(8)
            .build(),

        PromptIRBuilder("reviewer", "Review refactored code for correctness and quality")
            .phase(PhaseType.REVIEW)
            .add_context_ref("file:billing/processor.py")
            .add_constraint("Check for regressions")
            .add_constraint("Verify type safety")
            .set_output_requirements({"issues": "array", "suggestions": "array"})
            .set_token_budget(2000)
            .set_priority(5)
            .build(),
    ]
    return phases


def run_ir_pipeline(phase_irs, pipeline):
    """Process each IR through governance + plugins, collecting results."""
    results = []
    for ir in phase_irs:
        transformed, approved, violations = pipeline.process(ir)
        results.append({
            "role": ir.role,
            "phase": ir.phase.value,
            "approved": approved,
            "violations": violations,
            "original_budget": ir.token_budget,
            "optimized_budget": transformed.token_budget,
            "ir_id": transformed.ir_id,
        })
    return results


def demonstrate_schema_validation(validator):
    """Show schema validation on sample agent outputs."""
    print("--- Schema Validation Demo ---")

    # Valid JSON output
    valid_output = '{"issues": ["bare except", "magic numbers"], "severity_summary": "high"}'
    schema = {"issues": "array", "severity_summary": "string"}
    report = validator.validate(valid_output, schema, format_type="json", role="architect")
    print(f"  Valid JSON   -> result={report.result.value}, errors={report.errors or 'none'}")

    # Invalid JSON (missing field)
    invalid_output = '{"issues": ["bare except"]}'
    report2 = validator.validate(invalid_output, schema, format_type="json", role="architect")
    print(f"  Missing field -> result={report2.result.value}, errors={report2.errors}")

    # Malformed JSON with auto-repair
    malformed = "{'code': 'def foo(): pass', 'explanation': 'refactored',}"
    code_schema = {"code": "string", "explanation": "string"}
    report3 = validator.validate(malformed, code_schema, format_type="json", role="implementer")
    print(f"  Auto-repair  -> result={report3.result.value}, warnings={report3.warnings}")
    print()


def compute_token_savings(ir_results):
    """Estimate token savings from IR optimization vs raw prompts."""
    raw_total = 0
    compiled_total = 0
    for r in ir_results:
        raw_total += r["original_budget"]
        compiled_total += r["optimized_budget"]
    saved = raw_total - compiled_total
    pct = (saved / raw_total * 100) if raw_total else 0
    return raw_total, compiled_total, saved, pct


def main():
    print("=" * 70)
    print("  SYMPHONY-IR WORKFLOW: Code Refactoring Pipeline")
    print("=" * 70)
    print()

    # --- Setup ---
    print("[1/7] Building agent registry...")
    registry = build_agents()
    print(f"  Agents: {', '.join(registry.list_agents())}")
    print()

    print("[2/7] Initializing IR pipeline (governance + plugins)...")
    pipeline = PromptIRPipeline(
        plugins=[
            ContextDigestPlugin(config={"max_context_refs": 10}),
            BudgetOptimizerPlugin(),
        ],
        governance=IRGovernanceChecker(),
    )
    print("  Plugins: ContextDigestPlugin, BudgetOptimizerPlugin")
    print("  Governance: IRGovernanceChecker (default policies)")
    print()

    print("[3/7] Initializing prompt compiler and schema validator...")
    config_path = Path(__file__).resolve().parent.parent / "config"
    compiler = PromptCompiler(templates_path=str(config_path))
    validator = SchemaValidator(config={"auto_repair": True})
    print(f"  Compiler templates: {', '.join(compiler.list_templates())}")
    print()

    # --- Build phase IRs ---
    print("[4/7] Building PromptIR for each refactoring phase...")
    phase_irs = build_phase_irs()
    for ir in phase_irs:
        print(f"  Phase: {ir.phase.value:16s} | Role: {ir.role:12s} | "
              f"Budget: {ir.token_budget} | Priority: {ir.priority}")
    print()

    # --- Run through IR pipeline ---
    print("[5/7] Processing IRs through pipeline...")
    ir_results = run_ir_pipeline(phase_irs, pipeline)
    for r in ir_results:
        status = "APPROVED" if r["approved"] else "DENIED"
        print(f"  {r['role']:12s} [{r['phase']:16s}] {status}  "
              f"budget: {r['original_budget']} -> {r['optimized_budget']}")
        if r["violations"]:
            for v in r["violations"]:
                print(f"    Violation: {v}")
    print()

    # --- Schema validation ---
    print("[6/7] Demonstrating schema validation...")
    demonstrate_schema_validation(validator)

    # --- Full orchestration ---
    print("[7/7] Running full orchestrated refactoring workflow...")

    def agent_executor(agent_name, phase_brief, ctx):
        if registry.has_agent(agent_name):
            return registry.get_agent(agent_name).execute(phase_brief, ctx)
        return {"agent_name": agent_name, "role": "unknown",
                "output": "Agent unavailable", "confidence": 0.0,
                "risk_flags": ["CRITICAL_missing_agent"], "reasoning": "Not found"}

    def provider_resolver(agent_name):
        return "mock"

    governance_engine = MaaTGovernanceEngine(user_trust_score=0.85)

    orchestrator = Orchestrator(
        config={"max_phases": 4, "confidence_threshold": 0.80},
        agent_executor=agent_executor,
        governance_checker=lambda a, d, c: governance_engine.evaluate_action(a, d, c),
        prompt_compiler=compiler,
        schema_validator=validator,
        agent_provider_resolver=provider_resolver,
        ir_pipeline=pipeline,
    )

    ledger = orchestrator.run(
        "Refactor legacy billing module: extract dataclasses, add type hints, "
        "replace bare excepts, remove magic numbers",
        LEGACY_CONTEXT,
    )

    # --- Summary ---
    print()
    print("=" * 70)
    print("  RESULTS SUMMARY")
    print("=" * 70)
    print(f"  Run ID:          {ledger.run_id}")
    print(f"  Final state:     {ledger.state}")
    print(f"  Phases executed: {len(ledger.phases)}")
    print(f"  Agent responses: {len(ledger.agent_responses)}")
    print(f"  Decisions:       {len(ledger.decisions)}")
    print(f"  Avg confidence:  {ledger.confidence:.2f}")
    print()

    # Token savings
    raw_t, comp_t, saved_t, pct_t = compute_token_savings(ir_results)
    print("  Token Budget Optimization:")
    print(f"    Raw budget total:      {raw_t}")
    print(f"    Optimized budget total: {comp_t}")
    print(f"    Tokens saved:          {saved_t} ({pct_t:.1f}%)")
    print()

    # Decision chain
    print("  Decision Chain (last 10):")
    for d in ledger.decisions[-10:]:
        print(f"    [{d.state:15s}] {d.action}")
    print()

    # Validator stats
    vs = validator.get_validation_stats()
    print(f"  Schema validations: {vs['total_validations']}, "
          f"success rate: {vs['success_rate']:.0%}, "
          f"repair rate: {vs['repair_rate']:.0%}")

    # Pipeline stats
    ps = pipeline.get_pipeline_stats()
    print(f"  IR pipeline runs: {ps['total_runs']}, "
          f"transformations: {ps['total_transformations']}")
    print()
    print("Workflow complete.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
