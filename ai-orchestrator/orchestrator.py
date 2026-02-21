#!/usr/bin/env python3
"""AI Orchestrator CLI - Deterministic multi-agent coordination engine.

Commands:
    init    - Initialize .orchestrator/ directory with config templates
    run     - Execute an orchestration run
    status  - Show context provider availability
    history - Show recent orchestration runs
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

from cli_error_handler import translate_and_print, wrap_main
from preflight import run_checks, print_report, passed as preflight_passed, CheckStatus
from core.orchestrator import Orchestrator, AgentResponse, OrchestratorState
from core.governance import MaaTGovernanceEngine
from core.prompt_compiler import PromptCompiler
from core.schema_validator import SchemaValidator
from core.prompt_ir import (
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

logger = logging.getLogger("orchestrator")

# Default agents.yaml template
AGENTS_YAML_TEMPLATE = """\
# AI Orchestrator Agent Configuration
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
# AI Orchestrator Environment Configuration
# Copy this to .env and fill in your API keys

# Anthropic (Claude)
ANTHROPIC_API_KEY=

# OpenAI (GPT)
OPENAI_API_KEY=

# Ollama (local models - no key needed)
# OLLAMA_BASE_URL=http://localhost:11434
"""


def cmd_init(args):
    """Initialize .orchestrator/ directory."""
    project_root = Path(args.project).resolve()
    orch_dir = project_root / ".orchestrator"

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

    print(f"\nInitialized orchestrator at {orch_dir}")
    print("\nNext steps:")
    print(f"  1. Edit {env_file} with your API keys")
    print(f"  2. Customize {agents_path} as needed")
    print(f'  3. Run: python orchestrator.py run "your task here"')
    return 0


def cmd_run(args):
    """Execute an orchestration run."""
    project_root = Path(args.project).resolve()
    orch_dir = project_root / ".orchestrator"
    task = args.task

    if not task:
        print("Error: No task specified. Usage: orchestrator run <task>")
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

    # Pre-flight checks (skip with --skip-preflight for CI/scripts)
    if not getattr(args, "skip_preflight", False):
        provider = os.environ.get("SYMPHONY_PROVIDER", "claude")
        api_key  = os.environ.get("ANTHROPIC_API_KEY", "")
        ollama_url = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
        results = run_checks(
            project_root=project_root,
            provider=provider,
            api_key=api_key,
            ollama_url=ollama_url,
        )
        # Print only failures and warnings (not PASS items) to keep output clean
        fails  = [r for r in results if r.status == CheckStatus.FAIL]
        warns  = [r for r in results if r.status == CheckStatus.WARN]
        if fails:
            print_report(results, verbose=False)
            print("Fix the issues above before running.  Use --skip-preflight to bypass.")
            return 1
        if warns:
            for r in warns:
                print(f"⚠️   {r.name}: {r.message}")
                if r.fix:
                    print(f"    → {r.fix}")

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
            translate_and_print(str(e))
            print("⚠️  Falling back to mock agents (no real API calls will be made).")
            use_mock = True
    else:
        print(
            "\n⚠️  No agents.yaml found.\n"
            "   Run first:  python orchestrator.py init --project .\n"
            "   Using mock agents for now.\n"
        )
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
        print(f"IR pipeline: {'enabled' if ir_pipeline else 'disabled'}")
        print(f"Config: {system_config}")
        print("--- END DRY RUN ---")
        return 0

    # Execute
    print(f"\nRunning orchestration for: {task}")
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
            print(f"\nIR Pipeline Stats:")
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


def cmd_preflight(args):
    """Run pre-flight environment checks."""
    project_root = Path(args.project).resolve()

    # Determine provider from agents.yaml or env
    provider = args.provider or os.environ.get("SYMPHONY_PROVIDER", "claude")

    # Load API key from env / .env file
    env_file = project_root / ".orchestrator" / ".env"
    if env_file.exists():
        _load_env_file(str(env_file))
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")

    ollama_url = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")

    results = run_checks(
        project_root=project_root,
        provider=provider,
        api_key=api_key,
        ollama_url=ollama_url,
    )
    ok = print_report(results, verbose=args.verbose)
    return 0 if ok else 1


def cmd_status(args):
    """Show context provider availability."""
    project_root = Path(args.project).resolve()

    context_manager = ContextManager()
    context_manager.add_provider(FileSystemContext(str(project_root)))
    context_manager.add_provider(GitContext(str(project_root)))

    print(context_manager.get_summary())

    # Check orchestrator directory
    orch_dir = project_root / ".orchestrator"
    print(f"\nOrchestrator directory: {'exists' if orch_dir.exists() else 'not initialized'}")

    if orch_dir.exists():
        agents_yaml = orch_dir / "agents.yaml"
        env_file = orch_dir / ".env"
        print(f"  agents.yaml: {'found' if agents_yaml.exists() else 'missing'}")
        print(f"  .env:        {'found' if env_file.exists() else 'missing'}")

        runs_dir = orch_dir / "runs"
        if runs_dir.exists():
            runs = list(runs_dir.glob("*.json"))
            print(f"  runs:        {len(runs)} saved")

    return 0


def cmd_history(args):
    """Show recent orchestration runs."""
    project_root = Path(args.project).resolve()
    runs_dir = project_root / ".orchestrator" / "runs"

    if not runs_dir.exists():
        print("No runs found. Run 'orchestrator init' and then 'orchestrator run <task>' first.")
        return 1

    runs = sorted(runs_dir.glob("*.json"), reverse=True)
    limit = args.limit

    if not runs:
        print("No runs found.")
        return 0

    print(f"Recent runs (showing {min(limit, len(runs))} of {len(runs)}):")
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
    runs_dir = project_root / ".orchestrator" / "runs"

    if not runs_dir.exists():
        print("No runs found. Run some orchestrations first.")
        return 1

    run_files = sorted(runs_dir.glob("*.json"))
    if not run_files:
        print("No run ledgers found.")
        return 1

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


def _get_available_templates():
    """Get list of available flow templates."""
    templates_dir = Path(PACKAGE_DIR) / "flow" / "templates"
    templates = []
    if templates_dir.exists():
        for template_file in sorted(templates_dir.glob("*.yaml")):
            templates.append(template_file.stem)
    return templates


def cmd_flow_list(args):
    """List available flow templates."""
    templates = _get_available_templates()

    if not templates:
        print("No flow templates found.")
        return 1

    print("📚 Available Symphony Flow Templates:\n")

    import yaml

    for template_name in templates:
        template_path = (
            Path(PACKAGE_DIR) / "flow" / "templates" / f"{template_name}.yaml"
        )
        try:
            with open(template_path) as f:
                data = yaml.safe_load(f)

            name = data.get("name", template_name)
            description = data.get("description", "")
            nodes = data.get("nodes", {})

            print(f"🎯 {name} ({template_name})")
            print(f"   {description}")
            print(f"   Nodes: {len(nodes)}")
            print()
        except Exception as e:
            print(f"⚠️  {template_name}: Error reading template ({str(e)})")
            print()

    return 0


def cmd_flow_status(args):
    """Show status of flow projects."""
    project_root = Path(args.project).resolve()
    orch_dir = project_root / ".orchestrator"
    flows_dir = orch_dir / "flows"

    if not flows_dir.exists():
        print("No flow projects found. Start a flow with: orchestrator flow --template <name>")
        return 0

    projects = sorted(flows_dir.glob("*.json"))

    if not projects:
        print("No flow projects found.")
        return 0

    print(f"🎼 Flow Projects ({len(projects)} total):\n")

    for project_file in projects[:20]:  # Show most recent 20
        try:
            with open(project_file) as f:
                state = json.load(f)

            project_id = state.get("project_id", "unknown")
            template_id = state.get("template_id", "unknown")
            current_node = state.get("current_node_id", "unknown")
            decisions = len(state.get("decisions", []))
            path_length = len(state.get("selected_path", []))

            print(f"📋 {project_id} | {template_id}")
            print(f"   Current: {current_node}")
            print(f"   Progress: {path_length} nodes, {decisions} decisions")
            print()
        except Exception as e:
            print(f"⚠️  Error reading {project_file.name}: {str(e)}")

    return 0


def cmd_flow(args):
    """Execute guided flow workflow with bounded decision tree."""
    from flow.engine import BranchEngine
    from flow.adapter import IRAdapter

    # Parse variables
    variables = {}
    for v in args.var:
        if "=" not in v:
            print(f"❌ Invalid variable format: {v}")
            print("   Use: --var key=value")
            return 1
        key, val = v.split("=", 1)
        variables[key] = val

    # Template path
    template_path = Path(PACKAGE_DIR) / "flow" / "templates" / f"{args.template}.yaml"
    if not template_path.exists():
        available = _get_available_templates()
        print(f"❌ Template not found: {args.template}")
        if available:
            print(f"   Available templates: {', '.join(available)}")
        print(f"\n   View all: orchestrator flow-list")
        return 1

    # Set up logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    )

    # Load environment
    project_root = Path(args.project).resolve()
    orch_dir = project_root / ".orchestrator"
    env_file = orch_dir / ".env"
    if env_file.exists():
        _load_env_file(str(env_file))

    # Load agent registry for execution
    agents_yaml = orch_dir / "agents.yaml"
    registry = AgentRegistry()
    use_mock = False

    if agents_yaml.exists():
        try:
            registry.load_from_yaml(str(agents_yaml))
        except Exception as e:
            logger.warning(f"Could not load agents config: {e}")
            print("⚠️  Falling back to mock agents.")
            use_mock = True
    else:
        print("⚠️  No agents.yaml found. Using mock agents.")
        use_mock = True

    if use_mock:
        _setup_mock_agents(registry)

    # Set up governance and compilation
    governance = MaaTGovernanceEngine()
    compiler = None
    validator = None
    ir_pipeline = None

    if not args.no_compile:
        try:
            compiler = PromptCompiler(
                templates_path=str(PACKAGE_DIR / "config"),
                config={},
            )
        except Exception as e:
            logger.warning(f"Could not initialize prompt compiler: {e}")

        validator = SchemaValidator()

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

    # Agent executor
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
            }

    def agent_provider_resolver(agent_name):
        if registry.has_agent(agent_name):
            return registry.get_agent(agent_name).config.model_provider
        return "mock"

    # Initialize engine
    try:
        engine = BranchEngine(str(template_path))
        engine.state.variables = variables
        adapter = IRAdapter(engine.state)
    except Exception as e:
        print(f"❌ Failed to initialize flow: {str(e)}")
        return 1

    orchestrator = Orchestrator(
        config={"max_phases": 10, "confidence_threshold": 0.85},
        agent_executor=agent_executor,
        governance_checker=lambda at, ad, ctx: governance.evaluate_action(at, ad, ctx),
        prompt_compiler=compiler,
        schema_validator=validator,
        agent_provider_resolver=agent_provider_resolver,
        ir_pipeline=ir_pipeline,
    )

    print("=" * 60)
    print(f"🎼 Symphony Flow: {args.template}")
    print(f"📋 Project ID: {engine.state.project_id}")
    if variables:
        print(f"📌 Variables: {', '.join(f'{k}={v}' for k, v in variables.items())}")
    print("=" * 60)
    print()

    decision_count = 0
    execution_count = 0

    # Main decision loop
    try:
        while True:
            node = engine.get_current_node()

            # Display current step
            print(f"\n✓ Step {len(engine.state.selected_path)}: {node.summary}\n")

            # Terminal node check
            if not node.options:
                print("🎉 Workflow complete!\n")
                break

            # Show options
            print("What's next?")
            for opt in node.options:
                print(f"  {opt.id}) {opt.label}")
                if opt.description:
                    print(f"      {opt.description}")
            print()

            # Get choice
            import click

            choice = click.prompt("Choice", type=str).strip().upper()

            # Validate
            valid_ids = [o.id for o in node.options]
            if choice not in valid_ids:
                print(f"❌ Invalid choice. Choose from: {', '.join(valid_ids)}\n")
                continue

            # Navigate
            try:
                next_node = engine.select_option(choice)
                decision_count += 1
                print(f"→ Selected: {choice}")
            except ValueError as e:
                print(f"❌ Navigation error: {str(e)}\n")
                continue

            # Execute
            print("\n⚙️  Executing via Symphony-IR...\n")

            try:
                result = orchestrator.run(
                    next_node.summary, {"node_id": next_node.id}
                )
                execution_count += 1

                # Display result summary
                print(f"\n✓ Execution complete")
                print(f"  Run ID: {result.run_id}")
                print(f"  Confidence: {result.confidence:.2f}")
                print(f"  Agent responses: {len(result.agent_responses)}")

                # Record execution
                engine.record_execution(next_node.id, result.run_id)

            except Exception as e:
                logger.error(f"Execution failed: {e}", exc_info=True)
                print(f"❌ Execution failed: {str(e)}")
                print("   Continuing to next decision...")
                print()
                continue

            print()

    except KeyboardInterrupt:
        print("\n\n⏸️  Flow interrupted by user")
    except Exception as e:
        logger.error(f"Unexpected error in flow: {e}", exc_info=True)
        print(f"\n❌ Unexpected error: {str(e)}")

    # Save state
    save_path = orch_dir / "flows" / f"{engine.state.project_id}.json"
    try:
        engine.save_state(str(save_path))
        print(f"💾 Session saved: {save_path}")
    except Exception as e:
        print(f"⚠️  Could not save session: {str(e)}")

    # Display summary
    print("\n" + "=" * 60)
    print("📊 Flow Summary")
    print("=" * 60)
    print(f"Project:    {engine.state.project_id}")
    print(f"Template:   {engine.state.template_id}")
    print(f"Nodes:      {len(engine.state.selected_path)}")
    print(f"Decisions:  {decision_count}")
    print(f"Executions: {execution_count}")
    print(f"Current:    {engine.get_current_node().id}")

    if engine.get_current_node().options:
        print(f"Status:     In Progress")
    else:
        print(f"Status:     Complete")

    print("=" * 60)

    return 0


@wrap_main
def main():
    parser = argparse.ArgumentParser(
        description="AI Orchestrator - Deterministic multi-agent coordination engine",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # init
    init_parser = subparsers.add_parser("init", help="Initialize .orchestrator/ directory")
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
    run_parser.add_argument(
        "--skip-preflight", action="store_true",
        help="Skip pre-flight environment checks (useful in CI/CD)",
    )

    # preflight
    preflight_parser = subparsers.add_parser(
        "preflight", help="Check your environment before running (Python, API keys, Ollama, etc.)"
    )
    preflight_parser.add_argument(
        "--project", default=".", help="Project root directory (default: current dir)"
    )
    preflight_parser.add_argument(
        "--provider", default=None,
        help="Provider to check: claude, ollama, openai (default: reads SYMPHONY_PROVIDER env)"
    )
    preflight_parser.add_argument(
        "-v", "--verbose", action="store_true", help="Show all check details including passing ones"
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

    # flow
    flow_parser = subparsers.add_parser(
        "flow", help="Guided decision-tree workflow execution"
    )
    flow_parser.add_argument(
        "--template", required=True, help="Template name (e.g., code_review, refactor_code, new_feature)"
    )
    flow_parser.add_argument(
        "--var", action='append', default=[], help="Variables (format: key=value)"
    )
    flow_parser.add_argument(
        "--project", default=".", help="Project root directory (default: current dir)"
    )
    flow_parser.add_argument(
        "-v", "--verbose", action="store_true", help="Detailed output"
    )
    flow_parser.add_argument(
        "--no-compile", action="store_true", help="Disable prompt compiler"
    )
    flow_parser.add_argument(
        "--no-ir", action="store_true", help="Disable IR pipeline"
    )

    # flow-list
    flow_list_parser = subparsers.add_parser(
        "flow-list", help="List available flow templates"
    )

    # flow-status
    flow_status_parser = subparsers.add_parser(
        "flow-status", help="Show status of flow projects"
    )
    flow_status_parser.add_argument(
        "--project", default=".", help="Project root directory (default: current dir)"
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    commands = {
        "init":      cmd_init,
        "run":       cmd_run,
        "preflight": cmd_preflight,
        "status":    cmd_status,
        "history":   cmd_history,
        "efficiency":cmd_efficiency,
        "flow":      cmd_flow,
        "flow-list": cmd_flow_list,
        "flow-status": cmd_flow_status,
    }

    return commands[args.command](args)


if __name__ == "__main__":
    sys.exit(main() or 0)
