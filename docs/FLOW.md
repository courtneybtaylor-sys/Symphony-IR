# Symphony Flow - Guided Decision-Tree Workflows

Symphony Flow is a production-ready system for guided, interactive workflows that help you make structured decisions and automatically execute tasks via Symphony-IR's orchestrator.

## Overview

Symphony Flow combines:
- **Bounded decisions**: 2-4 options per step (prevents analysis paralysis)
- **Structured workflows**: Pre-built templates for common tasks
- **Automatic execution**: Each node maps to PromptIR and runs via Symphony-IR
- **State tracking**: Full history and persistence of decisions

## Quick Start

### 1. List Available Templates

```bash
python orchestrator.py flow-list
```

Output:
```
📚 Available Symphony Flow Templates:

🎯 Code Review Assistant (code_review)
   Guided code review workflow with focused analysis paths
   Nodes: 4

🎯 Code Refactoring Guide (refactor_code)
   Structured refactoring workflow with design and quick-fix paths
   Nodes: 4

🎯 Feature Implementation Guide (new_feature)
   Guided workflow for planning and implementing new features
   Nodes: 4

🎯 API Design & Specification (api_design)
   Guided workflow for designing RESTful and GraphQL APIs
   Nodes: 6

🎯 Database Schema Design (database_schema)
   Guided workflow for designing database schemas and relationships
   Nodes: 6

🎯 Testing Strategy Planning (testing_strategy)
   Guided workflow for creating comprehensive testing strategies
   Nodes: 7

🎯 Documentation Planning (documentation)
   Guided workflow for creating comprehensive project documentation
   Nodes: 6
```

### 2. Run a Flow

```bash
python orchestrator.py flow --template code_review --var component=auth.py
```

### 3. Track Your Projects

```bash
python orchestrator.py flow-status
```

## Available Templates

### Code Review (`code_review`)

Review code quality with focused analysis paths:
- **Bugs**: Identify logic errors and potential issues
- **Style**: Check conventions and consistency
- **Performance**: Find bottlenecks and optimizations

**Usage:**
```bash
python orchestrator.py flow --template code_review --var component=src/auth.py
```

### Code Refactoring (`refactor_code`)

Structured refactoring guidance:
- **Design improvements**: Propose better architecture
- **Quick fixes**: High-impact, low-risk improvements
- **Dependencies**: Optimize and upgrade dependencies

**Usage:**
```bash
python orchestrator.py flow --template refactor_code --var component=database.py
```

### New Feature (`new_feature`)

Plan and implement new features:
- **Architecture design**: Create technical design
- **Implementation checklist**: Step-by-step tasks
- **Risk analysis**: Identify and mitigate risks

**Usage:**
```bash
python orchestrator.py flow --template new_feature --var feature="User authentication"
```

### API Design (`api_design`)

Design robust APIs:
- **REST API**: Design RESTful endpoints and methods
- **GraphQL API**: Design GraphQL schema with queries
- **Hybrid API**: Combine REST and GraphQL
- **Security**: Plan authentication and authorization
- **Versioning**: Design version strategy

**Usage:**
```bash
python orchestrator.py flow --template api_design --var api_name="user-service"
```

### Database Schema (`database_schema`)

Design database schemas:
- **Relational (SQL)**: Tables, relationships, indexes
- **NoSQL**: Document structures, collections
- **Hybrid**: Combine both approaches
- **Optimization**: Query and index planning
- **Normalization**: Balance performance vs. integrity

**Usage:**
```bash
python orchestrator.py flow --template database_schema --var database_name="accounts"
```

### Testing Strategy (`testing_strategy`)

Plan comprehensive testing:
- **Unit testing**: Test individual components
- **Integration testing**: Test system interactions
- **Test pyramid**: Full coverage strategy
- **Performance testing**: Load and stress testing
- **Security testing**: Vulnerability assessment

**Usage:**
```bash
python orchestrator.py flow --template testing_strategy --var component_name="payment"
```

### Documentation (`documentation`)

Create project documentation:
- **User documentation**: End-user guides
- **Developer documentation**: API and code docs
- **Complete documentation**: All types
- **Video documentation**: Tutorial content
- **Architecture documentation**: Design docs

**Usage:**
```bash
python orchestrator.py flow --template documentation --var project_name="MyProject"
```

## How Flows Work

### 1. Start Flow

```bash
python orchestrator.py flow --template code_review --var component=auth.py
```

### 2. See Current Step

```
================================================
🎼 Symphony Flow: code_review
📋 Project ID: a1b2c3d4
📌 Variables: component=auth.py
================================================

✓ Step 1: Starting code review

What's next?
  A) Focus on bugs
      Look for potential bugs and logic errors
  B) Focus on style
      Check code style and conventions
  C) Focus on performance
      Identify performance bottlenecks

Choice:
```

### 3. Select Option

Type your choice (A, B, or C):

```
Choice: A
→ Selected: A

⚙️  Executing via Symphony-IR...

✓ Execution complete
  Run ID: xyz789
  Confidence: 0.92
  Agent responses: 3
```

### 4. Continue or Finish

If the node has more options, repeat. Otherwise:

```
🎉 Workflow complete!

============================================================
📊 Flow Summary
============================================================
Project:    a1b2c3d4
Template:   code_review
Nodes:      2
Decisions:  1
Executions: 1
Current:    bugs
Status:     Complete
============================================================

💾 Session saved: .orchestrator/flows/a1b2c3d4.json
```

## Commands

### `orchestrator flow`

Execute a guided workflow:

```bash
python orchestrator.py flow \
  --template <name> \
  --var key=value \
  --var key2=value2 \
  [--verbose] \
  [--no-compile] \
  [--no-ir] \
  [--project .]
```

**Options:**
- `--template` (required): Template name
- `--var`: Variables (format: key=value, multiple allowed)
- `--verbose`: Show detailed output
- `--no-compile`: Disable prompt compiler
- `--no-ir`: Disable IR pipeline
- `--project`: Project root directory

### `orchestrator flow-list`

List available templates with descriptions:

```bash
python orchestrator.py flow-list
```

### `orchestrator flow-status`

Show status of active flow projects:

```bash
python orchestrator.py flow-status [--project .]
```

Output:
```
🎼 Flow Projects (3 total):

📋 a1b2c3d4 | code_review
   Current: bugs
   Progress: 2 nodes, 1 decision

📋 b2c3d4e5 | new_feature
   Current: design
   Progress: 3 nodes, 2 decisions

📋 c3d4e5f6 | api_design
   Current: rest_design
   Progress: 2 nodes, 1 decision
```

## Variables

Variables allow you to customize flows:

```bash
# Single variable
python orchestrator.py flow --template code_review --var component=auth.py

# Multiple variables
python orchestrator.py flow --template api_design \
  --var api_name="user-service" \
  --var version="v2"

# With spaces (use quotes)
python orchestrator.py flow --template new_feature \
  --var feature="User authentication with OAuth"
```

Variables are:
- Resolved in node prompts (`{variable}`)
- Available throughout the workflow
- Persisted in project state
- Used for context in PromptIR

## Session Management

Flows automatically save state to:

```
.orchestrator/flows/{project_id}.json
```

### Session Contents

```json
{
  "project_id": "a1b2c3d4",
  "template_id": "code_review",
  "current_node_id": "bugs",
  "selected_path": ["start", "bugs"],
  "decisions": ["A"],
  "node_ledger_ids": {
    "bugs": "xyz789"
  },
  "variables": {
    "component": "auth.py"
  }
}
```

### View Session

```bash
cat .orchestrator/flows/a1b2c3d4.json | jq .
```

## Creating Custom Templates

### Template Structure

```yaml
template_id: "my_template"
name: "Template Display Name"
description: "Brief description of the template"

nodes:
  start:
    summary: "What this node does"
    role: "architect"  # or implementer, reviewer, researcher
    intent: "High-level objective with {variables}"
    phase: "PLANNING"  # PLANNING, IMPLEMENTATION, REVIEW, RESEARCH, SYNTHESIS
    priority: 5        # 1-10
    context_refs:
      - "file:{component}"
    constraints:
      - "Output constraint"
    token_budget_hint: 1000
    options:
      - id: "A"
        label: "Option label"
        description: "What this choice does"
        next_node_id: "next_node_id"
```

### Example: Simple Template

Create `flow/templates/security_audit.yaml`:

```yaml
template_id: "security_audit"
name: "Security Audit"
description: "Guided security audit workflow"

nodes:
  start:
    summary: "Starting security audit"
    role: "reviewer"
    intent: "Perform security audit of {component}"
    phase: "REVIEW"
    priority: 8
    context_refs:
      - "file:{component}"
    constraints: []
    token_budget_hint: 1000
    options:
      - id: "A"
        label: "OWASP review"
        description: "Check OWASP top 10"
        next_node_id: "owasp"
      - id: "B"
        label: "Dependency audit"
        description: "Check dependencies"
        next_node_id: "dependencies"

  owasp:
    summary: "OWASP audit"
    role: "reviewer"
    intent: "Review {component} against OWASP top 10"
    phase: "REVIEW"
    priority: 9
    context_refs:
      - "file:{component}"
    constraints:
      - "Check each OWASP category"
      - "List vulnerabilities with severity"
    token_budget_hint: 1500
    options: []

  dependencies:
    summary: "Dependency audit"
    role: "architect"
    intent: "Audit dependencies in {component}"
    phase: "REVIEW"
    priority: 7
    context_refs:
      - "file:{component}"
    constraints:
      - "Identify vulnerable packages"
      - "Check for outdated versions"
    token_budget_hint: 1200
    options: []
```

Then use it:

```bash
python orchestrator.py flow --template security_audit --var component=src/auth.py
```

## Best Practices

### 1. Design Bounded Choices

Keep options to 2-4 per node. This prevents:
- Decision paralysis
- Overwhelming users
- Complex branching

### 2. Clear Node Descriptions

Use specific, actionable summaries:

```yaml
# Good
summary: "Analyzing performance bottlenecks"

# Avoid
summary: "Analysis phase"
```

### 3. Variable Naming

Use consistent, descriptive variable names:

```bash
# Good
--var component=auth.py
--var api_name="user-service"

# Avoid
--var c=auth.py
--var name="x"
```

### 4. Terminal Node Design

Terminal nodes (no options) represent the end of a path:

```yaml
final_node:
  summary: "Security audit complete"
  options: []  # Empty = terminal
```

### 5. Path Variety

Design templates with multiple logical paths:

```yaml
start:
  options:
    - id: "A"
      next_node_id: "path1"
    - id: "B"
      next_node_id: "path2"
    - id: "C"
      next_node_id: "path3"
```

## Examples

### Example 1: Code Review Workflow

```bash
# Start code review
$ python orchestrator.py flow --template code_review --var component=src/payment.py

🎼 Symphony Flow: code_review
📋 Project ID: a1b2c3d4
📌 Variables: component=src/payment.py

✓ Step 1: Starting code review

What's next?
  A) Focus on bugs
      Look for potential bugs and logic errors
  B) Focus on style
      Check code style and conventions
  C) Focus on performance
      Identify performance bottlenecks

Choice: A
→ Selected: A

⚙️  Executing via Symphony-IR...

✓ Execution complete
  Run ID: xyz789
  Confidence: 0.92
  Agent responses: 3

🎉 Workflow complete!

💾 Session saved: .orchestrator/flows/a1b2c3d4.json
```

### Example 2: API Design Workflow

```bash
$ python orchestrator.py flow --template api_design --var api_name="order-service"

🎼 Symphony Flow: api_design
📋 Project ID: b2c3d4e5
📌 Variables: api_name=order-service

✓ Step 1: Defining API scope

What's next?
  A) REST API
      Design a RESTful API with standard HTTP methods
  B) GraphQL API
      Design a GraphQL API with schemas and queries
  C) Hybrid API
      Design both REST and GraphQL endpoints

Choice: A
→ Selected: A

⚙️  Executing via Symphony-IR...
(execution...)

✓ Step 2: Designing REST API
What's next?
  A) Add security
      Design authentication and authorization
  B) Add versioning
      Plan API versioning strategy

Choice: A
...
```

## Troubleshooting

### "Template not found"

```bash
# List available templates
python orchestrator.py flow-list

# Check template exists
ls ai-orchestrator/flow/templates/
```

### "Invalid variable format"

Variables must use `key=value` format:

```bash
# Correct
python orchestrator.py flow --template code_review --var component=auth.py

# Incorrect
python orchestrator.py flow --template code_review --var component
```

### "No agents found"

Flow will use mock agents. To use real agents:

```bash
python orchestrator.py init --project .
# Edit .orchestrator/agents.yaml
# Set ANTHROPIC_API_KEY environment variable
```

### Keyboard Interrupt

Press Ctrl+C to stop flow. State is saved:

```
⏸️  Flow interrupted by user

💾 Session saved: .orchestrator/flows/a1b2c3d4.json
```

## Performance

- **Typical execution time**: 30-90 seconds per node (depends on Claude API)
- **Token budget**: 3000 tokens per node (default)
- **Max phases**: 10 per orchestrator run
- **Parallel execution**: Enabled for agent responses

## Advanced Configuration

### Custom Agent Configuration

Edit `.orchestrator/agents.yaml`:

```yaml
agents:
  - name: architect
    role: System Architect
    model_provider: anthropic
    model_config:
      api_key: ${ANTHROPIC_API_KEY}
      model: claude-sonnet-4-20250514
    temperature: 0.7
    max_tokens: 2000
```

### Disable Compilation

Skip prompt compiler for faster execution:

```bash
python orchestrator.py flow --template code_review --var component=auth.py --no-compile
```

### Disable IR Pipeline

Use direct compilation instead of IR pipeline:

```bash
python orchestrator.py flow --template code_review --var component=auth.py --no-ir
```

## Integration with Other Tools

Flows integrate with:
- **Orchestrator**: Full orchestration with governance
- **Prompt Compiler**: Token optimization
- **Schema Validator**: Output format enforcement
- **IR Pipeline**: Governance and transformations
- **Governance Engine**: Policy checks

## Status

- ✅ Production ready
- ✅ 7 built-in templates
- ✅ Full orchestrator integration
- ✅ State persistence
- ✅ Error handling

---

**Questions?** See the main [README.md](../README.md) or check out a template:

```bash
python orchestrator.py flow-list
```
