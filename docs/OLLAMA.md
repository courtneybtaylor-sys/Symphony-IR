# Symphony-IR with Ollama - Local AI Models (No API Key Required)

Use Symphony-IR with fully local AI models via Ollama. No API keys, no cloud dependencies, no token costs.

## Quick Start

### 1. Install Ollama

Download and install from [ollama.ai](https://ollama.ai):

```bash
# macOS
brew install ollama

# Linux
curl -fsSL https://ollama.ai/install.sh | sh

# Windows
# Download installer from https://ollama.ai
```

### 2. Download a Model

```bash
# Start Ollama daemon first (automatically in background or via 'ollama serve')
ollama pull llama2       # Default: 7B model, ~4GB
ollama pull mistral      # Faster, smaller: 7B model, ~5GB
ollama pull neural-chat  # Conversational: 7B model, ~5GB
ollama pull dolphin-mixtral  # Most capable: 8x7B model, ~45GB (requires 24GB+ VRAM)
```

### 3. Start Ollama Server

Ollama runs on `localhost:11434` by default:

```bash
ollama serve
```

The server runs in the background. You'll see:
```
time=2024-02-20T10:30:45.123Z level=info msg="Listening on 127.0.0.1:11434"
```

### 4. Use with Symphony-IR

**Option A: Use Pre-Built Config**

```bash
cd ai-orchestrator

# Copy one of the provided configs
cp config/agents-ollama.yaml ../.orchestrator/agents.yaml
# or
cp config/agents-ollama-capable.yaml ../.orchestrator/agents.yaml
# or
cp config/agents-ollama-powerful.yaml ../.orchestrator/agents.yaml
```

**Option B: Use Environment Variable**

```bash
export OLLAMA_BASE_URL=http://localhost:11434

# Then use normally
python orchestrator.py run "Your task here"
python orchestrator.py flow --template code_review --var component=myfile.py
```

**Option C: Edit Your Config**

Edit `.orchestrator/agents.yaml` and change all `anthropic` providers to `ollama`:

```yaml
agents:
  - name: architect
    role: System Architect
    model_provider: ollama        # Changed from: anthropic
    model_config:
      model: llama2              # Your chosen model
      base_url: http://localhost:11434
    temperature: 0.7
    max_tokens: 2000
    system_prompt: |
      ...
```

### 5. Run Your First Flow

```bash
python orchestrator.py flow-list
python orchestrator.py flow --template code_review --var component=src/auth.py
```

## Available Models

### Lightweight Models (4-7GB, 7B params, Fast)

| Model | Size | Speed | Quality | Command |
|-------|------|-------|---------|---------|
| llama2 | 4GB | Fast | Good | `ollama pull llama2` |
| mistral | 5GB | Fast | Better | `ollama pull mistral` |
| neural-chat | 5GB | Fast | Conversational | `ollama pull neural-chat` |

**Use case**: Quick iterations, testing, resource-constrained machines

### Medium Models (7-20GB, 13B-30B params, Better)

| Model | Size | Speed | Quality | Command |
|-------|------|-------|---------|---------|
| llama2-13b | 8GB | Medium | Better | `ollama pull llama2:13b` |
| mistral-medium | 10GB | Medium | Good | Via custom |
| neural-chat-7b | 5GB | Fast | Good | `ollama pull neural-chat:7b` |

### Powerful Models (20GB+, Mixture of Experts, Best)

| Model | Size | Speed | Quality | Command | Notes |
|-------|------|-------|---------|---------|-------|
| dolphin-mixtral | 45GB | Medium | Excellent | `ollama pull dolphin-mixtral` | 8x7B MoE, most capable open model |
| neural-chat | Variable | Medium | Very Good | `ollama pull neural-chat` | Optimized for conversations |

**Use case**: Production workflows, complex reasoning

### Model Selection Guide

```
Speed (fast → slow):           mistral > llama2 > neural-chat > dolphin-mixtral
Quality (good → excellent):    llama2 < mistral < neural-chat < dolphin-mixtral
VRAM (GB):                     llama2(4) < mistral(5) < neural-chat(7) < dolphin-mixtral(24)
Conversational:                ★ neural-chat, ★★ mistral, ★★★ dolphin-mixtral
Code generation:               ★★ llama2, ★★★ mistral, ★★★★ dolphin-mixtral
Reasoning:                     ★★ llama2, ★★★ neural-chat, ★★★★ dolphin-mixtral
```

## Configuration Examples

### Config 1: Lightweight (Fast, Low VRAM)

```yaml
agents-ollama.yaml
model: llama2
base_url: http://localhost:11434

# Best for:
# - 4GB+ VRAM
# - Quick iterations
# - Testing and demos
```

Copy and use:

```bash
cp ai-orchestrator/config/agents-ollama.yaml .orchestrator/agents.yaml
ollama pull llama2
ollama serve &
python orchestrator.py run "Your task"
```

### Config 2: Balanced (Fast & Capable)

```yaml
agents-ollama-capable.yaml
model: mistral
base_url: http://localhost:11434

# Best for:
# - 8GB+ VRAM
# - Production workflows
# - Good quality + speed balance
```

Copy and use:

```bash
cp ai-orchestrator/config/agents-ollama-capable.yaml .orchestrator/agents.yaml
ollama pull mistral
ollama serve &
python orchestrator.py run "Your task"
```

### Config 3: Maximum Quality (Most Capable)

```yaml
agents-ollama-powerful.yaml
model: dolphin-mixtral
base_url: http://localhost:11434

# Best for:
# - 24GB+ VRAM
# - Complex reasoning
# - Production critical tasks
```

Copy and use:

```bash
cp ai-orchestrator/config/agents-ollama-powerful.yaml .orchestrator/agents.yaml
ollama pull dolphin-mixtral
ollama serve &
python orchestrator.py run "Your task"
```

## Using with Symphony Flow

### Example 1: Code Review with Local Model

```bash
# Start Ollama
ollama serve &

# Copy config
cp ai-orchestrator/config/agents-ollama.yaml .orchestrator/agents.yaml

# Run flow
python orchestrator.py flow --template code_review --var component=src/auth.py

# Interactive choices:
# ✓ Starting code review
# What's next?
#   A) Focus on bugs
#   B) Focus on style
#   C) Focus on performance
# Choice: A
#
# ⚙️  Executing via Symphony-IR with local llama2...
# ✓ Execution complete
```

### Example 2: API Design with Mistral

```bash
cp ai-orchestrator/config/agents-ollama-capable.yaml .orchestrator/agents.yaml
python orchestrator.py flow --template api_design --var api_name="user-service"
```

### Example 3: Test Strategy with Dolphin-Mixtral

```bash
cp ai-orchestrator/config/agents-ollama-powerful.yaml .orchestrator/agents.yaml
python orchestrator.py flow --template testing_strategy --var component_name="payment"
```

## Environment Variables

### Setting Ollama Base URL

```bash
# Default (localhost:11434)
export OLLAMA_BASE_URL=http://localhost:11434

# Custom host
export OLLAMA_BASE_URL=http://192.168.1.100:11434

# Check variable works
echo $OLLAMA_BASE_URL
```

**Note:** The YAML configs use `${OLLAMA_BASE_URL:-http://localhost:11434}`, meaning:
- If `OLLAMA_BASE_URL` is set → use it
- If not set → default to `http://localhost:11434`

### Verify Connection

```python
python -c "
from models.client import OllamaClient
client = OllamaClient(model='llama2', base_url='http://localhost:11434')
from models.client import Message
response = client.call([Message('user', 'Hello')])
print(f'✓ Connected to Ollama: {response.model}')
"
```

## Complete Setup Script

Save as `setup-ollama.sh`:

```bash
#!/bin/bash
set -e

echo "🚀 Setting up Symphony-IR with Ollama..."

# 1. Check if Ollama is installed
if ! command -v ollama &> /dev/null; then
    echo "❌ Ollama not found. Install from https://ollama.ai"
    exit 1
fi

# 2. Select model
echo ""
echo "Which model would you like to use?"
echo "1) llama2 (4GB, fast, good) - RECOMMENDED"
echo "2) mistral (5GB, fast, better)"
echo "3) neural-chat (5GB, conversational)"
echo "4) dolphin-mixtral (45GB, most capable)"
read -p "Choice (1-4): " choice

case $choice in
    1) MODEL="llama2" ;;
    2) MODEL="mistral" ;;
    3) MODEL="neural-chat" ;;
    4) MODEL="dolphin-mixtral" ;;
    *) MODEL="llama2" ;;
esac

echo "📥 Downloading $MODEL..."
ollama pull $MODEL

# 3. Copy appropriate config
echo "⚙️  Configuring Symphony-IR..."
mkdir -p .orchestrator

if [ "$MODEL" = "dolphin-mixtral" ]; then
    cp ai-orchestrator/config/agents-ollama-powerful.yaml .orchestrator/agents.yaml
elif [ "$MODEL" = "mistral" ]; then
    cp ai-orchestrator/config/agents-ollama-capable.yaml .orchestrator/agents.yaml
else
    cp ai-orchestrator/config/agents-ollama.yaml .orchestrator/agents.yaml
fi

# 4. Update model in config
sed -i.bak "s/model: .*/model: $MODEL/" .orchestrator/agents.yaml

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Start Ollama:    ollama serve"
echo "2. Run a flow:      python orchestrator.py flow-list"
echo "3. Try an example:  python orchestrator.py flow --template code_review --var component=src/auth.py"
echo ""
```

Run it:

```bash
bash setup-ollama.sh
```

## Performance Tips

### 1. GPU Acceleration

Ensure Ollama uses your GPU for faster inference:

```bash
# Ollama automatically detects GPU (NVIDIA, AMD, Apple Metal)
ollama serve

# Check logs for GPU detection
# Should see: "GPU memory: XXX GB"
```

**GPU Requirements:**
- NVIDIA: CUDA 11.8+ (automatically handles)
- AMD: ROCm support (check Ollama docs)
- Mac: Apple Silicon or Intel (automatic Metal acceleration)

### 2. Memory Management

If you have limited VRAM, reduce model size:

```bash
# Use smaller variant
ollama pull mistral:7b          # 7B params (lighter)
ollama pull neural-chat:7b      # 7B params
ollama pull llama2:7b           # 7B params (default)

# Or edit YAML to use smaller model
model: mistral:7b
```

### 3. Context Caching

Ollama caches models in memory. First request is slower:

```
First request (cold):     ~10-30 seconds
Subsequent requests:      ~2-5 seconds
```

### 4. Parallel Execution

Symphony-IR's parallel agent execution works well with local models:

```yaml
system:
  enable_parallel_execution: true  # Keep enabled
  max_phases: 10
```

## Switching Between Models and Providers

### Switch Between Local and Cloud

**To Cloud (Claude):**
```bash
cp ai-orchestrator/config/agents.yaml .orchestrator/agents.yaml
export ANTHROPIC_API_KEY=sk-...
```

**To Local (Ollama):**
```bash
cp ai-orchestrator/config/agents-ollama.yaml .orchestrator/agents.yaml
ollama serve &
```

### Use Different Ollama Models

Edit `.orchestrator/agents.yaml` and change the `model` field:

```yaml
agents:
  - name: architect
    model_provider: ollama
    model_config:
      model: mistral        # Changed from llama2
      base_url: http://localhost:11434
```

## Troubleshooting

### "Connection refused" / "Failed to connect"

Ollama server not running:

```bash
# Terminal 1: Start Ollama
ollama serve

# Terminal 2: Test Symphony-IR
python orchestrator.py status
```

### "Model not found: llama2"

Pull the model first:

```bash
ollama pull llama2
```

### Slow responses

1. Check GPU is being used:
   ```bash
   ollama serve  # Look for GPU memory in logs
   ```

2. Use smaller model:
   ```bash
   ollama pull mistral
   # Edit .orchestrator/agents.yaml to use mistral
   ```

3. Check available VRAM:
   ```bash
   nvidia-smi  # For NVIDIA GPUs
   ```

### High memory usage

Ollama keeps models in memory. Free space:

```bash
# Stop Ollama and clear models
ollama serve --rm

# Or just restart Ollama
pkill ollama
ollama serve
```

## Comparing Models

### Speed Test

```bash
python -c "
import time
from models.client import OllamaClient, Message

for model in ['llama2', 'mistral']:
    client = OllamaClient(model=model)

    start = time.time()
    response = client.call([Message('user', 'What is 2+2?')], max_tokens=50)
    elapsed = time.time() - start

    print(f'{model}: {elapsed:.1f}s')
"
```

### Quality Test

Create sample test in `.orchestrator/test_models.py`:

```python
from models.client import OllamaClient, Message

prompt = "Design a simple REST API for a todo application"

for model in ['llama2', 'mistral', 'neural-chat']:
    print(f"\n=== {model} ===")
    client = OllamaClient(model=model)
    response = client.call([Message('user', prompt)], max_tokens=300)
    print(response.content[:500])
```

## Advanced: Custom Models

### Using Ollama with Custom Quantizations

```bash
# Different quantizations of same model
ollama pull llama2:latest       # q4_K_M (default)
ollama pull llama2:latest-fp16  # Full precision (larger, slower)
ollama pull llama2:latest-q4    # Lower precision (smaller, faster)

# Use in config
model: llama2:q4
```

### Using External Model Sources

Ollama also supports pulling from Hugging Face:

```bash
# Custom or private models
ollama pull huggingface/user/model-name
```

See [Ollama model library](https://ollama.ai/library) for complete list.

## Integration with Other Tools

### With Streamlit GUI

The Streamlit interface also supports Ollama:

```bash
cd gui
# Edit config to use ollama provider
python -c "..."
streamlit run app.py
```

### With Custom Agents

Create custom agents using Ollama:

```python
from agents.agent import Agent, AgentConfig
from models.client import ModelFactory

config = AgentConfig(
    name="my_agent",
    role="Custom Role",
    model_provider="ollama",
    model_config={
        "model": "mistral",
        "base_url": "http://localhost:11434"
    },
    system_prompt="You are my custom agent..."
)

client = ModelFactory.create("ollama", model="mistral")
agent = Agent(config, client=client)
result = agent.execute("Do something")
```

## Cost Comparison

### Local Ollama (Free)

```
Model download:    One-time (no recurring cost)
Inference:         Free (local compute)
Monthly cost:      $0
Latency:           ~2-5s per request (local)
```

### Cloud Claude (Paid)

```
API key:           Required
Per request:       $0.003 (prompt) + $0.015 (completion) average
Monthly estimate:  $2-50+ depending on usage
Latency:           ~1-2s per request (API)
```

### When to Use Each

| Factor | Ollama | Claude |
|--------|--------|--------|
| Cost | 💰 Free | 💰💰💰 Paid |
| Speed | 🚀 Fast-ish | 🚀🚀 Very Fast |
| Quality | ⭐⭐⭐ Good | ⭐⭐⭐⭐ Excellent |
| Privacy | 🔒 All local | 🔓 Sent to cloud |
| Setup | ⏱️ 5 minutes | ⏱️ 1 minute |
| Internet | ✅ Not needed | ❌ Required |

## Next Steps

1. **Install Ollama**: https://ollama.ai
2. **Pull a model**: `ollama pull llama2`
3. **Run Ollama**: `ollama serve`
4. **Copy config**: `cp ai-orchestrator/config/agents-ollama.yaml .orchestrator/agents.yaml`
5. **Try it**: `python orchestrator.py flow --template code_review --var component=src/auth.py`

## Resources

- **Ollama**: https://ollama.ai
- **Models**: https://ollama.ai/library
- **Local AI**: https://github.com/jmorganca/ollama
- **Model Performance**: Check Ollama model cards for benchmarks

---

**Questions?** Run `python orchestrator.py flow-list` to see all available workflows, or check `docs/FLOW.md` for complete guide.

**Cost Calculator:**
- Ollama: Free (one-time model download)
- Cloud Claude: ~$0.03-0.50 per flow run

**Save 100% on inference costs with Ollama!** 🎉
