# Contributing to Symphony-IR

Thank you for your interest in contributing to Symphony-IR! We welcome contributions from everyone—whether you're fixing bugs, adding features, improving documentation, or sharing templates.

## 📋 Code of Conduct

Please review our [Code of Conduct](/.github/CODE_OF_CONDUCT.md) before participating. We're committed to providing a welcoming, inclusive community.

## 🚀 Getting Started

### 1. Fork & Clone

```bash
# Fork the repository on GitHub
# Clone your fork
git clone https://github.com/YOUR_USERNAME/Symphony-IR.git
cd Symphony-IR

# Add upstream remote
git remote add upstream https://github.com/courtneybtaylor-sys/Symphony-IR.git
```

### 2. Set Up Development Environment

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install development dependencies
pip install -r ai-orchestrator/requirements.txt
pip install -r gui/requirements.txt
pip install pytest pytest-cov  # for testing
```

### 3. Create a Branch

```bash
# Update main branch
git checkout main
git pull upstream main

# Create feature branch
git checkout -b feature/my-feature
# or for bug fixes:
git checkout -b fix/my-bug-fix
```

## 💻 Development Guidelines

### Code Style

- **Python**: Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/)
- **Line Length**: 100 characters max
- **Type Hints**: Use for public APIs (optional for internal code)
- **Docstrings**: Include for functions and classes

Example:

```python
def orchestrate_task(task: str, provider: str = "claude") -> Dict[str, Any]:
    """Execute a task through the orchestrator.

    Args:
        task: The task description
        provider: AI provider ("claude", "ollama", or "openai")

    Returns:
        Dictionary with results and metadata
    """
```

### License Headers

All new Python files must include the Apache 2.0 license header:

```python
# Copyright 2024 Kheper LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Your module description here."""
```

### Testing

All code contributions should include tests:

```bash
# Run tests locally
pytest tests/ --cov=. --cov-report=html

# Check coverage
open htmlcov/index.html
```

### Documentation

If your change affects users, please update:

- Docstrings in code
- Relevant docs in `docs/` directory
- `CHANGELOG.md` (if applicable)
- `README.md` (for major features)

## 🔄 Contribution Types

### Bug Fixes

1. Open an issue (if one doesn't exist) describing the bug
2. Create a branch: `git checkout -b fix/issue-123`
3. Fix the bug with tests
4. Submit a PR referencing the issue

### Features

1. Discuss in [GitHub Discussions](https://github.com/courtneybtaylor-sys/Symphony-IR/discussions) or [Issues](https://github.com/courtneybtaylor-sys/Symphony-IR/issues) first
2. Create a branch: `git checkout -b feature/my-feature`
3. Implement with tests and documentation
4. Submit a PR with clear description of use cases

### Templates & Workflows

1. Create a new template in `ai-orchestrator/flow/templates/`
2. Use consistent YAML structure
3. Include metadata (domain, difficulty, estimated_duration)
4. Add example usage in comments
5. Test with `python orchestrator.py flow <template_name>`

Example:

```yaml
# ai-orchestrator/flow/templates/my_template.yaml
name: "My Custom Workflow"
version: "1.0"
description: "Description of what this workflow does"
domain: "security"  # or "cloud", "data", "ml", etc.
difficulty: "intermediate"
estimated_duration: "10-15 minutes"
tags: ["audit", "compliance"]

agents:
  architect:
    prompt: "You are the architect..."
  implementer:
    prompt: "You are the implementer..."
  reviewer:
    prompt: "You are the reviewer..."

workflow:
  - step: 1
    agent: architect
    task: "Define the approach..."
```

### Documentation

- Fix typos and improve clarity
- Add examples and use cases
- Update API reference
- Improve architecture docs

## 📝 Pull Request Process

1. **Update from upstream:**
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

2. **Commit with clear messages:**
   ```bash
   git commit -m "fix: resolve authentication issue in CLI setup wizard (#123)"
   ```

   Use commit prefixes:
   - `feat:` — New feature
   - `fix:` — Bug fix
   - `docs:` — Documentation
   - `refactor:` — Code reorganization
   - `test:` — Test additions
   - `chore:` — Build, dependencies, etc.

3. **Push to your fork:**
   ```bash
   git push origin feature/my-feature
   ```

4. **Open a PR** with a clear description:
   - What problem does this solve?
   - How does it work?
   - Testing steps
   - Screenshots (if UI-related)

5. **Address review feedback** with new commits (don't force-push)

6. **Merge**: Repository maintainers will merge once approved

## ✅ Review Checklist

Before submitting, ensure:

- [ ] Code follows PEP 8 style guide
- [ ] All tests pass: `pytest tests/`
- [ ] New tests added for new features
- [ ] Documentation updated
- [ ] Apache license header on new files
- [ ] No hardcoded secrets or API keys
- [ ] Commit messages are clear and descriptive
- [ ] PR description explains the "why" not just the "what"

## 🔐 Security

**Please do not** open public issues for security vulnerabilities. See [SECURITY.md](SECURITY.md) for private reporting process.

## 📄 Licensing

By contributing to Symphony-IR, you agree that your contributions will be licensed under the Apache License 2.0. For substantial contributions from organizations, we may request a signed Contributor License Agreement (CLA).

## 🤝 Corporate Contributors

If you're contributing on behalf of an organization, please note:

- All code must be original or properly licensed
- No proprietary/confidential code
- Employer has approved the contribution
- For significant contributions, we may request a CLA

We'll notify you if a CLA is needed.

## 📚 Additional Resources

- [Architecture Guide](docs/ARCHITECTURE.md)
- [Design System](DESIGN_SYSTEM.md)
- [API Reference](docs/API.md)
- [CLI Documentation](docs/CLI.md)
- [Workflow Templates Guide](docs/FLOW.md)

## 🆘 Getting Help

- **Questions**: Ask in [GitHub Discussions](https://github.com/courtneybtaylor-sys/Symphony-IR/discussions)
- **Issues**: Search existing [GitHub Issues](https://github.com/courtneybtaylor-sys/Symphony-IR/issues)
- **Email**: contact@symphonyir.dev

## 🎉 Recognition

We'll recognize contributors in:

- Release notes (for significant contributions)
- Contributors list in README
- Community highlights in discussions

Thank you for helping make Symphony-IR better!

---

**Happy contributing!** 🚀
