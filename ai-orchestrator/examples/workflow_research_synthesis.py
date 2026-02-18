#!/usr/bin/env python3
"""Symphony-IR Workflow Example: Research and Synthesis Pipeline.

Demonstrates a 5-agent sequential research pipeline:
  1. Architect  -- scope the research domain and define structure
  2. Researcher -- gather findings from academic/technical sources
  3. Implementer -- draft a structured synthesis document
  4. Reviewer   -- critique the draft for gaps and bias
  5. Integrator -- produce the final synthesized deliverable

Key features demonstrated:
  - All 5 specialist agents used in sequence
  - Priority-based budget allocation (high priority = more tokens)
  - A/B efficiency comparison (compiled vs raw simulated runs)
  - Formatted efficiency report output
  - Full decision chain and audit trail

Runs without API keys using MockModelClient.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.orchestrator import Orchestrator, Phase
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
# Mock context: academic/technical research data
# ---------------------------------------------------------------------------
RESEARCH_CONTEXT = {
    "filesystem": {
        "root": "/research/llm-orchestration-survey",
        "key_files": {
            "papers/chain_of_thought.md": (
                "# Chain-of-Thought Prompting\n"
                "Wei et al. (2022) showed that CoT prompting improves reasoning\n"
                "accuracy by 15-30% on arithmetic and symbolic tasks.\n"
            ),
            "papers/react_framework.md": (
                "# ReAct: Synergizing Reasoning and Acting\n"
                "Yao et al. (2023) combined reasoning traces with actions,\n"
                "achieving state-of-the-art on knowledge-intensive tasks.\n"
            ),
            "papers/multi_agent_debate.md": (
                "# Multi-Agent Debate\n"
                "Du et al. (2023) found that multi-agent debate reduces\n"
                "hallucination rates by 40% compared to single-agent setups.\n"
            ),
            "papers/constitutional_ai.md": (
                "# Constitutional AI\n"
                "Bai et al. (2022) demonstrated self-improvement through\n"
                "constitutional principles, reducing harmful outputs by 60%.\n"
            ),
            "notes/research_questions.md": (
                "# Research Questions\n"
                "1. How do orchestration patterns affect output quality?\n"
                "2. What is the optimal agent count for code tasks?\n"
                "3. How does governance overhead impact latency?\n"
            ),
        },
    },
    "git": {
        "branch": "research/survey-draft",
        "status": "clean",
    },
}


def build_all_agents():
    """Register all 5 specialist agents."""
    registry = AgentRegistry()
    client = MockModelClient()
    agents = [
        ("architect", "Research Architect"),
        ("researcher", "Literature Researcher"),
        ("implementer", "Draft Writer"),
        ("reviewer", "Peer Reviewer"),
        ("integrator", "Synthesis Integrator"),
    ]
    for name, role in agents:
        cfg = AgentConfig(
            name=name, role=role,
            system_prompt=f"You are the {role} agent for academic research synthesis.",
            model_provider="mock",
        )
        registry.register_agent(Agent(config=cfg, client=client))
    return registry


def build_research_phases():
    """Define the 5-phase research pipeline with priority-based budgets."""
    return [
        (
            "Scope Definition",
            PromptIRBuilder("architect", "Define research scope for LLM orchestration survey")
                .phase(PhaseType.PLANNING)
                .add_context_ref("file:notes/research_questions.md")
                .add_constraint("Identify 3-5 key themes")
                .add_constraint("Define inclusion/exclusion criteria")
                .set_token_budget(2000)
                .set_priority(6)
                .set_schema_id("planning_output")
                .build()
        ),
        (
            "Literature Gathering",
            PromptIRBuilder("researcher", "Gather and summarize findings on LLM orchestration")
                .phase(PhaseType.RESEARCH)
                .add_context_ref("file:papers/chain_of_thought.md")
                .add_context_ref("file:papers/react_framework.md")
                .add_context_ref("file:papers/multi_agent_debate.md")
                .add_context_ref("file:papers/constitutional_ai.md")
                .add_constraint("Summarize key contributions of each paper")
                .add_constraint("Identify methodological strengths and weaknesses")
                .set_token_budget(4000)
                .set_priority(9)
                .set_schema_id("research_output")
                .build()
        ),
        (
            "Draft Writing",
            PromptIRBuilder("implementer", "Draft a structured survey section")
                .phase(PhaseType.IMPLEMENTATION)
                .add_context_ref("file:papers/chain_of_thought.md")
                .add_context_ref("file:papers/react_framework.md")
                .add_constraint("Use academic writing style")
                .add_constraint("Include comparison table")
                .set_token_budget(5000)
                .set_priority(8)
                .set_schema_id("draft_output")
                .build()
        ),
        (
            "Peer Review",
            PromptIRBuilder("reviewer", "Review draft for gaps, bias, and accuracy")
                .phase(PhaseType.REVIEW)
                .add_context_ref("file:notes/research_questions.md")
                .add_constraint("Check citation accuracy")
                .add_constraint("Identify missing perspectives")
                .add_constraint("Flag unsupported claims")
                .set_token_budget(2500)
                .set_priority(7)
                .set_schema_id("review_output")
                .build()
        ),
        (
            "Final Synthesis",
            PromptIRBuilder("integrator", "Synthesize all agent outputs into final survey section")
                .phase(PhaseType.SYNTHESIS)
                .add_context_ref("file:notes/research_questions.md")
                .add_constraint("Resolve conflicting findings")
                .add_constraint("Produce coherent narrative")
                .set_token_budget(3500)
                .set_priority(8)
                .set_schema_id("synthesis_output")
                .build()
        ),
    ]


def demonstrate_priority_budgets(phases, pipeline):
    """Show how priority affects token budget allocation."""
    print("--- Priority-Based Budget Allocation ---")
    print(f"  {'Phase':<25s} {'Role':<14s} {'Priority':>8s} {'Base':>6s} {'Optimized':>10s} {'Delta':>8s}")
    print("  " + "-" * 75)

    for label, ir in phases:
        transformed, approved, _ = pipeline.process(ir)
        base = ir.token_budget
        opt = transformed.token_budget
        delta = opt - base
        sign = "+" if delta >= 0 else ""
        print(f"  {label:<25s} {ir.role:<14s} {ir.priority:>8d} {base:>6d} {opt:>10d} {sign}{delta:>7d}")
    print()


def generate_ab_comparison():
    """Generate A/B efficiency comparison with simulated data."""
    print("--- A/B Efficiency Comparison ---")
    print()

    compiled_runs = [
        {
            "run_id": f"compiled_{i}",
            "compile_enabled": True,
            "total_input_tokens": 4500 + (i * 80),
            "total_output_tokens": 1800 + (i * 40),
            "duration_seconds": 25.0 + (i * 0.4),
            "retry_count": 0 if i % 4 != 0 else 1,
            "repair_count": 0 if i % 5 != 0 else 1,
            "model": "default",
        }
        for i in range(15)
    ]

    raw_runs = [
        {
            "run_id": f"raw_{i}",
            "compile_enabled": False,
            "total_input_tokens": 11000 + (i * 180),
            "total_output_tokens": 3800 + (i * 90),
            "duration_seconds": 42.0 + (i * 0.9),
            "retry_count": 1 if i % 2 == 0 else 2,
            "repair_count": 1 if i % 3 != 0 else 2,
            "model": "default",
        }
        for i in range(15)
    ]

    calculator = EfficiencyCalculator()
    report = calculator.generate_roi_report(compiled_runs, raw_runs, format="text")
    print(report)
    print()
    return calculator, compiled_runs, raw_runs


def run_orchestrated_pipeline():
    """Run the full 5-agent orchestrated research synthesis."""
    registry = build_all_agents()
    config_path = Path(__file__).resolve().parent.parent / "config"

    compiler = PromptCompiler(templates_path=str(config_path))
    validator = SchemaValidator(config={"auto_repair": True})
    governance = MaaTGovernanceEngine(user_trust_score=0.9)

    pipeline = PromptIRPipeline(
        plugins=[
            ContextDigestPlugin(config={"max_context_refs": 10}),
            BudgetOptimizerPlugin(),
        ],
        governance=IRGovernanceChecker(),
    )

    # Custom conductor that produces 5 phases matching our agent sequence
    def custom_conductor(task, ctx):
        return [
            Phase(name="Planning", agents=["architect"],
                  brief="Define scope and structure for: " + task),
            Phase(name="Research", agents=["researcher"],
                  brief="Gather findings for: " + task),
            Phase(name="Implementation", agents=["implementer"],
                  brief="Draft structured output for: " + task),
            Phase(name="Review", agents=["reviewer"],
                  brief="Critique and identify gaps in: " + task),
            Phase(name="Synthesis", agents=["integrator"],
                  brief="Synthesize final deliverable for: " + task),
        ]

    def agent_executor(agent_name, brief, ctx):
        if registry.has_agent(agent_name):
            return registry.get_agent(agent_name).execute(brief, ctx)
        return {"agent_name": agent_name, "role": "unknown",
                "output": "Unavailable", "confidence": 0.0,
                "risk_flags": ["CRITICAL_missing"], "reasoning": "Not found"}

    orchestrator = Orchestrator(
        config={"max_phases": 5, "confidence_threshold": 0.80},
        agent_executor=agent_executor,
        conductor_executor=custom_conductor,
        governance_checker=lambda a, d, c: governance.evaluate_action(a, d, c),
        prompt_compiler=compiler,
        schema_validator=validator,
        agent_provider_resolver=lambda n: "mock",
        ir_pipeline=pipeline,
    )

    ledger = orchestrator.run(
        "Survey of LLM orchestration patterns: chain-of-thought, ReAct, "
        "multi-agent debate, and constitutional AI governance",
        RESEARCH_CONTEXT,
    )
    return ledger, pipeline, compiler, validator


def main():
    print("=" * 70)
    print("  SYMPHONY-IR WORKFLOW: Research and Synthesis Pipeline")
    print("=" * 70)
    print()

    # --- Phase 1: Show the research pipeline structure ---
    print("[1/5] Building 5-agent research pipeline...")
    pipeline = PromptIRPipeline(
        plugins=[
            ContextDigestPlugin(config={"max_context_refs": 10}),
            BudgetOptimizerPlugin(),
        ],
        governance=IRGovernanceChecker(),
    )
    phases = build_research_phases()
    for label, ir in phases:
        print(f"  {label:<25s} -> {ir.role} (priority={ir.priority}, budget={ir.token_budget})")
    print()

    # --- Phase 2: Priority-based budget allocation ---
    print("[2/5] Demonstrating priority-based budget allocation...")
    demonstrate_priority_budgets(phases, pipeline)

    # --- Phase 3: Full orchestrated run ---
    print("[3/5] Running full 5-agent orchestrated pipeline...")
    ledger, run_pipeline, compiler, validator = run_orchestrated_pipeline()
    print(f"  Run ID:          {ledger.run_id}")
    print(f"  Final state:     {ledger.state}")
    print(f"  Phases:          {len(ledger.phases)}")
    print(f"  Agent responses: {len(ledger.agent_responses)}")
    print(f"  Decisions:       {len(ledger.decisions)}")
    print(f"  Avg confidence:  {ledger.confidence:.2f}")
    print()

    # Agent sequence
    print("  Agent Execution Sequence:")
    for i, r in enumerate(ledger.agent_responses, 1):
        mode = "IR+compiled" if r.metadata.get("compiled") else "raw"
        flags = ", ".join(r.risk_flags) if r.risk_flags else "none"
        print(f"    {i}. {r.agent_name:12s} conf={r.confidence:.2f} flags={flags} [{mode}]")
    print()

    # --- Phase 4: A/B efficiency comparison ---
    print("[4/5] Generating A/B efficiency comparison...")
    calculator, compiled_runs, raw_runs = generate_ab_comparison()

    # --- Phase 5: Final summary ---
    print("[5/5] Final Summary Report")
    print("=" * 70)
    print()

    # Orchestration stats
    print("  Orchestration:")
    print(f"    Agents used:        {len(ledger.agent_responses)}")
    print(f"    Phases completed:   {len(ledger.phases)}")
    print(f"    Average confidence: {ledger.confidence:.2f}")
    print()

    # Compiler stats
    cs = compiler.get_compilation_stats()
    print("  Prompt Compiler:")
    print(f"    Compilations:       {cs['total_compilations']}")
    print(f"    Avg tokens/prompt:  {cs['average_tokens_per_prompt']}")
    print(f"    Compression rate:   {cs['compression_rate']:.1%}")
    print()

    # Validator stats
    vs = validator.get_validation_stats()
    print("  Schema Validator:")
    print(f"    Validations:        {vs['total_validations']}")
    print(f"    Success rate:       {vs['success_rate']:.0%}")
    print(f"    Repair rate:        {vs['repair_rate']:.0%}")
    print()

    # Pipeline stats
    ps = run_pipeline.get_pipeline_stats()
    print("  IR Pipeline:")
    print(f"    Pipeline runs:      {ps['total_runs']}")
    print(f"    Transformations:    {ps['total_transformations']}")
    print()

    # A/B efficiency headline
    comparison = calculator.compare(compiled_runs, raw_runs)
    print("  Efficiency Headline:")
    print(f"    Token reduction:    {comparison.token_reduction_pct:.1f}%")
    print(f"    Cost reduction:     {comparison.cost_reduction_pct:.1f}%")
    print(f"    Latency reduction:  {comparison.latency_reduction_pct:.1f}%")
    print(f"    Efficiency score:   {comparison.efficiency_score:.3f}")
    print(f"    Confidence level:   {comparison.statistical_significance.replace('_', ' ')}")
    print()

    # Decision chain
    print("  Decision Chain (all):")
    for i, d in enumerate(ledger.decisions, 1):
        print(f"    {i:2d}. [{d.state:15s}] {d.action}")
    print()
    print("Workflow complete.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
