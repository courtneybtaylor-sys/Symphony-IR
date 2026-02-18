#!/usr/bin/env python3
"""Symphony-IR Workflow Example: Multi-File Codebase Analysis.

Demonstrates large-context handling and security-focused analysis:
  - 15+ file context that triggers ContextDigestPlugin compression
  - Governance blocking analysis of protected system paths (/etc/passwd)
  - Researcher + Reviewer agents running a security audit
  - Budget optimization for the research phase (1.3x multiplier)

Key features demonstrated:
  - ContextDigestPlugin compressing 15+ refs into a digest
  - IRGovernanceChecker denying forbidden path references
  - BudgetOptimizerPlugin phase-based multiplier
  - Full orchestrator run with compiled prompts
  - Governance violations report

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
# Mock context: a large Python project with 15+ files
# ---------------------------------------------------------------------------
def build_large_context():
    """Create a mock project context with 15+ files."""
    key_files = {}
    modules = [
        "auth/login.py", "auth/tokens.py", "auth/permissions.py",
        "api/routes.py", "api/middleware.py", "api/validators.py",
        "db/models.py", "db/migrations.py", "db/connection.py",
        "services/email.py", "services/payment.py", "services/logging.py",
        "utils/crypto.py", "utils/config.py", "utils/helpers.py",
        "tests/test_auth.py", "tests/test_api.py",
    ]
    for mod in modules:
        key_files[mod] = (
            f"# Module: {mod}\n"
            f"# Lines: ~150\n"
            f"class {mod.split('/')[-1].replace('.py','').title()}Handler:\n"
            f"    def process(self): ...\n"
        )
    return {
        "filesystem": {
            "root": "/projects/enterprise-app",
            "key_files": key_files,
        },
        "git": {
            "branch": "security/audit-2024",
            "status": "clean",
        },
    }


def build_agents():
    """Register researcher and reviewer agents."""
    registry = AgentRegistry()
    client = MockModelClient()
    for name, role in [("researcher", "Security Researcher"),
                        ("reviewer", "Security Reviewer"),
                        ("architect", "System Architect")]:
        cfg = AgentConfig(
            name=name, role=role,
            system_prompt=f"You are the {role} agent.",
            model_provider="mock",
        )
        registry.register_agent(Agent(config=cfg, client=client))
    return registry


def demo_context_digest():
    """Show ContextDigestPlugin compressing 15+ refs."""
    print("--- Context Digest Demo ---")
    file_refs = [f"file:src/module_{i}.py" for i in range(17)]
    ir = (
        PromptIRBuilder("researcher", "Analyze codebase for vulnerabilities")
        .phase(PhaseType.RESEARCH)
        .add_context_refs(file_refs)
        .set_token_budget(4000)
        .set_priority(7)
        .build()
    )
    print(f"  Context refs BEFORE digest: {len(ir.context_refs)}")

    digest_plugin = ContextDigestPlugin(config={"max_context_refs": 10})
    digested = digest_plugin.transform(ir)

    print(f"  Context refs AFTER digest:  {len(digested.context_refs)} (compressed to digest marker)")
    print(f"  Original refs preserved in metadata: {len(digested.metadata.get('original_context_refs', []))}")
    print(f"  Digest text: {digested.metadata.get('context_digest', '')[:80]}...")
    print()
    return digest_plugin


def demo_governance_block():
    """Show governance blocking analysis of protected paths."""
    print("--- Governance Blocking Demo ---")
    governance = IRGovernanceChecker()

    # Safe IR
    safe_ir = (
        PromptIRBuilder("researcher", "Analyze auth module for SQL injection")
        .phase(PhaseType.RESEARCH)
        .add_context_ref("file:auth/login.py")
        .add_context_ref("file:db/models.py")
        .set_token_budget(3000)
        .build()
    )
    approved, violations = governance.check(safe_ir)
    print(f"  Safe analysis request -> Approved: {approved}, Violations: {violations or 'none'}")

    # Dangerous IR referencing /etc/passwd
    dangerous_ir = (
        PromptIRBuilder("researcher", "Analyze system password configuration")
        .phase(PhaseType.RESEARCH)
        .add_context_ref("file:/etc/passwd")
        .add_context_ref("file:/etc/shadow")
        .add_context_ref("file:auth/login.py")
        .set_token_budget(3000)
        .build()
    )
    approved, violations = governance.check(dangerous_ir)
    print(f"  Protected path request -> Approved: {approved}")
    for v in violations:
        print(f"    VIOLATION: {v}")

    # Destructive intent
    destruct_ir = (
        PromptIRBuilder("researcher", "delete all logs and drop database tables")
        .phase(PhaseType.RESEARCH)
        .add_context_ref("file:db/connection.py")
        .set_token_budget(2000)
        .build()
    )
    approved, violations = governance.check(destruct_ir)
    print(f"  Destructive intent -> Approved: {approved}")
    for v in violations:
        print(f"    VIOLATION: {v}")

    report = governance.get_violations_report()
    print(f"\n  Governance summary: {report['total_checks']} checks, "
          f"{report['approved']} approved, {report['denied']} denied")
    print()
    return governance


def demo_budget_optimization():
    """Show how BudgetOptimizerPlugin adjusts budgets by phase."""
    print("--- Budget Optimization Demo ---")
    optimizer = BudgetOptimizerPlugin()
    base_budget = 3000

    test_cases = [
        ("Planning", PhaseType.PLANNING, 5),
        ("Research", PhaseType.RESEARCH, 7),
        ("Implementation", PhaseType.IMPLEMENTATION, 5),
        ("Review", PhaseType.REVIEW, 5),
        ("Research (high priority)", PhaseType.RESEARCH, 9),
    ]

    for label, phase, priority in test_cases:
        ir = (
            PromptIRBuilder("researcher", f"Task for {label}")
            .phase(phase)
            .set_token_budget(base_budget)
            .set_priority(priority)
            .build()
        )
        optimized = optimizer.transform(ir)
        multiplier = optimized.metadata.get("budget_multiplier", 1.0)
        print(f"  {label:30s} | base={base_budget} | multiplier={multiplier:.1f} "
              f"| priority={priority} | result={optimized.token_budget}")
    print()


def run_full_analysis():
    """Run the full orchestrated security analysis workflow."""
    print("--- Full Orchestrated Security Analysis ---")

    context = build_large_context()
    registry = build_agents()
    config_path = Path(__file__).resolve().parent.parent / "config"

    # Components
    compiler = PromptCompiler(templates_path=str(config_path))
    validator = SchemaValidator(config={"auto_repair": True})
    governance = MaaTGovernanceEngine(user_trust_score=0.85)

    pipeline = PromptIRPipeline(
        plugins=[
            ContextDigestPlugin(config={"max_context_refs": 10}),
            BudgetOptimizerPlugin(),
        ],
        governance=IRGovernanceChecker(),
    )

    def agent_executor(agent_name, brief, ctx):
        if registry.has_agent(agent_name):
            return registry.get_agent(agent_name).execute(brief, ctx)
        return {"agent_name": agent_name, "role": "unknown",
                "output": "Unavailable", "confidence": 0.0,
                "risk_flags": ["CRITICAL_missing_agent"], "reasoning": "Not found"}

    orchestrator = Orchestrator(
        config={"max_phases": 3, "confidence_threshold": 0.80},
        agent_executor=agent_executor,
        governance_checker=lambda a, d, c: governance.evaluate_action(a, d, c),
        prompt_compiler=compiler,
        schema_validator=validator,
        agent_provider_resolver=lambda n: "mock",
        ir_pipeline=pipeline,
    )

    ledger = orchestrator.run(
        "Perform security audit: identify SQL injection, XSS, CSRF, "
        "insecure crypto, and hardcoded credentials across the codebase",
        context,
    )

    print(f"  Run ID:          {ledger.run_id}")
    print(f"  Final state:     {ledger.state}")
    print(f"  Phases:          {len(ledger.phases)}")
    print(f"  Agent responses: {len(ledger.agent_responses)}")
    print(f"  Decisions:       {len(ledger.decisions)}")
    print(f"  Avg confidence:  {ledger.confidence:.2f}")
    print()

    # Show agent summary
    print("  Agent Responses:")
    for r in ledger.agent_responses:
        flags = ", ".join(r.risk_flags) if r.risk_flags else "none"
        mode = "IR+compiled" if r.metadata.get("compiled") else "raw"
        print(f"    {r.agent_name:12s} conf={r.confidence:.2f} flags={flags} [{mode}]")
    print()

    # Pipeline stats
    ps = pipeline.get_pipeline_stats()
    print(f"  IR pipeline: {ps['total_runs']} runs, "
          f"{ps['total_transformations']} transformations")

    # Compiler stats
    cs = compiler.get_compilation_stats()
    print(f"  Compiler: {cs['total_compilations']} compilations, "
          f"avg {cs['average_tokens_per_prompt']} tokens/prompt")
    print()

    return ledger


def main():
    print("=" * 70)
    print("  SYMPHONY-IR WORKFLOW: Multi-File Codebase Analysis")
    print("=" * 70)
    print()

    file_count = len(build_large_context()["filesystem"]["key_files"])
    print(f"[1/5] Project context: {file_count} files in enterprise-app")
    print()

    print("[2/5] Context Digest -- compressing large file sets")
    demo_context_digest()

    print("[3/5] Governance -- blocking protected paths")
    demo_governance_block()

    print("[4/5] Budget Optimization -- phase-based multipliers")
    demo_budget_optimization()

    print("[5/5] Full Security Analysis Run")
    ledger = run_full_analysis()

    # --- Final Summary ---
    print("=" * 70)
    print("  FINAL SUMMARY")
    print("=" * 70)
    print(f"  Files in context:         {file_count}")
    print(f"  ContextDigest threshold:  10 (files > 10 get compressed)")
    print(f"  Research budget multiplier: 1.3x")
    print(f"  Governance denials shown:  /etc/passwd, /etc/shadow blocked")
    print(f"  Orchestrator phases:       {len(ledger.phases)}")
    print(f"  Total agent calls:         {len(ledger.agent_responses)}")
    print(f"  Final confidence:          {ledger.confidence:.2f}")
    print()
    print("  Decision chain (last 8):")
    for d in ledger.decisions[-8:]:
        print(f"    [{d.state:15s}] {d.action}")
    print()
    print("Workflow complete.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
