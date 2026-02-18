#!/usr/bin/env python3
"""AI Orchestrator Demo - Runs without API keys using mock models.

This demonstrates the full orchestration architecture:
- State machine execution
- Multi-agent coordination
- Governance checks
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


def main():
    print("=" * 70)
    print("  AI ORCHESTRATOR - Architecture Demo")
    print("  Deterministic Multi-Agent Coordination Engine")
    print("=" * 70)
    print()

    # Step 1: Create mock context
    print("[1/5] Creating mock project context...")
    context = create_mock_context()
    print(f"  - Filesystem context: {context['filesystem']['root']}")
    print(f"  - Git branch: {context['git']['branch']}")
    print()

    # Step 2: Set up agents
    print("[2/5] Initializing agent registry...")
    registry = create_mock_agents()
    print(f"  - Agents: {', '.join(registry.list_agents())}")
    print()

    # Step 3: Set up governance
    print("[3/5] Initializing Ma'aT governance engine...")
    governance = MaaTGovernanceEngine(user_trust_score=0.85)
    print(f"  - Principles: {', '.join(governance.get_principles().keys())}")
    print()

    # Step 4: Run orchestration
    task = "Design and implement a new authentication system with JWT tokens, " \
           "password hashing, and role-based access control"

    print("[4/5] Running orchestration...")
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
    )

    ledger = orchestrator.run(task, context)

    # Step 5: Display results
    print()
    print("[5/5] Results")
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
        print(f"  {r.agent_name:12s} ({r.role:18s}) conf={r.confidence:.2f}  flags={flags}")
    print()

    # Governance audit
    audit_log = governance.get_audit_log()
    if audit_log:
        print("Governance Audit:")
        print("-" * 70)
        for entry in audit_log:
            print(f"  [{entry['decision']:14s}] {entry['action_type']}: {entry['reason'][:60]}")
        print()

    # Architecture demonstration
    print("Architecture Demonstrated:")
    print("-" * 70)
    print("  [x] Deterministic state machine (INIT -> PLAN -> EXECUTE -> SYNTHESIZE -> VALIDATE -> TERMINATE)")
    print("  [x] Model-agnostic abstraction (MockModelClient swappable for OpenAI/Anthropic/Ollama)")
    print("  [x] Conductor + Specialist pattern (5 specialist agents)")
    print("  [x] Structured output parsing (OUTPUT/CONFIDENCE/RISK_FLAGS/REASONING)")
    print("  [x] Ma'aT governance layer (constitutional principle checks)")
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
    print("  1. Run 'python orchestrator.py init' to set up your project")
    print("  2. Add API keys to .orchestrator/.env")
    print("  3. Customize agents in .orchestrator/agents.yaml")
    print('  4. Run: python orchestrator.py run "your task here"')
    print()
    print("  Swap models by changing model_provider in agents.yaml:")
    print("    anthropic -> OpenAI/GPT")
    print("    openai    -> Anthropic/Claude")
    print("    ollama    -> Local models (Llama, Mistral, etc.)")
    print("    mock      -> Testing without API keys")
    print()

    return 0


if __name__ == "__main__":
    sys.exit(main())
