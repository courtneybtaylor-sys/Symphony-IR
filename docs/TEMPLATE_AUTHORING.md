# Template Authoring Guide — Creating Symphony Flow Templates

## Introduction

This guide explains how to create custom Symphony Flow templates for specialized workflows. Templates are YAML-based decision trees that guide Claude through complex tasks step-by-step.

## Template Anatomy

A complete template looks like this:

```yaml
template_id: "unique_lowercase_id"
name: "Human-Readable Template Name"
description: "What this template helps users accomplish (1-2 sentences)"
domain: "Category (Development, Security, Cloud, Data, etc.)"
target_audience: "Who should use this (Job titles or roles)"

nodes:
  start:
    summary: "Node heading (visible in UI)"
    role: "Role the AI takes (reviewer, architect, analyst, etc.)"
    intent: "Goal statement. Use {variable} for context. What will Claude do?"
    phase: "PLANNING | DESIGN | ANALYSIS | ASSESSMENT | OPTIMIZATION | etc."
    priority: "1-10 (higher = more urgent/critical)"
    context_refs:
      - "file:{file_name}"
      - "requirements:{requirement_name}"
    constraints:
      - "Specific instruction 1"
      - "Specific instruction 2"
    token_budget_hint: 1200 # Estimated tokens for this node
    options:
      - id: "A"
        label: "User-facing option label"
        description: "What this path explores (optional)"
        next_node_id: "target_node"
      - id: "B"
        label: "Another option"
        next_node_id: "another_node"

  target_node:
    summary: "Analyzing bugs"
    role: "reviewer"
    intent: "Identify bugs in {file_name}"
    phase: "ANALYSIS"
    priority: 8
    context_refs:
      - "file:{file_name}"
    constraints:
      - "List issues with severity"
      - "Include reproduction steps"
    token_budget_hint: 1500
    options: [] # Terminal node (no further options)
```

## Step-by-Step Tutorial

### 1. Plan Your Template

Before writing YAML, think about:

**What problem does this solve?**
- What is the user trying to accomplish?
- What is their starting context?
- What decisions do they need to make?

**What are the key decision points?**
- What are 2-4 main paths through the workflow?
- Are there sub-decisions within each path?
- What's the maximum depth (usually 3-4 levels)?

**What information does Claude need?**
- What files or context should be analyzed?
- What constraints or requirements apply?
- What depth of analysis is needed (token budget)?

### 2. Define Your Nodes

Write out the decision tree on paper or whiteboard:

```
START
├─ Path A (Bug Analysis)
│  ├─ Categorize bugs by severity
│  └─ Provide fixes
├─ Path B (Performance Analysis)
│  ├─ Identify bottlenecks
│  └─ Suggest optimizations
└─ Path C (Architecture Review)
   └─ Suggest improvements
```

### 3. Write Node Descriptions

Each node needs:

**`summary`** (1-2 words)
- Heading visible in UI
- Examples: "Analyzing bugs", "Evaluating performance"

**`role`** (1-2 words)
- What role Claude takes
- Examples: "reviewer", "analyst", "architect"

**`intent`** (1-3 sentences)
- Goal statement with {variables}
- What Claude will analyze and what the output should be
- Variables are replaced with user input at runtime

**`phase`** (1 word)
- Which phase of work (PLANNING, DESIGN, ANALYSIS, OPTIMIZATION, etc.)
- Helps organize nodes visually

**`priority`** (1-10)
- 10 = critical/urgent (security, outages)
- 8 = high (important design decisions)
- 5 = normal (standard analysis)
- 1-3 = low priority

**`constraints`** (2-5 bullets)
- Specific, actionable instructions
- Tell Claude exactly what to focus on
- Example: "List all issues with CVSS score if available"

**`token_budget_hint`** (number)
- Estimated tokens needed for Claude's response
- Use 800-1000 for analysis, 1200-1500 for deep analysis
- Larger budgets = more detailed responses

### 4. Define Decision Options

Each node (except terminal nodes) has `options`:

```yaml
options:
  - id: "A"                          # Single letter
    label: "User-facing label"       # What user sees
    description: "Optional detail"   # Why choose this path
    next_node_id: "target_node"      # Where it leads
  - id: "B"
    label: "Another option"
    next_node_id: "another_node"
```

**Best practices:**
- 2-4 options per node (not more)
- Options should be clearly different
- Each leads to a different analysis path

### 5. Write the YAML File

Create file: `ai-orchestrator/flow/templates/template_name.yaml`

```yaml
template_id: "template_name"
name: "Template Name"
description: "Brief description"
domain: "Development"
target_audience: "Software Engineers"

nodes:
  start:
    summary: "Getting started"
    role: "analyst"
    intent: "Plan analysis of {component}"
    phase: "PLANNING"
    priority: 5
    context_refs: []
    constraints: []
    token_budget_hint: 800
    options:
      - id: "A"
        label: "Path 1"
        next_node_id: "node_1"
      - id: "B"
        label: "Path 2"
        next_node_id: "node_2"

  node_1:
    summary: "Deep dive 1"
    role: "analyst"
    intent: "Analyze {component} for X"
    phase: "ANALYSIS"
    priority: 7
    context_refs:
      - "file:{component}"
    constraints:
      - "Provide specific examples"
    token_budget_hint: 1200
    options: []

  node_2:
    summary: "Deep dive 2"
    role: "analyst"
    intent: "Analyze {component} for Y"
    phase: "ANALYSIS"
    priority: 7
    context_refs:
      - "file:{component}"
    constraints:
      - "Compare to best practices"
    token_budget_hint: 1200
    options: []
```

## Best Practices

### Node Naming
- Use lowercase with underscores: `security_review`, `cost_analysis`
- Be descriptive: `node_1`, `node_2` are bad
- Match node name to its purpose

### Intent Statements
❌ **Bad:** "Review code for issues"
✅ **Good:** "Identify potential bugs and logic errors in {component}, with reproduction steps and severity ratings"

❌ **Bad:** "Analyze database"
✅ **Good:** "Design optimized database schema for {application}, considering performance, normalization, and scalability"

### Context Variables
Use variables to make templates reusable:

```yaml
intent: "Review security of {application} API, focusing on {area}"
# User provides: application="my-app", area="authentication"
# Template becomes: "Review security of my-app API, focusing on authentication"
```

Common variable names:
- `{component}` — Code file or module
- `{application}` — Full application name
- `{service}` — Microservice or API
- `{model_type}` — Type of ML model
- `{target}` — Target of analysis (security, performance, etc.)
- `{incident_type}` — Type of incident
- `{phase}` — Development phase

### Constraints (Instructions)

Constraints are **concrete**, **specific** instructions that guide Claude:

❌ **Bad:** "Be thorough"
✅ **Good:** "List all N+1 query issues with specific line numbers and optimization techniques"

❌ **Bad:** "Think about security"
✅ **Good:** "Check authentication, authorization, input validation, and error handling"

### Token Budgets

Estimate tokens needed for each node:

| Response Type | Token Budget |
|---------------|--------------|
| Quick analysis (3-5 bullets) | 600-800 |
| Standard response (2-3 pages) | 1000-1200 |
| Deep analysis (4-6 pages) | 1400-1600 |
| Very thorough (6-8 pages) | 1800-2000 |

Test your template and adjust based on actual response length.

### Decision Paths

Keep the decision tree balanced:

- **Too shallow:** No meaningful choices, few paths
- **Too deep:** User makes 6+ decisions to reach result
- **Just right:** 3-4 levels, 2-4 options per node

```
Shallow (bad):
  start → analysis → done

Balanced (good):
  start
  ├─ path1 → sub1 → done
  ├─ path2 → sub2 → done
  └─ path3 → sub3 → done

Deep (bad):
  start → A → B → C → D → E → F → done
```

## Testing Your Template

### 1. Validate YAML Syntax

```bash
python3 -c "
import yaml
with open('ai-orchestrator/flow/templates/template_name.yaml') as f:
    yaml.safe_load(f)
print('✅ YAML is valid')
"
```

### 2. Load in Code

```python
from ai-orchestrator.flow.engine import TemplateLoader

loader = TemplateLoader()
template = loader.load_template('template_name')
print(f"✅ Loaded template: {template['name']}")
```

### 3. Test in Desktop GUI

1. Launch `gui/main.py`
2. Click **Symphony Flow** tab
3. Find your template in the dropdown
4. Test each decision path
5. Verify outputs make sense

### 4. Test in Web GUI

```bash
streamlit run gui/streamlit_app.py
# Test "Symphony Flow" tab
```

### 5. Manual CLI Test

```bash
python ai-orchestrator/orchestrator.py flow start template_name
```

## Common Mistakes to Avoid

### 1. Unclear Intent Statements

❌ "Analyze code" — Too vague
✅ "Identify performance bottlenecks in {component} with estimated impact and optimization suggestions"

### 2. Dead Nodes

Every node except terminal nodes should lead somewhere:

```yaml
options:
  - id: "A"
    label: "Option A"
    next_node_id: "next_node"  # ✅ This node must exist

  - id: "B"
    label: "Option B"
    next_node_id: "nonexistent"  # ❌ Will crash!
```

### 3. Inconsistent Variable Names

```yaml
intent: "Analyze {component}"
context_refs:
  - "file:{component_name}"  # ❌ Different variable name!
```

**Fix:** Use same variable names consistently (`{component}` everywhere).

### 4. Too Many Options

```yaml
options:
  - id: "A"
    label: "Option A"
  - id: "B"
    label: "Option B"
  - id: "C"
    label: "Option C"
  - id: "D"
    label: "Option D"
  - id: "E"
    label: "Option E"  # ❌ Too many! Overwhelming.
```

Keep to 2-4 options per node.

### 5. Insufficient Context

```yaml
intent: "Review code"
context_refs: []  # ❌ Claude has no context!
```

**Fix:** Provide file references or requirements:
```yaml
context_refs:
  - "file:{component}"
  - "requirements:performance"
```

### 6. Vague Constraints

```yaml
constraints:
  - "Be comprehensive"  # ❌ Vague
```

**Fix:** Be specific:
```yaml
constraints:
  - "List all queries that could cause N+1 issues"
  - "Provide specific line numbers and fix suggestions"
```

## Template Checklist

Before submitting a new template:

- [ ] YAML is valid (no syntax errors)
- [ ] `template_id` is unique (no conflicts)
- [ ] All `next_node_id` references exist
- [ ] Intent statements are specific and clear
- [ ] Constraints are concrete and actionable
- [ ] Token budgets are realistic
- [ ] Tested in desktop GUI
- [ ] Tested in web GUI
- [ ] Tested in CLI
- [ ] Documentation added to `FLOW_TEMPLATES.md`
- [ ] No dead or unreachable nodes
- [ ] Decision paths are balanced (not too deep)
- [ ] Variables are consistent throughout

## Template Versioning

If you update a template significantly:

```yaml
template_id: "template_name"
version: "2.0"  # Add version field
name: "Template Name (v2)"
changelog: |
  - Added new decision paths
  - Updated token budgets
```

## Contributing Templates

To contribute a template back to the project:

1. **Fork the repo** and create a branch
2. **Add your template** to `ai-orchestrator/flow/templates/`
3. **Update docs** in `FLOW_TEMPLATES.md` with description and use cases
4. **Add tests** (if applicable) to `tests/test_flows.py`
5. **Submit a PR** with:
   - Template YAML file
   - Documentation updates
   - Test results
   - Use case examples

## Examples

### Example 1: Simple Code Review

See actual template: [`code_review.yaml`](../ai-orchestrator/flow/templates/code_review.yaml)

### Example 2: Complex Security Audit

See actual template: [`security_audit.yaml`](../ai-orchestrator/flow/templates/security_audit.yaml)

### Example 3: Multi-Path Cloud Design

See actual template: [`cloud_architecture.yaml`](../ai-orchestrator/flow/templates/cloud_architecture.yaml)

## Troubleshooting

### Template doesn't appear in GUI dropdown
- Check `template_id` is in the file name (e.g., `my_template.yaml` for `template_id: "my_template"`)
- Check file is in `ai-orchestrator/flow/templates/`
- Reload GUI (restart application)

### YAML load error
- Use `python3 -c "import yaml; yaml.safe_load(open('file.yaml'))"` to validate
- Check indentation (2 spaces, no tabs)
- Check quotes around strings with colons

### Claude response is too short
- Increase `token_budget_hint`
- Make constraints more detailed
- Check intent statement is specific enough

### Claude response is too long
- Decrease `token_budget_hint`
- Simplify constraints
- Break into separate nodes

## Resources

- [Design Tokens Specification](https://design-tokens.github.io/community-group/format/)
- [YAML Specification](https://yaml.org/)
- [Claude Prompt Engineering Guide](https://docs.anthropic.com/en/docs/intro)

---

**Last updated:** 2026-02-22
**Status:** Production Ready
**Questions?** Open an issue or discussion on GitHub
