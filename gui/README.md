# Symphony-IR GUI

A Streamlit-based web interface for running Symphony-IR orchestration workflows from your browser.

## Features

- **Task Execution**: Run orchestration tasks directly from the web interface
- **Variable Support**: Add context variables (key=value pairs) for tasks
- **Real-time Output**: View command execution output with color coding
- **Session Management**: Browse and view saved session JSON files
- **Metrics Dashboard**: View execution metrics including tokens, costs, and confidence scores
- **Session Upload**: Import and view existing session JSON files
- **Ledger ID Extraction**: Automatically extract and display ledger IDs from output
- **Cost Analysis**: Track tokens used and estimated costs

## Installation

### 1. Install Dependencies

```bash
cd gui
pip install -r requirements.txt
```

### 2. Set Up Environment

Ensure the Symphony-IR orchestrator is properly configured:

```bash
# From the repository root
cd ai-orchestrator
python orchestrator.py init --project ..
```

## Running the GUI

```bash
cd gui
streamlit run app.py
```

The GUI will open in your browser at `http://localhost:8501`

## Usage

### Basic Workflow

1. **Enter Task Description**: In the sidebar, describe the task for the orchestrator
   - Example: "Design architecture for a user authentication system"

2. **Add Variables** (Optional):
   - Click "Add variable" to include context variables
   - Format: key=value pairs
   - Example: component=auth.py, language=Python

3. **Configure Options** (Optional):
   - **Verbose output**: See detailed execution logs
   - **Dry run**: Test without actual execution
   - **Disable prompt compiler**: Run without optimization
   - **Disable IR pipeline**: Use direct compilation

4. **Run**: Click "▶ Run Orchestrator" to execute

5. **View Results**:
   - **Output tab**: See execution output and ledger IDs
   - **Sessions tab**: Browse previously saved sessions
   - **Metrics tab**: Analyze execution statistics
   - **Upload tab**: Import external session files

### Sidebar Options

- **Task Description**: The main prompt for the orchestrator
- **Variables**: Add contextual information (0-10 variables)
- **Verbose**: Show detailed logs and statistics
- **Dry run**: Preview without execution
- **No compile**: Skip prompt compiler optimization
- **No IR**: Skip IR pipeline transformations

## Tabs Explained

### Output Tab
- **Summary**: Quick status, ledger IDs, resources used
- **Raw Output**: Full command output for debugging

### Sessions Tab
- Browse most recently saved sessions
- View complete session JSON with all metadata
- Download individual sessions as JSON

### Metrics Tab
- **Resource Usage**: Tokens and costs
- **Phase Analysis**: Which phases were executed
- **Confidence Scores**: Model confidence metrics

### Upload Tab
- Upload an existing session.json file
- View imported session details
- Download imported sessions

## Configuration

### Environment Variables

Create a `.env` file in the repository root (or `.orchestrator/.env`):

```bash
ANTHROPIC_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here
```

### Agents Configuration

Edit `.orchestrator/agents.yaml` to customize:
- Agent roles and names
- Model providers and versions
- Temperature and token limits
- System prompts
- Custom constraints

## Advanced Features

### Session Management

Sessions are automatically saved to:
```
.orchestrator/runs/run_YYYYMMDD_HHMMSS_<run_id>.json
```

Access them through the **Sessions** tab or directly from the file system.

### Real-time Output

Output is displayed and parsed for:
- Status indicators (✓ success, ✗ error)
- Ledger IDs (with copy button)
- Token counts and costs
- Confidence scores
- Phase transitions

### Cost Tracking

The GUI automatically extracts:
- Tokens used per execution
- Estimated cost (if available)
- Cost per 1K tokens analysis

## Troubleshooting

### "orchestrator.py not found"
Ensure you're running the GUI from the correct directory:
```bash
cd /path/to/Symphony-IR/gui
streamlit run app.py
```

### Timeout errors
If executions take longer than 5 minutes, increase the timeout in `app.py`:
```python
timeout=600  # 10 minutes
```

### Missing environment variables
Set API keys in `.orchestrator/.env`:
```bash
export ANTHROPIC_API_KEY=sk-...
```

### No sessions appearing
Sessions are saved to `.orchestrator/runs/`. Ensure:
1. The directory exists
2. You have read permissions
3. At least one orchestration has been run

## API Integration

The GUI communicates with Symphony-IR via:
```bash
python orchestrator.py run "<task>" --project . [--verbose] [--dry-run]
```

All output is captured, parsed, and displayed in the interface.

## Development

### Adding New Features

1. **New Tab**: Add to tabs definition at the bottom of `app.py`
2. **New Widget**: Use Streamlit components (st.button, st.slider, etc.)
3. **New Parsing**: Add regex patterns to extract data from output

### Testing

```bash
# Test without Anthropic API
streamlit run app.py --logger.level=debug

# Test dry run
# Enable "Dry run" checkbox in GUI
```

## Limitations

- Single-threaded execution (runs one task at a time)
- No user authentication or session persistence
- File uploads limited to JSON format
- Output limited to recent sessions

## Future Enhancements

- [ ] Multi-user support with authentication
- [ ] Batch task execution
- [ ] Advanced analytics dashboard
- [ ] Task history and replay
- [ ] Custom agent configuration UI
- [ ] Real-time streaming output
- [ ] Database backend for session persistence

## Support

For issues or questions:
1. Check the logs in `.orchestrator/logs/`
2. Review agent configuration in `.orchestrator/agents.yaml`
3. Test with `python orchestrator.py run "test task" --verbose`
4. Check API key configuration

## License

Part of Symphony-IR project
