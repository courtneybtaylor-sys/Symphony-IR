# Workflow Templates Guide

Symphony-IR includes pre-built workflow templates for common enterprise tasks. This guide explains how to use and customize them.

## What Are Templates?

Templates are pre-configured workflow patterns that guide multi-agent orchestration through specific domains:

- **Code Review** — Analyze code quality and style
- **Security Audit** — Identify security issues
- **Cloud Architecture** — Design scalable systems
- **Data Pipeline** — Plan data workflows
- **ML Model** — Design ML solutions
- **Incident Response** — Handle security incidents
- **Compliance Audit** — Check regulatory compliance
- **Performance Optimization** — Improve efficiency

Each template defines:
- 🤖 Agent roles and prompts
- 📋 Workflow steps
- 🎯 Variables and inputs
- 📊 Output structure

## Using Templates

### From CLI

```bash
# List all templates
python orchestrator.py flow-list

# Run a template
python orchestrator.py flow code_review --variables component=auth.py

# Run with multiple variables
python orchestrator.py flow cloud_architecture \
  --variables requirements="high availability, multi-region" \
  --variables budget="$10k/month"

# Filter by domain
python orchestrator.py flow-list --domain security

# Search templates
python orchestrator.py flow-list --search "audit"
```

### From GUI

1. Open Symphony-IR desktop app
2. Go to "Flows" tab
3. Select template from dropdown
4. Enter required variables
5. Click "Run Flow"

### From Python

```python
from ai_orchestrator.orchestrator import Orchestrator

orchestrator = Orchestrator()

# Run template
result = orchestrator.flow(
    template='code_review',
    variables={
        'component': 'src/auth.py',
        'context': 'REST API authentication'
    }
)

print(result['architect'])
print(result['implementer'])
print(result['reviewer'])
```

## Available Templates

### Code Review

Review code for quality, style, and best practices.

**Variables:**
- `component` — File or component to review
- `context` — Additional context (optional)
- `focus` — Specific focus area (security, performance, readability)

**Example:**
```bash
python orchestrator.py flow code_review --variables component=src/main.py focus=performance
```

**Output:**
- Architect: Code structure analysis
- Implementer: Detailed improvement suggestions
- Reviewer: Quality assessment and final recommendations

### Security Audit

Identify security vulnerabilities and compliance issues.

**Variables:**
- `target` — System or code to audit
- `scope` — Scope of audit (application, infrastructure, codebase)
- `frameworks` — Compliance frameworks (optional)

**Example:**
```bash
python orchestrator.py flow security_audit --variables target=api-server scope=application
```

**Output:**
- Vulnerabilities identified
- Risk assessment
- Remediation recommendations
- Compliance status

### Cloud Architecture

Design scalable, reliable cloud infrastructure.

**Variables:**
- `requirements` — System requirements
- `scale` — Expected scale (small, medium, large)
- `budget` — Budget constraints
- `providers` — Preferred cloud providers (AWS, GCP, Azure)

**Example:**
```bash
python orchestrator.py flow cloud_architecture \
  --variables requirements="multi-tenant SaaS" \
  --variables budget="$20k/month"
```

**Output:**
- Proposed architecture
- Technology recommendations
- Cost estimation
- Scalability assessment

### Data Pipeline

Plan and design data workflows.

**Variables:**
- `source` — Data source description
- `transformation` — Required transformations
- `destination` — Target system
- `volume` — Data volume (small, medium, large)

**Example:**
```bash
python orchestrator.py flow data_pipeline \
  --variables source="PostgreSQL database" \
  --variables transformation="aggregation and cleansing"
```

**Output:**
- Pipeline architecture
- Tool recommendations
- Data quality measures
- Performance optimization

### ML Model

Design machine learning solutions.

**Variables:**
- `problem` — Problem statement
- `data` — Data description
- `constraints` — Constraints (latency, accuracy, resources)
- `timeline` — Project timeline

**Example:**
```bash
python orchestrator.py flow ml_model \
  --variables problem="customer churn prediction" \
  --variables data="6 months of transaction history"
```

**Output:**
- Problem framing
- Model selection
- Data pipeline design
- Evaluation strategy

### Incident Response

Handle security or operational incidents.

**Variables:**
- `incident` — Incident description
- `severity` — Severity level (low, medium, high, critical)
- `systems` — Affected systems
- `context` — Additional context

**Example:**
```bash
python orchestrator.py flow incident_response \
  --variables incident="unauthorized access detected" \
  --variables severity=high
```

**Output:**
- Incident triage
- Containment plan
- Remediation steps
- Post-incident review

### Compliance Audit

Ensure compliance with regulations and standards.

**Variables:**
- `framework` — Compliance framework (GDPR, SOC2, ISO27001, HIPAA)
- `scope` — Scope of audit (data, infrastructure, process)
- `systems` — Systems to audit

**Example:**
```bash
python orchestrator.py flow compliance_audit \
  --variables framework=GDPR \
  --variables scope=data
```

**Output:**
- Gap analysis
- Compliance status
- Remediation plan
- Timeline and resources

### Performance Optimization

Improve system performance.

**Variables:**
- `system` — System to optimize
- `metrics` — Performance metrics (throughput, latency, memory)
- `constraints` — Constraints (budget, compatibility)
- `priority` — Priority areas

**Example:**
```bash
python orchestrator.py flow performance_optimization \
  --variables system="web application" \
  --variables metrics="page load time"
```

**Output:**
- Performance analysis
- Bottleneck identification
- Optimization recommendations
- Expected improvements

## Creating Custom Templates

### Template Structure

Create a YAML file in `ai-orchestrator/flow/templates/`:

```yaml
# my_template.yaml
name: "Custom Analysis"
version: "1.0"
description: "Analyze something custom"
domain: "custom"
difficulty: "intermediate"
estimated_duration: "10-15 minutes"
tags: ["custom", "analysis"]

variables:
  input_file:
    description: "File to analyze"
    required: true
  focus_area:
    description: "Area to focus on"
    required: false
    default: "general"

agents:
  architect:
    prompt: "You are an architect. Analyze the structure and design..."
  implementer:
    prompt: "You are an implementer. Provide detailed improvements..."
  reviewer:
    prompt: "You are a reviewer. Critique the recommendations..."

workflow:
  - step: 1
    agent: architect
    task: "Analyze the {{input_file}}. Focus on {{focus_area}}."

  - step: 2
    agent: implementer
    task: "Based on the architect's analysis, provide detailed recommendations."

  - step: 3
    agent: reviewer
    task: "Review the recommendations and provide critique."
```

### Using Variables in Templates

```yaml
# Variables are substituted with {{variable_name}}
task: "Review {{component}} for {{focus}} issues"

# Conditionals (in advanced templates)
conditional:
  - if: focus == "security"
    prompt: "Focus on security vulnerabilities"
  - if: focus == "performance"
    prompt: "Focus on performance optimizations"
```

### Testing Custom Templates

```bash
# Verify template syntax
python -c "import yaml; yaml.safe_load(open('my_template.yaml'))"

# Run custom template
python orchestrator.py flow my_template --variables input_file=test.py focus_area=security
```

## Template Metadata

Each template includes metadata for discovery and filtering:

```yaml
domain: "security"                    # Domain: security, cloud, data, ml, etc.
difficulty: "intermediate"            # Level: beginner, intermediate, advanced
estimated_duration: "15-20 minutes"   # Time estimate
tags: ["audit", "compliance"]         # Search tags
industry: ["finance", "healthcare"]   # Relevant industries
prerequisites: ["Python 3.10+"]       # Requirements
```

## Best Practices

1. **Start Simple** — Use built-in templates before creating custom ones
2. **Clear Variables** — Provide descriptive variable names and prompts
3. **Realistic Scope** — Break complex tasks into multiple steps
4. **Agent Clarity** — Give agents specific, focused roles
5. **Document Outputs** — Make expected outputs clear in workflow

## Sharing Templates

To share custom templates:

1. Commit to `ai-orchestrator/flow/templates/`
2. Document in template YAML with clear descriptions
3. Add examples to this guide
4. Submit PR to repository

## See Also

- [CLI Guide](CLI.md) — Running workflows
- [Python API](PYTHON_API.md) — Programmatic usage
- [Architecture](../ARCHITECTURE.md) — Flow system design
- [Contributing](../../CONTRIBUTING.md) — Template contribution guidelines

## References

- Template files: `ai-orchestrator/flow/templates/`
- Flow system: `ai-orchestrator/flow/engine.py`
- Agent definitions: `ai-orchestrator/agents/`
