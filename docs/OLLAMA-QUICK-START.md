# Ollama Quick Start - Local AI Models in 5 Minutes

Get Symphony-IR running with free, local AI models in under 5 minutes. No API keys, no cloud, no costs.

## 1. Install Ollama (1 minute)

```bash
# macOS
brew install ollama

# Linux
curl -fsSL https://ollama.ai/install.sh | sh

# Windows
# Download from https://ollama.ai
```

## 2. Download a Model (2 minutes)

Choose based on your system:

```bash
# Fastest & lightest (recommended for most)
ollama pull mistral

# Alternative options:
ollama pull llama2          # Fast, good quality
ollama pull neural-chat     # Great for conversations
ollama pull dolphin-mixtral # Most capable (requires 24GB VRAM)
```

## 3. Start Ollama Server (automatically runs in background)

```bash
ollama serve
```

See: `Listening on 127.0.0.1:11434`

## 4. Configure Symphony-IR (1 minute)

```bash
cd Symphony-IR/ai-orchestrator

# Choose configuration based on model:
# - For mistral, neural-chat:
cp config/agents-ollama-capable.yaml ../.orchestrator/agents.yaml

# - For llama2:
cp config/agents-ollama.yaml ../.orchestrator/agents.yaml

# - For dolphin-mixtral:
cp config/agents-ollama-powerful.yaml ../.orchestrator/agents.yaml
```

## 5. Run Symphony Flow (1 minute)

```bash
# List available workflows
python orchestrator.py flow-list

# Run code review
python orchestrator.py flow --template code_review --var component=src/auth.py

# Or try other templates:
python orchestrator.py flow --template api_design --var api_name="user-service"
python orchestrator.py flow --template database_schema --var database_name="accounts"
python orchestrator.py flow --template testing_strategy --var component_name="payment"
```

## That's It! 🎉

Your local AI orchestrator is now running completely free, with no API keys, no cloud, no costs.

---

## Command Reference

### Start Ollama (keep running in background)
```bash
ollama serve
```

### Pull Different Models
```bash
ollama pull llama2
ollama pull mistral
ollama pull neural-chat
ollama pull dolphin-mixtral
```

### Switch Configurations
```bash
# Lightweight (llama2)
cp ai-orchestrator/config/agents-ollama.yaml .orchestrator/agents.yaml

# Balanced (mistral)
cp ai-orchestrator/config/agents-ollama-capable.yaml .orchestrator/agents.yaml

# Powerful (dolphin-mixtral)
cp ai-orchestrator/config/agents-ollama-powerful.yaml .orchestrator/agents.yaml
```

### Run Orchestrator
```bash
cd ai-orchestrator

# List templates
python orchestrator.py flow-list

# Run a flow
python orchestrator.py flow --template code_review --var component=myfile.py

# Check flow status
python orchestrator.py flow-status

# Run general task
python orchestrator.py run "Your task description"
```

### Check It's Working
```bash
# Verify Ollama is running
curl http://localhost:11434/api/tags

# Verify Symphony-IR config
python orchestrator.py status
```

---

## Model Comparison

| Model | Size | Speed | Quality | Best For |
|-------|------|-------|---------|----------|
| llama2 | 4GB | ⚡⚡⚡ Fast | ⭐⭐⭐ | Testing, quick iterations |
| mistral | 5GB | ⚡⚡ Medium | ⭐⭐⭐⭐ | **Most recommended** |
| neural-chat | 5GB | ⚡⚡ Medium | ⭐⭐⭐⭐ | Conversations, chat |
| dolphin-mixtral | 45GB | ⚡ Slow | ⭐⭐⭐⭐⭐ | Complex reasoning |

**Recommendation**: Start with `mistral` - great balance of speed and quality.

---

## Troubleshooting

### "Connection refused"
Ollama not running. Start it:
```bash
ollama serve
```

### "Model not found"
Pull the model first:
```bash
ollama pull mistral
```

### Slow responses
Your GPU might not be used. Check Ollama logs for GPU memory. Ollama automatically uses GPU if available.

### Need more help?
See [docs/OLLAMA.md](OLLAMA.md) for complete documentation.

---

## Next: Using Different Models

Edit `.orchestrator/agents.yaml` and change the model line:

```yaml
agents:
  - name: architect
    model_provider: ollama
    model_config:
      model: mistral  # Change to: llama2, neural-chat, dolphin-mixtral
      base_url: http://localhost:11434
```

---

## Cost Savings Calculator

- **Monthly cost with Ollama**: $0 (one-time model download)
- **Monthly cost with Claude**: $2-50+ depending on usage
- **Cost per flow with Ollama**: $0
- **Cost per flow with Claude**: $0.03-0.50

**Save $0-50/month by using local models!** 💰

---

**Questions?** Check [docs/OLLAMA.md](OLLAMA.md) for comprehensive guide.
