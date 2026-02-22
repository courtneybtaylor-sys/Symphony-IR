# GUI (Graphical User Interface) Guide

Symphony-IR's beautiful desktop application provides a point-and-click interface for orchestrating multi-agent workflows. This guide covers how to use the GUI.

## Quick Start

### Launch the Application

```bash
# From project root
python gui/main.py

# Or from gui directory
cd gui
python main.py
```

The desktop window opens with:
- 🎯 **Orchestrator tab** — Run ad-hoc tasks
- 📚 **History tab** — View past executions
- ⚙️ **Settings tab** — Configure API keys
- 🔧 **Flows tab** — Run workflow templates

## Main Interface

### Orchestrator Tab

The main workspace for running tasks.

**Input Area:**
1. Type your task description in the text field
2. Click "Run Orchestration" button
3. Results appear in the output panel

**Example tasks:**
- "Write a Python function that validates email addresses"
- "Analyze this code for performance issues"
- "Design a database schema for a blog platform"

**Output Panel:**
- **Architect Response** — Initial analysis and approach
- **Implementer Response** — Detailed implementation
- **Reviewer Response** — Quality review and suggestions

**Features:**
- 📋 Copy button to copy any response
- 💾 Save button to save results
- 📊 Token usage and cost tracking
- ⏱️ Real-time progress indicators

### History Tab

Review past orchestration runs.

**Features:**
- 📅 List of all past executions
- 🔍 Search by task description
- 📥 Download results as JSON
- 🗑️ Delete old executions
- ⏮️ Replay previous runs

**What's displayed:**
- Task description
- Execution time
- Provider used (Claude/Ollama)
- Token count and estimated cost
- Status (completed/failed)

### Flows Tab (Symphony Flow)

Pre-built workflow templates for common tasks.

**Available Flows:**
- **Code Review** — Review code quality and style
- **Security Audit** — Identify security vulnerabilities
- **Cloud Architecture** — Design cloud solutions
- **Data Pipeline** — Plan data transformation
- **ML Model** — Design ML/AI solutions
- **Incident Response** — Handle security incidents
- **Compliance Audit** — Check regulatory compliance
- **Performance Optimization** — Improve performance

**How to use:**
1. Select a flow from the dropdown
2. Enter required variables (e.g., component name)
3. Click "Run Flow"
4. Results appear with multi-step responses

### Settings Tab

Configure API keys and preferences.

**Providers:**
- **Claude** — Anthropic's Claude API
  - Paste your API key: `sk-ant-...`
  - Select model (claude-opus recommended)

- **Ollama** — Local or remote Ollama instance
  - Enter URL: `http://localhost:11434`
  - Select model (mistral, llama2, neural-chat, etc.)

**Preferences:**
- Default provider (Claude/Ollama)
- Model selection
- Temperature (creativity level)
- Max tokens (output length)

**Features:**
- ✅ Test connection button
- 🔐 Secure credential storage (Windows Credential Manager, macOS Keychain, Linux Secret Service)
- 🔄 Provider switching
- 💾 Auto-save settings

## Workflow

### Typical Usage Flow

1. **Setup (First Time)**
   - Launch GUI
   - Go to Settings tab
   - Add Claude API key or Ollama URL
   - Click "Test Connection"

2. **Run Task**
   - Go to Orchestrator tab
   - Type task description
   - Click "Run Orchestration"
   - Wait for results

3. **Review Results**
   - Read Architect's approach
   - Read Implementer's solution
   - Read Reviewer's feedback
   - Copy or save results

4. **Track History**
   - Go to History tab
   - View all past tasks
   - Search by description
   - Download results

5. **Use Templates** (Optional)
   - Go to Flows tab
   - Select a pre-built workflow
   - Enter variables
   - Run the flow

## Features

### 🎨 Beautiful Design System

- Modern, clean interface with dark/light mode
- Responsive layout that works at any window size
- Smooth animations and transitions
- Professional color scheme (blue primary, purple accents)

### 📊 Real-Time Tracking

- Live progress indicator during execution
- Token count and cost estimation
- Execution time tracking
- Provider information

### 💾 Session Management

- Auto-save settings
- History persistence
- Session export/import
- Batch task processing

### 🔐 Security

- API keys stored securely in OS credential manager
- No API keys logged or displayed
- HTTPS-only communication
- Local session history (never sent to cloud)

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+Enter` / `Cmd+Enter` | Run task |
| `Ctrl+C` | Copy to clipboard |
| `Ctrl+S` | Save results |
| `Ctrl+L` | Clear input |
| `Ctrl+H` | Go to History tab |
| `Ctrl+,` | Go to Settings tab |

## Troubleshooting

### Issue: "API Key Invalid"

**Solution:**
1. Go to Settings tab
2. Verify API key is correct
3. Click "Test Connection"
4. Check Anthropic dashboard for key status

### Issue: "Cannot connect to Ollama"

**Solution:**
1. Ensure Ollama is running: `ollama serve`
2. Check URL is correct: `http://localhost:11434`
3. Verify model is downloaded: `ollama list`
4. Click "Test Connection" in Settings

### Issue: "GUI not launching"

**Solution:**
```bash
# Check Python version
python --version  # Should be 3.10+

# Check dependencies
pip install PyQt6

# Run with error output
python gui/main.py --verbose
```

### Issue: "Out of memory" error

**Solution:**
- Close other applications
- Use smaller models in Ollama (neural-chat instead of llama2)
- Reduce max tokens in Settings

## Advanced Usage

### Command Line Launch

```bash
# Launch with specific provider
SYMPHONY_PROVIDER=claude python gui/main.py

# Launch and run task
python gui/main.py --task "Your task here"

# Launch with debug output
python gui/main.py --debug
```

### Configuration Files

GUI settings are stored in `~/.symphonyir/config.json`:

```json
{
  "providers": {
    "claude": {"api_key": "..."},
    "ollama": {"url": "..."}
  },
  "gui_theme": "dark",
  "history_limit": 100
}
```

### Integrating Custom Workflows

1. Add custom workflow YAML to `ai-orchestrator/flow/templates/`
2. Restart GUI
3. New workflow appears in Flows tab

## Performance Tips

- ⚡ Claude API is faster than local Ollama
- 🎯 More specific prompts get better results
- 💨 Reduce max tokens to get faster responses
- 🧠 Use larger models for complex tasks

## See Also

- [CLI Guide](CLI.md) — Command-line interface
- [Python API](PYTHON_API.md) — Programmatic usage
- [Settings & Troubleshooting](../../GETTING_STARTED.md)
- [Design System](../DESIGN/DESIGN_SYSTEM.md) — UI/UX details

## Technical Details

- **Framework**: PyQt6
- **Language**: Python 3.10+
- **Entry Point**: `gui/main.py`
- **Configuration**: `~/.symphonyir/config.json`
- **History**: `~/.symphonyir/history/`

For more technical details, see:
- `gui/README.md` — Development guide
- `gui/main.py` — Application code
- `gui/tabs/` — Individual UI components
