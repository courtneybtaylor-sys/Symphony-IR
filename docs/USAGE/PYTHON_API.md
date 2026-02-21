# Python API Guide

Use Symphony-IR as a Python library to integrate multi-agent orchestration into your applications.

## Installation

```bash
pip install -r ai-orchestrator/requirements.txt
```

## Quick Start

```python
from ai_orchestrator.orchestrator import Orchestrator

# Initialize
orchestrator = Orchestrator()

# Run a simple task
result = orchestrator.run("Write a Python function that validates email addresses")

# Access results
architect_response = result['architect']
implementer_response = result['implementer']
reviewer_response = result['reviewer']

print(architect_response)
print(implementer_response)
print(reviewer_response)
```

## Basic Usage

### Run a Task

```python
from ai_orchestrator.orchestrator import Orchestrator

orchestrator = Orchestrator(provider='claude')

# Simple task
result = orchestrator.run(
    task="Design a REST API for a blog platform",
    provider='claude'
)
```

### Run a Workflow

```python
# Run a pre-built workflow
result = orchestrator.flow(
    template='code_review',
    variables={'component': 'src/auth.py'}
)
```

### Get Results

```python
# Access orchestration results
print(result['architect'])      # Architect's analysis
print(result['implementer'])    # Implementation details
print(result['reviewer'])       # Review feedback
print(result['metadata'])       # Execution metadata
```

### Result Structure

```python
{
    'architect': {
        'response': str,      # Architect's response
        'tokens': int,        # Tokens used
        'cost': float         # Estimated cost
    },
    'implementer': {
        'response': str,
        'tokens': int,
        'cost': float
    },
    'reviewer': {
        'response': str,
        'tokens': int,
        'cost': float
    },
    'metadata': {
        'task': str,
        'provider': str,
        'execution_time': float,
        'total_tokens': int,
        'total_cost': float,
        'status': str          # 'completed' or 'failed'
    }
}
```

## Configuration

### From Code

```python
from ai_orchestrator.config import Config

config = Config(
    provider='claude',
    claude_api_key='sk-ant-...',
    model='claude-opus'
)

orchestrator = Orchestrator(config=config)
```

### From Environment

```python
import os

os.environ['ANTHROPIC_API_KEY'] = 'sk-ant-...'
os.environ['SYMPHONY_PROVIDER'] = 'claude'

orchestrator = Orchestrator()
```

### From Config File

```python
from ai_orchestrator.config import Config

config = Config.from_file('~/.symphonyir/config.json')
orchestrator = Orchestrator(config=config)
```

## Advanced Usage

### Custom Agents

```python
from ai_orchestrator.agents import Agent

# Define custom agent
analyst = Agent(
    name='Analyst',
    role='Data analyst',
    system_prompt='You are an expert data analyst...'
)

# Use in orchestration
result = orchestrator.run(
    task='Analyze this dataset',
    agents=[analyst]
)
```

### Custom Workflow

```python
from ai_orchestrator.flow import Workflow

workflow = Workflow(name='custom_analysis')
workflow.add_step(agent='architect', task='Analyze requirements')
workflow.add_step(agent='implementer', task='Propose solution')
workflow.add_step(agent='reviewer', task='Review and critique')

result = orchestrator.flow(workflow=workflow, variables={})
```

### Streaming Results

```python
# Stream results as they arrive
for chunk in orchestrator.run_stream(
    task='Generate documentation'
):
    print(chunk, end='', flush=True)
```

### Batch Processing

```python
import asyncio

async def process_batch():
    tasks = [
        'Task 1',
        'Task 2',
        'Task 3'
    ]

    results = await orchestrator.run_batch(tasks)
    return results

# Run async
results = asyncio.run(process_batch())
```

### Cost Tracking

```python
# Get cost estimate before running
estimate = orchestrator.estimate_cost(
    task='Your task here'
)
print(f"Estimated cost: ${estimate['total_cost']}")

# Or track after running
result = orchestrator.run('Your task')
print(f"Actual cost: ${result['metadata']['total_cost']}")
```

## Providers

### Claude (Anthropic)

```python
orchestrator = Orchestrator(provider='claude')

# Custom model
orchestrator = Orchestrator(
    provider='claude',
    model='claude-opus'  # or 'claude-sonnet', 'claude-haiku'
)
```

### Ollama (Local)

```python
orchestrator = Orchestrator(provider='ollama')

# Custom URL and model
orchestrator = Orchestrator(
    provider='ollama',
    ollama_url='http://localhost:11434',
    model='mistral'
)
```

### OpenAI

```python
orchestrator = Orchestrator(provider='openai')

# Custom model
orchestrator = Orchestrator(
    provider='openai',
    openai_api_key='sk-...',
    model='gpt-4'
)
```

## Integration Examples

### Flask Integration

```python
from flask import Flask, request, jsonify
from ai_orchestrator.orchestrator import Orchestrator

app = Flask(__name__)
orchestrator = Orchestrator()

@app.route('/analyze', methods=['POST'])
def analyze():
    task = request.json.get('task')
    result = orchestrator.run(task)
    return jsonify(result)

if __name__ == '__main__':
    app.run()
```

### FastAPI Integration

```python
from fastapi import FastAPI
from ai_orchestrator.orchestrator import Orchestrator

app = FastAPI()
orchestrator = Orchestrator()

@app.post('/analyze")
async def analyze(task: str):
    result = orchestrator.run(task)
    return result
```

### Django Integration

```python
from django.http import JsonResponse
from django.views import View
from ai_orchestrator.orchestrator import Orchestrator

class AnalyzeView(View):
    def __init__(self):
        self.orchestrator = Orchestrator()

    def post(self, request):
        task = request.POST.get('task')
        result = self.orchestrator.run(task)
        return JsonResponse(result)
```

## Error Handling

```python
from ai_orchestrator.exceptions import (
    OrchestratorError,
    ProviderError,
    ConfigError
)

try:
    result = orchestrator.run('Your task')
except ProviderError as e:
    print(f"Provider error: {e}")
except ConfigError as e:
    print(f"Configuration error: {e}")
except OrchestratorError as e:
    print(f"Orchestration error: {e}")
```

## Testing

```python
import unittest
from ai_orchestrator.orchestrator import Orchestrator
from ai_orchestrator.testing import MockProvider

class TestOrchestration(unittest.TestCase):
    def setUp(self):
        self.orchestrator = Orchestrator(
            provider=MockProvider()  # Use mock for testing
        )

    def test_simple_task(self):
        result = self.orchestrator.run('Test task')
        self.assertIn('architect', result)
        self.assertIn('implementer', result)
        self.assertIn('reviewer', result)
```

## Performance

### Caching

```python
# Enable response caching
orchestrator.enable_cache()

# Results are cached for identical tasks
result1 = orchestrator.run('Task')
result2 = orchestrator.run('Task')  # Returns cached result

# Clear cache
orchestrator.clear_cache()
```

### Concurrency

```python
import concurrent.futures

tasks = ['Task 1', 'Task 2', 'Task 3']

with concurrent.futures.ThreadPoolExecutor() as executor:
    results = list(executor.map(orchestrator.run, tasks))
```

## See Also

- [CLI Guide](CLI.md) — Command-line interface
- [GUI Guide](GUI.md) — Desktop application
- [Architecture](../ARCHITECTURE.md) — How it works
- [Contributing](../../CONTRIBUTING.md) — Extend Symphony-IR

## API Reference

For detailed API documentation, see:
- `ai-orchestrator/README.md` — Module reference
- `ai-orchestrator/orchestrator.py` — Main class
- `ai-orchestrator/agents/` — Agent implementations
- `ai-orchestrator/flow/` — Workflow system

## Examples

Check the `ai-orchestrator/` directory for:
- `example.py` — Comprehensive examples
- `QUICKSTART.md` — Quick reference
- Test files in `tests/` — Usage patterns
