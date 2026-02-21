# Changelog

All notable changes to Symphony-IR are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Added

#### Governance & Community
- **Apache License 2.0** — Migrated from MIT for patent protection and strategic AI/ML positioning
- **Code of Conduct** — Contributor Covenant 2.1 for community standards
- **Security Policy** — Vulnerability reporting process with private disclosure
- **Contributing Guide** — Comprehensive guide for code contributors with setup, style, and PR process
- **Project Roadmap** — 6-month vision with v1.0→v1.1→v1.2+ roadmap

#### GitHub Integration
- **Issue Templates** — Bug report and feature request templates with clear structure
- **Pull Request Template** — PR checklist with testing and documentation requirements
- **GitHub Discussions** — Setup for Q&A and community engagement (manual enable required)

#### CI/CD & Quality
- **Dependency Security Workflow** — Weekly vulnerability scanning with `pip-audit` and license compliance checking
- **Test Suite Workflow** — Multi-platform (Windows/macOS/Linux) and multi-version (Python 3.10/3.11/3.12) testing
- **Code Quality Checks** — Black formatting, isort imports, Flake8 linting, mypy type checking
- **CI Documentation** — Comprehensive guide for CI/CD workflows and local testing

#### Documentation Reorganization
- **Centralized docs/ structure** — Modular documentation with clear hierarchy
- **User Guides** — CLI, GUI, Python API, and workflow templates documentation
- **Developer Guides** — Development setup, testing guide, and CI/CD documentation
- **Design System** — Moved to `docs/DESIGN/` with design tokens and component specs
- **Navigation Hub** — `docs/README.md` with role-based paths (User, Developer, Designer, Maintainer)
- **Learning Paths** — Beginner to Expert progression guides

### Changed

#### License
- Changed primary license from **MIT** to **Apache License 2.0**
- Apache 2.0 selected for:
  - Patent grant (critical for AI/ML products in 2026)
  - Permissive use (allows commercial derivatives)
  - Standard infrastructure positioning

#### Documentation
- Root README simplified with link to `docs/` hub
- All design documentation moved to `docs/DESIGN/`
- Architecture documentation moved to `docs/ARCHITECTURE.md`
- Created `docs/USAGE/` for user-focused guides
- Created `docs/DEVELOPMENT/` for contributor guides

### Security

- Added vulnerability reporting mechanism (SECURITY.md)
- Implemented automated dependency scanning with pip-audit
- Added license compliance checking
- Established security patch timeline (48-hour acknowledgment)
- Added Apache license headers to main entry points

### Infrastructure

- Added GitHub Actions workflow for dependency checking (weekly + PR)
- Added GitHub Actions workflow for multi-platform testing
- Added code quality checks (Black, isort, Flake8, mypy)
- Added documentation validation (markdown, broken links, YAML)
- Added Apache license header verification

---

## [1.0.0] - 2026-02-21

### Added

#### Core Features
- **Multi-agent Orchestration** — Architect, Implementer, and Reviewer agents
- **Deterministic Execution** — Reproducible workflow execution with cost tracking
- **Three User Interfaces** — Desktop GUI (PyQt6), CLI, and web (Streamlit)
- **Provider Support** — Claude, Ollama, OpenAI API integration
- **Secure Credentials** — System credential manager integration (Windows, macOS, Linux)

#### User Features
- **Desktop GUI** — Beautiful PyQt6 interface with design token system
- **CLI Interface** — Powerful command-line interface with setup wizard
- **Session History** — Persistent execution history with search and replay
- **Cost Tracking** — Token usage and estimated API cost monitoring
- **Enterprise Workflows** — 8 pre-built templates (code review, security audit, cloud architecture, etc.)

#### Enterprise Templates
- Code Review — Analyze code quality and style
- Security Audit — Identify security vulnerabilities
- Cloud Architecture — Design scalable systems
- Data Pipeline — Plan data workflows
- ML Model — Design machine learning solutions
- Incident Response — Handle security incidents
- Compliance Audit — Check regulatory compliance
- Performance Optimization — Improve system efficiency

#### Distribution
- **Windows Installer** — MSI installer with code signing
- **macOS Installer** — DMG bundle with app signing and notarization
- **Linux Installer** — AppImage with GPG signature
- **Code Signing** — Professional code signing infrastructure
- **PyInstaller Builds** — Cross-platform executable generation

#### Architecture & Design
- **Design Token System** — Unified design language (colors, typography, spacing)
- **Modular Architecture** — Separate CLI, GUI, and core orchestration layers
- **Error Handling** — Comprehensive error messages and recovery
- **Configuration Management** — Unified config across GUI and CLI
- **Context Management** — Multi-step context preservation across agents

### Documentation
- Getting Started Guide — 5-minute installation and first run
- Architecture Documentation — System design and components
- API Reference — Python library documentation
- CLI Reference — Command-line interface documentation
- Design System Documentation — UI/UX guidelines

### Testing & Quality
- Pytest test suite — Unit and integration tests
- Code coverage tracking — Coverage goals and metrics
- Style enforcement — Black, isort, Flake8 integration
- Type checking — mypy type annotations

---

## Versioning

Symphony-IR uses semantic versioning:

- **MAJOR** (1.x.y) — Breaking changes, major features
- **MINOR** (x.1.y) — New features, backward compatible
- **PATCH** (x.y.1) — Bug fixes, security patches

---

## Release Process

1. **Development** — Features and fixes on feature branches
2. **Testing** — All tests must pass on CI/CD
3. **Changelog** — Update CHANGELOG.md with new features
4. **Version Bump** — Update version in setup.py and pyproject.toml
5. **Release** — Tag with semantic version and create GitHub release
6. **Distribution** — Build and sign executables, publish to package managers

---

## Supported Versions

| Version | Status | Support Until |
|---------|--------|---------------|
| 1.1.x | In Development | TBD |
| 1.0.x | Current | 2026-12-31 |
| < 1.0 | End of Life | 2026-02-28 |

---

## Security Updates

Security patches are released as soon as possible:

- **Critical** — Released within 24 hours
- **High** — Released within 48 hours
- **Medium** — Released within 1 week
- **Low** — Released with next version

See [SECURITY.md](SECURITY.md) for vulnerability reporting.

---

## Contributors

Thank you to all contributors who have helped build Symphony-IR!

See [CONTRIBUTING.md](CONTRIBUTING.md) to get involved.

---

## Links

- [GitHub Repository](https://github.com/courtneybtaylor-sys/Symphony-IR)
- [Issue Tracker](https://github.com/courtneybtaylor-sys/Symphony-IR/issues)
- [Discussions](https://github.com/courtneybtaylor-sys/Symphony-IR/discussions)
- [License](LICENSE.txt)
- [Code of Conduct](.github/CODE_OF_CONDUCT.md)
- [Security Policy](SECURITY.md)
- [Project Roadmap](ROADMAP.md)
