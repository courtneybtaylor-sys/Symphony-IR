# Symphony Flow Templates — Guided AI Workflows

## Overview

Symphony Flow Templates are guided, multi-step workflows that structure complex tasks into decision trees. They help users solve problems systematically by breaking them into manageable phases with clear decision points.

**Current Status:** 12 production templates across 6 domains

## Template Catalog

### Developer-Focused Templates (7 templates)

#### 1. Code Review Assistant
**ID:** `code_review`
**Purpose:** Structured code review with multiple focus areas
**When to use:** Reviewing pull requests, assessing code quality
**Paths:**
- Focus on bugs → Identify logic errors and issues
- Focus on style → Check conventions and readability
- Focus on performance → Find bottlenecks and optimizations
**Audience:** Software Engineers, Tech Leads

---

#### 2. Code Refactoring Guide
**ID:** `refactor_code`
**Purpose:** Plan code improvements and refactoring efforts
**When to use:** Before starting large refactoring projects
**Paths:**
- Design improvements → Architecture changes
- Quick wins → Small, impactful changes
- Dependency cleanup → Reduce technical debt
**Audience:** Software Engineers, Architects

---

#### 3. Feature Implementation Guide
**ID:** `new_feature`
**Purpose:** Plan and design new features
**When to use:** Starting feature development
**Paths:**
- Architecture design → System design and interfaces
- Implementation → Code structure and dependencies
- Risk analysis → Edge cases and failure modes
**Audience:** Product Managers, Software Engineers

---

#### 4. API Design & Specification
**ID:** `api_design`
**Purpose:** Design and document APIs (REST, GraphQL, gRPC)
**When to use:** Creating new APIs or updating existing ones
**Paths:**
- REST API → HTTP-based design
- GraphQL API → Query language design
- Hybrid → Multi-protocol approach
- Security design → Authentication and authorization
- Versioning strategy → API evolution planning
**Audience:** Backend Engineers, API Architects

---

#### 5. Database Schema Design
**ID:** `database_schema`
**Purpose:** Design optimal database schemas
**When to use:** Starting new database projects or redesigning existing ones
**Paths:**
- Relational (SQL) → ACID database design
- NoSQL → Document or key-value design
- Hybrid → Mixed polyglot persistence
- Optimization → Indexing and query performance
- Normalization → Schema refinement and consistency
**Audience:** Database Architects, Backend Engineers

---

#### 6. Testing Strategy Planning
**ID:** `testing_strategy`
**Purpose:** Plan comprehensive testing approaches
**When to use:** Starting new projects or improving test coverage
**Paths:**
- Unit testing → Component-level tests
- Integration testing → System integration tests
- Test pyramid → Balanced test distribution
- Performance testing → Load and stress testing
- Security testing → Vulnerability and penetration testing
**Audience:** QA Engineers, Software Engineers, Test Architects

---

#### 7. Documentation Planning
**ID:** `documentation`
**Purpose:** Plan technical documentation strategy
**When to use:** Starting projects or improving documentation
**Paths:**
- User documentation → End-user guides
- Developer documentation → API and SDK docs
- API documentation → Endpoint and schema docs
- Examples & tutorials → Getting started guides
- Troubleshooting → FAQ and known issues
**Audience:** Technical Writers, Developers, Product Managers

---

### Enterprise-Focused Templates (5 templates)

#### 8. Security Audit & Threat Assessment
**ID:** `security_audit`
**Purpose:** Comprehensive security reviews and vulnerability assessments
**When to use:** Before major releases, compliance audits, or security assessments
**Paths:**
- OWASP Top 10 → Vulnerability-focused review
- Infrastructure security → Cloud/network security
- API security → Authentication and access control
- Data protection & compliance → Privacy and regulatory compliance
**Key Phases:** Assessment → Vulnerability Analysis → Risk Prioritization
**Audience:** Security Engineers, DevSecOps, Compliance Officers

---

#### 9. Cloud Architecture Design & Optimization
**ID:** `cloud_architecture`
**Purpose:** Design and optimize cloud infrastructure
**When to use:** Planning cloud migrations, new deployments, or infrastructure optimization
**Paths:**
- New AWS deployment → Amazon Web Services architecture
- New Azure deployment → Microsoft Azure architecture
- GCP architecture → Google Cloud Platform architecture
- Cost optimization → Reduce cloud spending
- Multi-cloud strategy → Platform-agnostic design
**Key Phases:** Design → Optimization → Security Hardening
**Audience:** Cloud Architects, DevOps Engineers, Solutions Architects

---

#### 10. Data Pipeline & ETL Design
**ID:** `data_pipeline`
**Purpose:** Design data pipelines, data warehouses, and analytics infrastructure
**When to use:** Building or optimizing data platforms
**Paths:**
- Real-time streaming → Kafka, Kinesis, Pub/Sub
- Batch ETL → Daily/hourly data loads
- Data warehouse → Snowflake, BigQuery, Redshift
- Data lake → S3, ADLS, GCS storage
- Optimization → Performance and cost tuning
**Key Phases:** Design → Quality Assurance → Performance Tuning
**Audience:** Data Engineers, Data Architects, Analytics Engineers

---

#### 11. ML Model Lifecycle & MLOps
**ID:** `ml_model_lifecycle`
**Purpose:** Design ML pipelines, training, deployment, and monitoring
**When to use:** Starting ML projects or operationalizing models
**Paths:**
- Model design & training → Architecture and algorithms
- Feature engineering → Feature pipeline design
- Model evaluation → Metrics and validation
- MLOps & deployment → Automation and CI/CD
- Model optimization → Hyperparameter tuning
**Key Phases:** Design → Evaluation → Optimization → Deployment
**Audience:** ML Engineers, Data Scientists, MLOps Engineers

---

#### 12. Incident Response & Crisis Management
**ID:** `incident_response`
**Purpose:** Structured incident response playbooks
**When to use:** During production incidents, incident reviews
**Paths:**
- Critical outage → Availability issues
- Performance degradation → Slow service response
- Security breach → Data or system compromise
- Data loss → Data integrity issues
- Infrastructure failure → Hardware/network failures
**Key Phases:** Response → Remediation → Analysis → Learning
**Audience:** Incident Commanders, SREs, On-Call Engineers

---

## Template Structure

Each template is a YAML file in `ai-orchestrator/flow/templates/` with the following structure:

```yaml
template_id: "unique_id"
name: "Human-readable name"
description: "What this template helps you do"
domain: "Category (Developer, Security, Cloud, etc.)"
target_audience: "Who should use this"

nodes:
  start:
    summary: "Node heading"
    role: "Role of the agent (reviewer, architect, etc.)"
    intent: "What the AI will do. Use {variable} for context"
    phase: "PLANNING, DESIGN, ANALYSIS, etc."
    priority: "1-10 (importance/urgency)"
    context_refs:
      - "file:{name}"        # Reference to files
      - "requirements:{name}" # Project requirements
    constraints:
      - "Specific instruction for this phase"
      - "Another constraint..."
    token_budget_hint: 1000 # Estimated tokens needed
    options:
      - id: "A"
        label: "Next step option"
        description: "What this option does"
        next_node_id: "next_node"
```

## Using Templates in Symphony-IR

### Desktop GUI (PyQt6)

1. Launch Symphony-IR desktop application
2. Click **Symphony Flow** tab
3. Select template from dropdown list
4. Click **Start Workflow**
5. Answer prompts for context variables (e.g., `{component}`, `{model_type}`)
6. Follow the guided decision tree
7. Claude analyzes each decision and provides detailed output

### Web GUI (Streamlit)

1. Open Streamlit app: `streamlit run gui/streamlit_app.py`
2. Go to **Symphony Flow** tab
3. Select template and context variables
4. Follow interactive workflow
5. View results in real-time

### CLI

```bash
# List available templates
python ai-orchestrator/orchestrator.py flow list

# Start a template flow
python ai-orchestrator/orchestrator.py flow start code_review

# Start with context
python ai-orchestrator/orchestrator.py flow start security_audit --target "my-app.py"
```

## Template Selection Guide

### For Software Engineers

**Starting a feature?** → `new_feature`
**Reviewing code?** → `code_review`
**Refactoring?** → `refactor_code`
**Designing API?** → `api_design`
**Planning tests?** → `testing_strategy`

### For DevOps / Cloud Teams

**Designing cloud architecture?** → `cloud_architecture`
**Production incident?** → `incident_response`
**Security audit?** → `security_audit`

### For Data Teams

**Building data pipeline?** → `data_pipeline`
**ML project?** → `ml_model_lifecycle`

### For Architects

**Database design?** → `database_schema`
**API ecosystem?** → `api_design`
**Cloud strategy?** → `cloud_architecture`

### For Everyone

**Writing documentation?** → `documentation`
**Security concerns?** → `security_audit`

## Template Performance

Each template is optimized for token efficiency:

| Template | Base Tokens | Per Decision | Total (Typical Run) |
|----------|-------------|--------------|-------------------|
| Code Review | 800 | 300 | 1,400 |
| API Design | 1,100 | 500 | 3,200 |
| Security Audit | 1,200 | 400 | 3,000 |
| Cloud Architecture | 1,100 | 600 | 4,200 |
| Data Pipeline | 1,100 | 500 | 3,500 |
| ML Lifecycle | 1,100 | 600 | 4,000 |
| Incident Response | 1,000 | 400 | 2,800 |

## Creating Custom Templates

See [`TEMPLATE_AUTHORING.md`](TEMPLATE_AUTHORING.md) for detailed guide to:
- Template YAML schema
- Writing effective node descriptions
- Setting appropriate token budgets
- Testing custom templates
- Contributing templates back to the project

## Template Maintenance

### Adding New Templates

1. Create new `.yaml` file in `ai-orchestrator/flow/templates/`
2. Follow YAML structure and naming conventions
3. Test in GUI
4. Update this documentation
5. Submit PR with template and docs

### Updating Existing Templates

1. Modify `.yaml` file
2. Update `description` if scope changed
3. Test changes in GUI
4. Update docs if significant changes
5. Bump version in metadata if breaking changes

## Contributing Templates

We welcome community-contributed templates! To contribute:

1. **Create your template** following [`TEMPLATE_AUTHORING.md`](TEMPLATE_AUTHORING.md)
2. **Test thoroughly** in both desktop and web GUIs
3. **Add documentation** covering:
   - When to use this template
   - Example use cases
   - Key decision points
4. **Submit PR** with template, tests, and documentation

### Template Contribution Ideas

- **DevOps & Infrastructure:** Kubernetes deployment, CI/CD pipeline design, monitoring setup
- **Product:** User research planning, feature prioritization, launch checklist
- **Business:** Market analysis, competitive analysis, business case development
- **Compliance:** Audit readiness, data governance, privacy implementation
- **QA:** Test planning, quality metrics, automation strategy

---

**Last updated:** 2026-02-22
**Total Templates:** 12
**Status:** Production ready
**Maintenance:** Monthly review and community feedback
