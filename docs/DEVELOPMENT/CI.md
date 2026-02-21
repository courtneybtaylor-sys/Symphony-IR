# Continuous Integration (CI/CD)

Symphony-IR uses GitHub Actions to automatically test, audit, and validate code changes. This guide explains the CI workflows and how to work with them.

## Overview

Our CI/CD pipeline ensures:

✅ **Security**: Dependency vulnerability scanning
✅ **Quality**: Multi-platform, multi-version testing
✅ **Compliance**: License audits and code style checks
✅ **Reliability**: Automated validation before merge

## Workflows

### 1. Dependency Security Check (`dependency-check.yml`)

**Schedule**: Weekly (Mondays 09:00 UTC) + on pull requests with requirements changes

**What it does:**

- Scans `requirements.txt` files with `pip-audit`
- Checks for known vulnerabilities in dependencies
- Verifies license compliance
- Comments on PRs with audit results

**When you'll see it:**

- Every Monday at 09:00 UTC (scheduled run)
- When you modify `**/requirements.txt` (PR trigger)
- When you modify the workflow file itself

**What to do if it fails:**

1. Review the audit report in the GitHub Actions logs
2. Check which packages have known vulnerabilities
3. Update vulnerable packages: `pip install --upgrade package_name`
4. Run locally: `pip-audit`
5. Commit the updated `requirements.txt`
6. Create a pull request

### 2. Test Suite (`tests.yml`)

**Triggers:**

- On push to `main` and `claude/*` branches
- On pull requests to `main`
- Manual trigger via `workflow_dispatch`

**What it does:**

- Tests on **3 operating systems**: Ubuntu, macOS, Windows
- Tests on **3 Python versions**: 3.10, 3.11, 3.12
- Validates core imports
- Runs design token generation checks
- Validates CLI help text
- Runs pytest suite (if tests exist)

**Jobs:**

#### Test Python

```
matrix:
  os: [ubuntu-latest, macos-latest, windows-latest]
  python-version: [3.10, 3.11, 3.12]
```

Runs 9 parallel test jobs (3×3 matrix).

**What to do if it fails:**

1. Check which OS/Python version failed
2. Reproduce locally:
   ```bash
   python -m venv test-env
   source test-env/bin/activate
   python -m pip install -r requirements.txt
   pytest tests/ -v
   ```
3. Fix the issue and push again

#### Code Quality Check

Uses these tools:

- **Black**: Code formatting
- **isort**: Import sorting
- **Flake8**: Style linting
- **mypy**: Type checking

**What to do if it fails:**

- Black: `black ai-orchestrator/ gui/ windows/`
- isort: `isort ai-orchestrator/ gui/ windows/`
- Flake8: Review output and fix violations
- mypy: Add type hints to problematic lines

#### Documentation Validation

- Checks markdown syntax
- Looks for broken internal links
- Validates that files referenced exist

#### Build Validation

- Compiles Python files for syntax errors
- Validates YAML templates
- Checks Apache license headers

## Local Testing

### Run Tests Locally

```bash
# Set up environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install dependencies
pip install -r ai-orchestrator/requirements.txt
pip install -r gui/requirements.txt
pip install pytest pytest-cov

# Run tests
pytest tests/ -v --cov=ai_orchestrator --cov=gui
```

### Run Linting

```bash
pip install black isort flake8 mypy

# Format with Black
black ai-orchestrator/ gui/ windows/

# Sort imports
isort ai-orchestrator/ gui/

# Check style
flake8 ai-orchestrator/ gui/

# Type check
mypy ai-orchestrator/
```

### Run Dependency Audit

```bash
pip install pip-audit pip-licenses

# Check for vulnerabilities
pip-audit

# Check licenses
pip-licenses --format=markdown
```

## Common Issues & Solutions

### Issue: Tests fail on Windows but pass on Ubuntu

**Cause**: Path separators or line endings

**Solution**:
- Use `os.path.join()` instead of hardcoded `/`
- Set git to handle line endings: `git config core.autocrlf true`

### Issue: `ModuleNotFoundError` in tests

**Cause**: Missing dependencies or incorrect Python path

**Solution**:
```bash
pip install -e .
```

### Issue: Black reformats code unexpectedly

**Cause**: Different Black version or config

**Solution**:
```bash
pip install --upgrade black
black --version  # Should match workflow
```

### Issue: Dependency vulnerability reported but package is outdated

**Cause**: Newer package has same vulnerability, or pip-audit data is outdated

**Solution**:
1. Check if there's a newer version: `pip index versions package_name`
2. Check the vulnerability details: `pip-audit --desc`
3. If unavoidable, open an issue for tracking

## Branch Protection Rules

The `main` branch requires:

✅ Passing CI checks (all workflows must succeed)
✅ Code review (1 approval minimum)
✅ No unresolved conversations
✅ Branches must be up to date before merge

## Making CI Changes

### Add a New Workflow

1. Create `.github/workflows/new-workflow.yml`
2. Define triggers and jobs
3. Test locally if possible
4. Push as a feature branch
5. CI will test the workflow itself

### Modify Existing Workflow

1. Edit the workflow file
2. Test changes in a feature branch
3. Once approved, merge to `main`
4. The workflow takes effect immediately

### Disable a Check Temporarily

If a check is blocking merges:

1. **Option A**: Disable the job (comment out the job)
2. **Option B**: Make checks non-blocking (continue-on-error: true)
3. **Option C**: File an issue and fix the underlying problem

## Performance

**Workflow runtime targets:**

- Dependency check: < 5 minutes
- Test suite: < 15 minutes (parallel)
- Code quality: < 5 minutes
- Documentation: < 2 minutes

If workflows exceed these times, consider:
- Reducing matrix dimensions (fewer Python versions)
- Caching pip dependencies
- Running some checks only on PR, not every push

## Debugging Workflows

### View Logs

1. Go to GitHub: Actions → Select Workflow → Click Run
2. Click "Job Name" to expand logs
3. Use `GITHUB_TOKEN` and `ACTIONS_STEP_DEBUG` for more details

### Test Workflow Locally

Use [act](https://github.com/nektos/act):

```bash
# Install act
brew install act  # macOS
# or download from https://github.com/nektos/act

# Run workflow locally
act --job test-python
```

### Debug Job Step

Add a debug step:

```yaml
- name: Debug Info
  run: |
    echo "Python version:"
    python --version
    echo "Installed packages:"
    pip list | grep -E "pytest|black|flake8"
```

## Best Practices

1. **Keep workflows simple**: Complex CI is hard to debug
2. **Cache dependencies**: Use `setup-python` with `cache: pip`
3. **Document failures**: Leave clear error messages
4. **Test locally first**: Run workflows before pushing
5. **Monitor workflow time**: Aim for < 20 minutes total
6. **Use continue-on-error sparingly**: Only for non-critical checks

## References

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Workflow Syntax](https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions)
- [pip-audit](https://github.com/pypa/pip-audit)
- [pytest Documentation](https://docs.pytest.org/)
- [Black Code Formatter](https://black.readthedocs.io/)

## Getting Help

- Check workflow logs: GitHub → Actions → Select workflow
- Ask in [GitHub Discussions](https://github.com/courtneybtaylor-sys/Symphony-IR/discussions)
- Report issues: [GitHub Issues](https://github.com/courtneybtaylor-sys/Symphony-IR/issues)
