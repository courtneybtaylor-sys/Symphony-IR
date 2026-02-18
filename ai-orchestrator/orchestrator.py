#!/usr/bin/env python3
"""Symphony-IR CLI — Compiler-grade runtime for multi-model AI orchestration.

Commands:
    init       - Initialize .symphony/ directory with config templates
    run        - Execute an orchestration run
    status     - Show context provider availability
    history    - Show recent orchestration runs
    efficiency - Generate A/B efficiency report from run ledgers
"""

import argparse
import json
import logging
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

# Add the package root to sys.path for imports
PACKAGE_DIR = Path(__file__).resolve().parent
if str(PACKAGE_DIR) not in sys.path:
    sys.path.insert(0, str(PACKAGE_DIR))

from core.orchestrator import Orchestrator, AgentResponse, OrchestratorState
from core.governance import MaaTGovernanceEngine
from core.prompt_compiler import PromptCompiler
from core.schema_validator import SchemaValidator
from core.prompt_ir import (
    IR_SCHEMA_VERSION,
    PromptIRPipeline,
    ContextDigestPlugin,
    BudgetOptimizerPlugin,
    IRGovernanceChecker,
)
from core.efficiency_stats import EfficiencyCalculator, RunLedgerParser
from models.client import ModelFactory, MockModelClient
from agents.agent import Agent, AgentConfig, AgentRegistry
from context.providers import (
    ContextManager,
    FileSystemContext,
    GitContext,
    ActiveFileContext,
)

logger = logging.getLogger("symphony")

# Default agents.yaml template
AGENTS_YAML_TEMPLATE = """\
# Symphony-IR Agent Configuration
# Environment variables use ${VAR_NAME} syntax

agents:
  - name: architect
    role: System Architect
    model_provider: anthropic
    model_config:
      api_key: ${ANTHROPIC_API_KEY}
      model: claude-sonnet-4-20250514
    temperature: 0.7
    max_tokens: 2000
    system_prompt: |
      You are the System Architect agent.

      Your role is to:
      - Design high-level system architecture
      - Identify constraints and dependencies
      - Spot architectural risks
      - Ensure scalability and maintainability

      Always consider the bigger picture.
    constraints:
      focus: "Architecture and design, not implementation"
      output_format: "Structured diagrams or component descriptions"

  - name: researcher
    role: Researcher
    model_provider: anthropic
    model_config:
      api_key: ${ANTHROPIC_API_KEY}
      model: claude-sonnet-4-20250514
    temperature: 0.5
    max_tokens: 2000
    system_prompt: |
      You are the Researcher agent.

      Your role is to:
      - Find relevant documentation and prior art
      - Research best practices and patterns
      - Identify potential dependencies and libraries
      - Summarize findings concisely

      Be thorough but focused.
    constraints:
      focus: "Research and documentation, not implementation"
      output_format: "Structured findings with references"

  - name: implementer
    role: Implementer
    model_provider: anthropic
    model_config:
      api_key: ${ANTHROPIC_API_KEY}
      model: claude-sonnet-4-20250514
    temperature: 0.3
    max_tokens: 4000
    system_prompt: |
      You are the Implementer agent.

      Your role is to:
      - Write concrete code and implementation details
      - Follow architectural guidelines from the Architect
      - Apply best practices from the Researcher
      - Create working, tested solutions

      Write clean, maintainable code.
    constraints:
      focus: "Concrete implementation"
      output_format: "Code with inline documentation"

  - name: reviewer
    role: Reviewer
    model_provider: anthropic
    model_config:
      api_key: ${ANTHROPIC_API_KEY}
      model: claude-sonnet-4-20250514
    temperature: 0.4
    max_tokens: 2000
    system_prompt: |
      You are the Reviewer agent.

      Your role is to:
      - Critique code and designs for issues
      - Identify edge cases and failure modes
      - Check for security vulnerabilities
      - Suggest concrete improvements

      Be constructive but thorough.
    constraints:
      focus: "Quality and correctness"
      output_format: "Issue list with severity and suggestions"

  - name: integrator
    role: Integrator
    model_provider: anthropic
    model_config:
      api_key: ${ANTHROPIC_API_KEY}
      model: claude-sonnet-4-20250514
    temperature: 0.5
    max_tokens: 3000
    system_prompt: |
      You are the Integrator agent.

      Your role is to:
      - Synthesize outputs from all other agents
      - Ensure consistency across components
      - Validate API contracts and interfaces
      - Create the final integrated solution

      Focus on coherence and completeness.
    constraints:
      focus: "Integration and synthesis"
      output_format: "Integrated output with component map"

conductor:
  model_provider: anthropic
  model_config:
    api_key: ${ANTHROPIC_API_KEY}
    model: claude-sonnet-4-20250514
  system_prompt: |
    You are the Conductor - the orchestration planner.

    Create structured plans in this format:

    PHASES:
    1. Phase name: Description
       Agents: [list]
       Termination: Success criteria

    Be decisive. Create clear, actionable plans.

system:
  max_phases: 10
  confidence_threshold: 0.85
  enable_parallel_execution: true
  log_level: INFO
"""

ENV_TEMPLATE = """\
# Symphony-IR Environment Configuration
# Copy this to .env and fill in your API keys

# Anthropic (Claude)
ANTHROPIC_API_KEY=

# OpenAI (GPT)
OPENAI_API_KEY=

# Ollama (local models - no key needed)
# OLLAMA_BASE_URL=http://localhost:11434
"""


def cmd_init(args):
    """Initialize .symphony/ directory."""
    project_root = Path(args.project).resolve()
    orch_dir = project_root / ".symphony"

    if orch_dir.exists() and not args.force:
        print(f"Directory {orch_dir} already exists. Use --force to overwrite.")
        return 1

    # Create directory structure
    (orch_dir / "runs").mkdir(parents=True, exist_ok=True)
    (orch_dir / "logs").mkdir(parents=True, exist_ok=True)

    # Write agents.yaml
    agents_path = orch_dir / "agents.yaml"
    agents_path.write_text(AGENTS_YAML_TEMPLATE)
    print(f"  Created {agents_path}")

    # Write .env.template
    env_path = orch_dir / ".env.template"
    env_path.write_text(ENV_TEMPLATE)
    print(f"  Created {env_path}")

    # Write .env if it doesn't exist
    env_file = orch_dir / ".env"
    if not env_file.exists():
        env_file.write_text(ENV_TEMPLATE)
        print(f"  Created {env_file}")

    print(f"\nSymphony-IR initialized at {orch_dir}")
    print(f"\nIR Schema Version: {IR_SCHEMA_VERSION}")
    print("\nNext steps:")
    print(f"  1. Edit {env_file} with your API keys")
    print(f"  2. Customize {agents_path} as needed")
    print('  3. Run: symphony run "your task here"')
    return 0


def cmd_run(args):
    """Execute an orchestration run."""
    project_root = Path(args.project).resolve()

    # Support both .symphony and legacy .orchestrator directories
    orch_dir = project_root / ".symphony"
    if not orch_dir.exists():
        legacy_dir = project_root / ".orchestrator"
        if legacy_dir.exists():
            orch_dir = legacy_dir

    task = args.task

    if not task:
        print("Error: No task specified. Usage: symphony run <task>")
        return 1

    # Set up logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    )

    # Load environment
    env_file = orch_dir / ".env"
    if env_file.exists():
        _load_env_file(str(env_file))

    # Set up context providers
    context_manager = ContextManager()
    context_manager.add_provider(FileSystemContext(str(project_root)))
    context_manager.add_provider(GitContext(str(project_root)))
    if args.file:
        context_manager.add_provider(ActiveFileContext(args.file))

    print("Collecting context...")
    context = context_manager.collect_all()

    # Load agent registry
    agents_yaml = orch_dir / "agents.yaml"
    registry = AgentRegistry()
    use_mock = False

    if agents_yaml.exists():
        try:
            registry.load_from_yaml(str(agents_yaml))
        except Exception as e:
            print(f"Warning: Could not load agents config: {e}")
            print("Falling back to mock agents.")
            use_mock = True
    else:
        print("No agents.yaml found. Run 'symphony init' first, or using mock agents.")
        use_mock = True

    if use_mock:
        _setup_mock_agents(registry)

    # Set up governance
    governance = MaaTGovernanceEngine()

    # Load system config
    system_config = {"max_phases": 10, "confidence_threshold": 0.85}
    if agents_yaml.exists():
        import yaml

        with open(agents_yaml) as f:
            raw = yaml.safe_load(f)
        if raw and "system" in raw:
            system_config.update(raw["system"])

    # Set up prompt compiler
    compiler = None
    validator = None
    ir_pipeline = None
    if not args.no_compile:
        templates_path = orch_dir if (orch_dir / "prompt_templates.yaml").exists() else PACKAGE_DIR / "config"
        try:
            compiler_config = system_config.get("prompt_compiler", {})
            compiler = PromptCompiler(
                templates_path=str(templates_path),
                config=compiler_config if compiler_config else None,
            )
            print(f"  Prompt compiler: {len(compiler.list_templates())} templates loaded")
        except Exception as e:
            logger.warning(f"Could not initialize prompt compiler: {e}")

        validator = SchemaValidator(config=system_config.get("schema_validator"))
        print(f"  Schema validator: enabled (auto_repair={validator.config.get('auto_repair', True)})")

        # Set up IR pipeline (unless --no-ir flag)
        if not args.no_ir and compiler:
            ir_governance = IRGovernanceChecker()
            ir_plugins = [
                ContextDigestPlugin(config={"max_context_refs": 10}),
                BudgetOptimizerPlugin(),
            ]
            ir_pipeline = PromptIRPipeline(
                plugins=ir_plugins,
                governance=ir_governance,
            )
            print(f"  IR pipeline: enabled ({len(ir_plugins)} plugins, governance active)")
            print(f"  IR schema: v{IR_SCHEMA_VERSION}")

    # Create agent executor
    def agent_executor(agent_name, phase_brief, ctx):
        if registry.has_agent(agent_name):
            agent = registry.get_agent(agent_name)
            return agent.execute(phase_brief, ctx)
        else:
            return {
                "agent_name": agent_name,
                "role": "unknown",
                "output": f"Agent '{agent_name}' not found",
                "confidence": 0.0,
                "risk_flags": ["CRITICAL_missing_agent"],
                "reasoning": "Agent not registered",
            }

    # Agent provider resolver for prompt compiler
    def agent_provider_resolver(agent_name):
        if registry.has_agent(agent_name):
            return registry.get_agent(agent_name).config.model_provider
        return "mock"

    # Create orchestrator
    orchestrator = Orchestrator(
        config=system_config,
        agent_executor=agent_executor,
        governance_checker=lambda at, ad, ctx: governance.evaluate_action(at, ad, ctx),
        prompt_compiler=compiler,
        schema_validator=validator,
        agent_provider_resolver=agent_provider_resolver,
        ir_pipeline=ir_pipeline,
    )

    if args.dry_run:
        print("\n--- DRY RUN ---")
        print(f"Task: {task}")
        print(f"Agents: {registry.list_agents()}")
        print(f"Context providers: {context_manager.get_summary()}")
        print(f"Prompt compiler: {'enabled (' + str(len(compiler.list_templates())) + ' templates)' if compiler else 'disabled'}")
        print(f"Schema validator: {'enabled' if validator else 'disabled'}")
        print(f"IR pipeline: {'enabled (v' + IR_SCHEMA_VERSION + ')' if ir_pipeline else 'disabled'}")
        print(f"Config: {system_config}")
        print("--- END DRY RUN ---")
        return 0

    # Execute
    print(f"\nSymphony-IR: Running orchestration for: {task}")
    print("-" * 60)

    ledger = orchestrator.run(task, context)

    # Save ledger
    runs_dir = orch_dir / "runs"
    runs_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    ledger_path = runs_dir / f"run_{timestamp}_{ledger.run_id}.json"
    orchestrator.save_ledger(str(ledger_path))

    # Display summary
    print(f"\n{'=' * 60}")
    print(f"Run ID:      {ledger.run_id}")
    print(f"State:       {ledger.state}")
    print(f"Phases:      {len(ledger.phases)}")
    print(f"Agents used: {len(set(r.agent_name for r in ledger.agent_responses))}")
    print(f"Decisions:   {len(ledger.decisions)}")
    print(f"Confidence:  {ledger.confidence:.2f}")
    print(f"Ledger:      {ledger_path}")
    print(f"{'=' * 60}")

    if args.verbose:
        print("\nDecision Chain:")
        for d in ledger.decisions:
            print(f"  [{d.state}] {d.action}: {d.reason}")

        if compiler:
            stats = compiler.get_compilation_stats()
            print(f"\nPrompt Compiler Stats:")
            print(f"  Compilations:   {stats.get('total_compilations', 0)}")
            print(f"  Avg tokens:     {stats.get('average_tokens_per_prompt', 0)}")
            print(f"  Compression:    {stats.get('compression_rate', 0):.1%}")

        if validator:
            stats = validator.get_validation_stats()
            print(f"\nSchema Validator Stats:")
            print(f"  Validations:    {stats.get('total_validations', 0)}")
            print(f"  Success rate:   {stats.get('success_rate', 0):.1%}")
            print(f"  Repair rate:    {stats.get('repair_rate', 0):.1%}")

        if ir_pipeline:
            stats = ir_pipeline.get_pipeline_stats()
            print(f"\nIR Pipeline Stats (v{IR_SCHEMA_VERSION}):")
            print(f"  Pipeline runs:      {stats.get('total_runs', 0)}")
            print(f"  Transformations:    {stats.get('total_transformations', 0)}")
            print(f"  Avg transforms/run: {stats.get('avg_transformations_per_run', 0):.1f}")

            if ir_pipeline.governance:
                gov_report = ir_pipeline.governance.get_violations_report()
                print(f"\nIR Governance:")
                print(f"  Checks:       {gov_report.get('total_checks', 0)}")
                print(f"  Approved:     {gov_report.get('approved', 0)}")
                print(f"  Denied:       {gov_report.get('denied', 0)}")
                print(f"  Approval rate:{gov_report.get('approval_rate', 0):.1%}")

    # Export compiler/validator logs
    logs_dir = orch_dir / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    if compiler:
        compiler.export_log(str(logs_dir / f"compilation_{timestamp}_{ledger.run_id}.json"))
    if validator:
        validator.export_log(str(logs_dir / f"validation_{timestamp}_{ledger.run_id}.json"))

    return 0


def cmd_status(args):
    """Show context provider availability."""
    project_root = Path(args.project).resolve()

    context_manager = ContextManager()
    context_manager.add_provider(FileSystemContext(str(project_root)))
    context_manager.add_provider(GitContext(str(project_root)))

    print(f"Symphony-IR Status (IR Schema v{IR_SCHEMA_VERSION})")
    print("-" * 40)
    print(context_manager.get_summary())

    # Check symphony directory (support legacy .orchestrator too)
    orch_dir = project_root / ".symphony"
    legacy_dir = project_root / ".orchestrator"
    active_dir = orch_dir if orch_dir.exists() else (legacy_dir if legacy_dir.exists() else None)

    if active_dir:
        print(f"\nSymphony directory: {active_dir}")
        agents_yaml = active_dir / "agents.yaml"
        env_file = active_dir / ".env"
        print(f"  agents.yaml: {'found' if agents_yaml.exists() else 'missing'}")
        print(f"  .env:        {'found' if env_file.exists() else 'missing'}")

        runs_dir = active_dir / "runs"
        if runs_dir.exists():
            runs = list(runs_dir.glob("*.json"))
            print(f"  runs:        {len(runs)} saved")
    else:
        print(f"\nSymphony directory: not initialized")
        print("  Run 'symphony init' to get started.")

    return 0


def cmd_history(args):
    """Show recent orchestration runs."""
    project_root = Path(args.project).resolve()

    # Support both .symphony and legacy .orchestrator
    runs_dir = project_root / ".symphony" / "runs"
    if not runs_dir.exists():
        runs_dir = project_root / ".orchestrator" / "runs"

    if not runs_dir.exists():
        print("No runs found. Run 'symphony init' and then 'symphony run <task>' first.")
        return 1

    runs = sorted(runs_dir.glob("*.json"), reverse=True)
    limit = args.limit

    if not runs:
        print("No runs found.")
        return 0

    print(f"Symphony-IR Run History (showing {min(limit, len(runs))} of {len(runs)}):")
    print("-" * 80)

    for run_file in runs[:limit]:
        try:
            data = json.loads(run_file.read_text())
            run_id = data.get("run_id", "unknown")
            task = data.get("task", "")[:50]
            state = data.get("state", "unknown")
            confidence = data.get("confidence", 0.0)
            timestamp = data.get("timestamp", "")
            phases = len(data.get("phases", []))
            responses = len(data.get("agent_responses", []))

            print(f"  {run_id} | {state:10s} | conf={confidence:.2f} | "
                  f"phases={phases} agents={responses} | {task}")

            if args.detailed:
                for d in data.get("decisions", []):
                    print(f"    [{d['state']}] {d['action']}: {d['reason']}")
                print()
        except (json.JSONDecodeError, KeyError) as e:
            print(f"  Error reading {run_file.name}: {e}")

    return 0


def cmd_efficiency(args):
    """Generate A/B efficiency report from run ledgers."""
    project_root = Path(args.project).resolve()

    # Support both .symphony and legacy .orchestrator
    runs_dir = project_root / ".symphony" / "runs"
    if not runs_dir.exists():
        runs_dir = project_root / ".orchestrator" / "runs"

    if not runs_dir.exists():
        print("No runs found. Run some orchestrations first.")
        return 1

    run_files = sorted(runs_dir.glob("*.json"))
    if not run_files:
        print("No run ledgers found.")
        return 1

    print(f"Symphony-IR Efficiency Report (IR Schema v{IR_SCHEMA_VERSION})")
    print(f"Parsing {len(run_files)} run ledgers...")

    compiled_runs, raw_runs = RunLedgerParser.parse_multiple_ledgers(
        [str(f) for f in run_files]
    )

    if not compiled_runs and not raw_runs:
        print("No valid runs found in ledgers.")
        return 1

    calculator = EfficiencyCalculator()
    report_format = "json" if args.json else "text"

    # If we only have compiled or only raw runs, show stats for what we have
    if not raw_runs:
        print("Note: No raw (uncompiled) runs found. Showing compiled stats only.")
        stats = calculator.summarize_runs(compiled_runs)
        print(f"\nCompiled Runs: {stats.run_count}")
        print(f"  Avg Tokens:   {stats.avg_total_tokens:,.0f}")
        print(f"  Avg Duration: {stats.avg_duration_seconds:.2f}s")
        print(f"  Avg Retries:  {stats.avg_retries:.2f}")
        print(f"  Avg Cost:     ${stats.avg_cost_usd:.4f}")
        return 0

    if not compiled_runs:
        print("Note: No compiled runs found. Showing raw stats only.")
        stats = calculator.summarize_runs(raw_runs)
        print(f"\nRaw Runs: {stats.run_count}")
        print(f"  Avg Tokens:   {stats.avg_total_tokens:,.0f}")
        print(f"  Avg Duration: {stats.avg_duration_seconds:.2f}s")
        print(f"  Avg Retries:  {stats.avg_retries:.2f}")
        print(f"  Avg Cost:     ${stats.avg_cost_usd:.4f}")
        return 0

    report = calculator.generate_roi_report(compiled_runs, raw_runs, format=report_format)
    print(report)

    # Export if requested
    if args.export:
        comparison = calculator.compare(compiled_runs, raw_runs)
        calculator.export_comparison(comparison, args.export)
        print(f"\nReport exported to: {args.export}")

    return 0


def _load_env_file(path: str):
    """Load environment variables from a .env file."""
    try:
        with open(path) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    key, _, value = line.partition("=")
                    key = key.strip()
                    value = value.strip().strip("'\"")
                    if key and value:
                        os.environ.setdefault(key, value)
    except Exception as e:
        logger.warning(f"Could not load .env file: {e}")


def _setup_mock_agents(registry: AgentRegistry):
    """Set up mock agents for testing without API keys."""
    mock_client = MockModelClient()

    mock_agents = [
        ("architect", "System Architect", "You are the System Architect agent."),
        ("researcher", "Researcher", "You are the Researcher agent."),
        ("implementer", "Implementer", "You are the Implementer agent."),
        ("reviewer", "Reviewer", "You are the Reviewer agent."),
        ("integrator", "Integrator", "You are the Integrator agent."),
    ]

    for name, role, prompt in mock_agents:
        config = AgentConfig(
            name=name,
            role=role,
            system_prompt=prompt,
            model_provider="mock",
        )
        agent = Agent(config=config, client=mock_client)
        registry.register_agent(agent)


def main():
    parser = argparse.ArgumentParser(
        description="Symphony-IR — Compiler-grade runtime for multi-model AI orchestration",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # init
    init_parser = subparsers.add_parser("init", help="Initialize .symphony/ directory")
    init_parser.add_argument(
        "--project", default=".", help="Project root directory (default: current dir)"
    )
    init_parser.add_argument(
        "--force", action="store_true", help="Overwrite existing config"
    )

    # run
    run_parser = subparsers.add_parser("run", help="Execute an orchestration run")
    run_parser.add_argument("task", nargs="?", help="Task description to orchestrate")
    run_parser.add_argument(
        "--project", default=".", help="Project root directory (default: current dir)"
    )
    run_parser.add_argument("--file", help="Active file to include in context")
    run_parser.add_argument(
        "--dry-run", action="store_true", help="Show plan without executing"
    )
    run_parser.add_argument(
        "-v", "--verbose", action="store_true", help="Detailed output"
    )
    run_parser.add_argument(
        "--no-compile", action="store_true",
        help="Disable prompt compiler and schema validator",
    )
    run_parser.add_argument(
        "--no-ir", action="store_true",
        help="Disable IR pipeline (use direct compilation instead)",
    )

    # status
    status_parser = subparsers.add_parser(
        "status", help="Show context provider availability"
    )
    status_parser.add_argument(
        "--project", default=".", help="Project root directory (default: current dir)"
    )

    # history
    history_parser = subparsers.add_parser("history", help="Show recent runs")
    history_parser.add_argument(
        "--project", default=".", help="Project root directory (default: current dir)"
    )
    history_parser.add_argument(
        "--limit", type=int, default=10, help="Number of runs to show (default: 10)"
    )
    history_parser.add_argument(
        "--detailed", action="store_true", help="Show full decision chains"
    )

    # efficiency
    eff_parser = subparsers.add_parser(
        "efficiency", help="Generate A/B efficiency report from run ledgers"
    )
    eff_parser.add_argument(
        "--project", default=".", help="Project root directory (default: current dir)"
    )
    eff_parser.add_argument(
        "--json", action="store_true", help="Output in JSON format"
    )
    eff_parser.add_argument(
        "--export", type=str, help="Export report to file"
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    commands = {
        "init": cmd_init,
        "run": cmd_run,
        "status": cmd_status,
        "history": cmd_history,
        "efficiency": cmd_efficiency,
    }

    return commands[args.command](args)


if __name__ == "__main__":
    sys.exit(main() or 0)
