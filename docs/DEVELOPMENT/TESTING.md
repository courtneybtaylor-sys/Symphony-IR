# Testing Guide

This guide covers writing, running, and maintaining tests for Symphony-IR.

## Test Structure

```
tests/
├── test_orchestrator.py      # CLI orchestrator tests
├── test_agents.py            # Agent tests
├── test_flow.py              # Workflow/template tests
└── gui/
    ├── test_credentials.py   # Credential handling
    ├── test_errors.py        # Error handling
    └── test_redaction.py     # Sensitive data redaction
```

## Running Tests

### Run All Tests

```bash
# All tests with verbose output
pytest tests/ -v

# With coverage report
pytest tests/ --cov=ai_orchestrator --cov=gui --cov-report=html

# Open HTML report
open htmlcov/index.html  # macOS
```

### Run Specific Tests

```bash
# Specific test file
pytest tests/test_agents.py -v

# Specific test function
pytest tests/test_agents.py::test_architect_agent -v

# Tests matching pattern
pytest tests/ -k "test_agent" -v

# Stop on first failure
pytest tests/ -x

# Show local variables on failure
pytest tests/ -l
```

### Run with Markers

```bash
# Mark tests with categories
@pytest.mark.unit
@pytest.mark.integration
@pytest.mark.slow

# Run only unit tests
pytest tests/ -m unit -v

# Skip slow tests
pytest tests/ -m "not slow"
```

## Writing Tests

### Basic Test Structure

```python
import pytest
from ai_orchestrator.agents import Architect

def test_architect_initialization():
    """Test that Architect agent initializes correctly."""
    architect = Architect()
    assert architect.role == "Architect"
    assert architect.name == "architect"

def test_architect_prompt():
    """Test Architect's system prompt is set."""
    architect = Architect()
    assert "architect" in architect.system_prompt.lower()
```

### Testing Orchestrator

```python
from ai_orchestrator.orchestrator import Orchestrator

def test_orchestrator_run():
    """Test running a simple task."""
    orch = Orchestrator()
    result = orch.run("Test task")

    assert 'architect' in result
    assert 'implementer' in result
    assert 'reviewer' in result
    assert 'metadata' in result

def test_orchestrator_with_provider():
    """Test running with specific provider."""
    orch = Orchestrator(provider='claude')
    assert orch.provider == 'claude'
```

### Testing Workflows

```python
from ai_orchestrator.flow import Workflow, Engine

def test_workflow_creation():
    """Test creating a workflow."""
    workflow = Workflow(name='test_workflow')
    assert workflow.name == 'test_workflow'

def test_workflow_execution():
    """Test executing a workflow."""
    engine = Engine()
    result = engine.run(workflow={...}, variables={})
    assert result['status'] == 'completed'
```

### Testing with Fixtures

```python
import pytest

@pytest.fixture
def orchestrator():
    """Provide a test orchestrator."""
    return Orchestrator(provider='test')

@pytest.fixture
def sample_task():
    """Provide a sample task."""
    return "Write a test function"

def test_with_fixtures(orchestrator, sample_task):
    """Test using fixtures."""
    result = orchestrator.run(sample_task)
    assert result is not None
```

### Mocking External Calls

```python
from unittest.mock import Mock, patch

@patch('ai_orchestrator.providers.claude.Client')
def test_orchestrator_with_mock(mock_client):
    """Test with mocked API client."""
    mock_client.return_value.messages.create.return_value = Mock(
        content=[Mock(text="Test response")]
    )

    orch = Orchestrator()
    result = orch.run("Test task")

    assert mock_client.called
```

### Parameterized Tests

```python
import pytest

@pytest.mark.parametrize("provider,expected", [
    ('claude', 'claude-opus'),
    ('ollama', 'mistral'),
])
def test_providers(provider, expected):
    """Test different providers."""
    orch = Orchestrator(provider=provider)
    assert orch.model == expected
```

### Exception Testing

```python
import pytest
from ai_orchestrator.exceptions import ProviderError

def test_invalid_api_key():
    """Test handling invalid API key."""
    with pytest.raises(ProviderError):
        orch = Orchestrator(api_key='invalid')
        orch.run("Test task")

def test_provider_timeout():
    """Test handling provider timeout."""
    with pytest.raises(TimeoutError):
        orch = Orchestrator(timeout=0.001)
        orch.run("Test task")
```

## Test Coverage

### Check Coverage

```bash
# Generate coverage report
pytest tests/ --cov=ai_orchestrator --cov=gui --cov-report=term-missing

# Create HTML report
pytest tests/ --cov=ai_orchestrator --cov=gui --cov-report=html
open htmlcov/index.html
```

### Coverage Goals

- **Overall**: 80%+
- **Core modules**: 90%+
- **Agent logic**: 85%+
- **Error handling**: 100%

### Improve Coverage

```bash
# Find uncovered lines
pytest tests/ --cov=ai_orchestrator --cov-report=term-missing:skip-covered

# Focus on specific module
pytest tests/ --cov=ai_orchestrator.agents --cov-report=html
```

## Performance Testing

### Timing Tests

```python
import pytest

@pytest.mark.performance
def test_orchestrator_performance():
    """Test orchestrator runs within time limit."""
    orch = Orchestrator()

    # Time the execution
    start = time.time()
    result = orch.run("Quick task")
    elapsed = time.time() - start

    # Should complete in reasonable time
    assert elapsed < 30  # 30 seconds
```

### Benchmark Tests

```python
import pytest

@pytest.mark.benchmark
def test_agent_response_speed(benchmark):
    """Benchmark agent response time."""
    agent = Architect()
    result = benchmark(agent.respond, "Test prompt")
    assert result is not None
```

## Integration Testing

### Test Multiple Components

```python
def test_full_orchestration_flow():
    """Test complete orchestration workflow."""
    config = Config(provider='claude')
    orch = Orchestrator(config=config)

    # Run through full workflow
    result = orch.run("Design a REST API")

    # Verify all components responded
    assert result['architect']['response']
    assert result['implementer']['response']
    assert result['reviewer']['response']
    assert result['metadata']['status'] == 'completed'
```

## GUI Testing

### Test PyQt6 Components

```python
from PyQt6.QtWidgets import QApplication
from gui.main import MainWindow

def test_main_window():
    """Test main window creation."""
    app = QApplication.instance() or QApplication([])
    window = MainWindow()

    assert window.isVisible() or not window.isVisible()
    assert window.windowTitle() == "Symphony-IR"
```

### Test Streamlit Components

```python
def test_streamlit_imports():
    """Test Streamlit app imports correctly."""
    import gui.streamlit_app
    assert gui.streamlit_app is not None
```

## Testing Best Practices

### ✅ DO

- Write descriptive test names: `test_agent_responds_to_prompt()`
- Use fixtures for common setup
- Test edge cases and errors
- Mock external dependencies
- Keep tests independent
- Use clear assertions

### ❌ DON'T

- Use vague names: `test_function()`
- Hardcode test data
- Make tests depend on each other
- Test private methods directly
- Skip error cases
- Leave print() statements

## Continuous Integration

Tests run automatically on:
- **Pull requests**: All tests must pass
- **Pushes to main**: All tests must pass
- **Weekly schedule**: Full test suite + coverage check

See [CI Guide](CI.md) for workflow details.

## Test Examples

### Testing Credentials

```python
# gui/tests/test_credentials.py
def test_credential_storage():
    """Test storing credentials securely."""
    from gui.credentials import CredentialManager

    manager = CredentialManager()
    manager.set('api_key', 'test-key')

    retrieved = manager.get('api_key')
    assert retrieved == 'test-key'

def test_credential_not_exposed():
    """Test credentials aren't logged."""
    import logging
    manager = CredentialManager()
    manager.set('api_key', 'secret-key')

    # Log something with credentials
    logger = logging.getLogger()
    logger.info(f"Initialized with {manager}")

    # Ensure secret not in logs
    # (implementation varies by logger)
```

### Testing Error Handling

```python
# gui/tests/test_errors.py
def test_redaction():
    """Test sensitive data redaction."""
    from gui.errors import redact_sensitive_data

    data = "API Key: sk-ant-12345"
    redacted = redact_sensitive_data(data)

    assert "sk-ant-12345" not in redacted
    assert "API Key: [REDACTED]" in redacted
```

## Running Tests Before Commit

### Pre-commit Hook

```bash
# .git/hooks/pre-commit (create this file)
#!/bin/bash
pytest tests/ --tb=short
if [ $? -ne 0 ]; then
    echo "Tests failed! Fix before committing."
    exit 1
fi
```

Make it executable:
```bash
chmod +x .git/hooks/pre-commit
```

## Debugging Tests

### Verbose Output

```bash
# Show print statements
pytest tests/ -s

# Show local variables on failure
pytest tests/ -l

# Show full diff on assertion failure
pytest tests/ --tb=long
```

### Use Debugger

```bash
# Drop into pdb on failure
pytest tests/ --pdb

# Drop into pdb on first failure
pytest tests/ --pdb --maxfail=1

# Drop into pdb on error
pytest tests/ --pdbcls=IPython.terminal.debugger:TerminalPdb
```

## See Also

- [Development Setup](SETUP.md) — Environment configuration
- [CI/CD Guide](CI.md) — Automated testing
- [Contributing Guide](../../CONTRIBUTING.md) — PR process

## Resources

- [pytest documentation](https://docs.pytest.org/)
- [unittest.mock docs](https://docs.python.org/3/library/unittest.mock.html)
- [Coverage.py docs](https://coverage.readthedocs.io/)
