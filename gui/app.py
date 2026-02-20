#!/usr/bin/env python3
"""Streamlit GUI for Symphony-IR - Web interface for orchestrator CLI."""

import os
import json
import subprocess
import streamlit as st
from pathlib import Path
from datetime import datetime
import tempfile
import re

# Page configuration
st.set_page_config(
    page_title="Symphony-IR GUI",
    page_icon="🎼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load custom CSS for dark theme support
try:
    css_path = Path(__file__).parent / "styles.css"
    if css_path.exists():
        with open(css_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except Exception as e:
    print(f"Warning: Could not load custom styles: {e}")

# Session state initialization
if "session_id" not in st.session_state:
    st.session_state.session_id = None
if "last_output" not in st.session_state:
    st.session_state.last_output = None
if "ledger_content" not in st.session_state:
    st.session_state.ledger_content = None
if "uploaded_session" not in st.session_state:
    st.session_state.uploaded_session = None

def get_orchestrator_path():
    """Get path to orchestrator.py"""
    current_dir = Path(__file__).resolve().parent.parent
    orch_path = current_dir / "ai-orchestrator" / "orchestrator.py"
    return orch_path if orch_path.exists() else None

def find_session_files(directory="."):
    """Find all session_*.json files in directory and subdirectories."""
    path = Path(directory)
    sessions = []
    for json_file in path.rglob("session_*.json"):
        sessions.append({
            "name": json_file.name,
            "path": str(json_file),
            "modified": json_file.stat().st_mtime
        })
    return sorted(sessions, key=lambda x: x["modified"], reverse=True)

def extract_ledger_id(output):
    """Extract ledger ID from output."""
    matches = re.findall(r"[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}", output)
    return matches

def extract_tokens_and_cost(output):
    """Extract token count and cost from output."""
    token_match = re.search(r"Tokens:\s*([\d,]+)", output)
    cost_match = re.search(r"Cost:\s*\$([0-9.]+)", output)

    tokens = int(token_match.group(1).replace(",", "")) if token_match else 0
    cost = float(cost_match.group(1)) if cost_match else 0.0

    return tokens, cost

def run_symphony_command(task, variables=None):
    """Run Symphony-IR orchestrator command."""
    orchestrator_path = get_orchestrator_path()

    if not orchestrator_path:
        return False, "Error: orchestrator.py not found"

    variables = variables or {}

    try:
        # Build the command
        cmd = ["python", str(orchestrator_path), "run", task]

        # Add variables to environment (for context)
        env = os.environ.copy()

        # Run the orchestrator
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300,  # 5 minute timeout
            cwd=str(orchestrator_path.parent.parent),
            env=env
        )

        output = result.stdout + result.stderr
        success = result.returncode == 0

        return success, output
    except subprocess.TimeoutExpired:
        return False, "Error: Command execution timed out (>5 minutes)"
    except Exception as e:
        return False, f"Error executing command: {str(e)}"

def parse_json_safe(content):
    """Safely parse JSON content."""
    try:
        return json.loads(content)
    except json.JSONDecodeError as e:
        return {"error": f"Invalid JSON: {str(e)}", "raw_content": content}

# Header
col1, col2 = st.columns([4, 1])
with col1:
    st.markdown("# 🎼 Symphony-IR")
    st.markdown("**Web interface for orchestrating multi-agent AI workflows**")
with col2:
    st.markdown("")
    st.markdown("")
    st.caption("v0.1 • Multi-agent Orchestration")

# Sidebar
with st.sidebar:
    st.markdown("## ⚙️ Configuration")
    st.divider()

    # Task input
    st.markdown("### Task Definition")
    task = st.text_area(
        "Describe your task",
        placeholder="Enter the task or workflow you'd like the orchestrator to execute...",
        height=100,
        label_visibility="collapsed"
    )
    st.caption("📝 Be specific about what you want the AI agents to accomplish")

    # Variables section
    st.divider()
    st.markdown("### 📦 Context Variables")
    st.caption("Optional: Provide additional context or parameters for your task")

    variables = {}
    num_vars = st.number_input("Number of variables", min_value=0, max_value=10, value=0, label_visibility="collapsed")

    if num_vars > 0:
        for i in range(int(num_vars)):
            col1, col2 = st.columns([1, 1.5], gap="small")
            with col1:
                key = st.text_input(f"Key {i+1}", key=f"var_key_{i}", placeholder="e.g., model", label_visibility="collapsed")
            with col2:
                value = st.text_input(f"Value {i+1}", key=f"var_val_{i}", placeholder="e.g., gpt-4", label_visibility="collapsed")

            if key and value:
                variables[key] = value

    # Options
    st.divider()
    st.markdown("### ⚡ Advanced Options")

    col1, col2 = st.columns(2)
    with col1:
        verbose = st.checkbox("Verbose output", value=False, help="Show detailed execution logs")
        no_ir = st.checkbox("Disable IR pipeline", value=False, help="Skip intermediate representation processing")
    with col2:
        dry_run = st.checkbox("Dry run mode", value=False, help="Preview execution without running")
        no_compile = st.checkbox("Disable compiler", value=False, help="Skip prompt compilation step")

    # Run button
    st.divider()
    run_button = st.button(
        "▶️  Execute Orchestration",
        type="primary",
        use_container_width=True,
        disabled=not task,
        help="Run the orchestrator with your current configuration"
    )

    if run_button and task:
        with st.spinner("⏳ Executing orchestration... This may take a moment."):
            success, output = run_symphony_command(task, variables)
            st.session_state.last_output = output

            if success:
                st.success("✅ Orchestration completed successfully!", icon="✅")
                st.balloons()
                # Extract ledger IDs
                ledger_ids = extract_ledger_id(output)
                if ledger_ids:
                    st.session_state.ledger_ids = ledger_ids
            else:
                st.error("❌ Orchestration execution failed. Check the output tab for details.", icon="❌")

# Main content area with tabs
tab1, tab2, tab3, tab4 = st.tabs(["📊 Output", "📁 Sessions", "📈 Metrics", "📤 Import"])

with tab1:
    st.markdown("## 📊 Execution Output")

    if st.session_state.last_output:
        # Color-code the output based on success indicators
        output_text = st.session_state.last_output

        # Create columns for summary and output
        col1, col2 = st.columns([1.2, 1.8])

        with col1:
            st.markdown("### 📋 Summary")

            # Parse key info from output
            if "error" in output_text.lower() or "failed" in output_text.lower():
                st.error("**Status:** Failed", icon="⚠️")
            else:
                st.success("**Status:** Success", icon="✅")

            # Extract and display ledger IDs
            ledger_ids = extract_ledger_id(output_text)
            if ledger_ids:
                st.markdown("### 🔗 Session IDs")
                for lid in ledger_ids:
                    col_a, col_b = st.columns([4, 1], gap="small")
                    with col_a:
                        st.code(lid, language="text")
                    with col_b:
                        if st.button("📋", key=f"copy_{lid}", help="Copy session ID"):
                            st.toast(f"Copied: {lid[:8]}...")

            # Extract tokens and cost
            tokens, cost = extract_tokens_and_cost(output_text)
            if tokens > 0 or cost > 0:
                st.markdown("### 💾 Resource Usage")
                col_t, col_c = st.columns(2, gap="small")
                with col_t:
                    st.metric("Tokens Used", f"{tokens:,}", delta="Total tokens processed")
                with col_c:
                    st.metric("Cost (USD)", f"${cost:.4f}", delta=f"Est. cost", delta_color="off")

        with col2:
            st.markdown("### 📄 Raw Output")
            st.text_area(
                "Full execution output",
                value=output_text,
                height=400,
                disabled=True,
                label_visibility="collapsed"
            )
    else:
        st.info("💡 No execution data yet. Run an orchestration to see output here.", icon="ℹ️")

with tab2:
    st.markdown("## 📁 Session Files")

    col1, col2, col3 = st.columns([2, 1, 1])

    with col1:
        st.markdown("### Recent Sessions")
        st.caption("View and manage past orchestration sessions")

    with col2:
        st.markdown("")
        st.markdown("")
        if st.button("🔄 Refresh Sessions", use_container_width=True, help="Reload session list"):
            st.rerun()

    with col3:
        st.markdown("")
        st.markdown("")
        session_count = len(find_session_files())
        st.metric("Sessions", session_count)

    st.divider()

    sessions = find_session_files()

    if sessions:
        st.markdown(f"### Found {len(sessions)} session(s)")
        for i, session in enumerate(sessions[:10], 1):  # Show most recent 10
            with st.expander(f"📄 **{i}.** {session['name']}", expanded=False):
                try:
                    with open(session['path']) as f:
                        content = json.load(f)

                    # Display as formatted JSON
                    st.json(content)

                    # Download button
                    json_str = json.dumps(content, indent=2)
                    st.download_button(
                        label="⬇️  Download Session JSON",
                        data=json_str,
                        file_name=session['name'],
                        mime="application/json",
                        use_container_width=True,
                        key=f"download_{i}"
                    )
                except Exception as e:
                    st.error(f"❌ Error reading file: {str(e)}")
    else:
        st.info("📭 No session files found. Run an orchestration first to generate sessions.", icon="ℹ️")

with tab3:
    st.markdown("## 📈 Metrics & Statistics")

    if st.session_state.last_output:
        output = st.session_state.last_output

        # Token and cost analysis
        col1, col2, col3 = st.columns(3, gap="large")

        tokens, cost = extract_tokens_and_cost(output)

        with col1:
            st.metric("💾 Total Tokens", f"{tokens:,}", help="Total tokens processed in execution")

        with col2:
            st.metric("💰 Total Cost", f"${cost:.4f}", help="Estimated API cost")

        with col3:
            if tokens > 0:
                cost_per_token = (cost / tokens) * 1000
                st.metric("💵 Cost per 1K", f"${cost_per_token:.6f}", help="Average cost efficiency")

        st.divider()

        # Phase analysis
        st.markdown("### ⚙️ Execution Phases")

        phase_matches = re.findall(r"Phase:\s*(\w+)", output)
        if phase_matches:
            phase_counts = {}
            for phase in phase_matches:
                phase_counts[phase] = phase_counts.get(phase, 0) + 1

            col1, col2 = st.columns([1.2, 1], gap="large")
            with col1:
                st.markdown("**Phase Distribution**")
                st.bar_chart(phase_counts)
            with col2:
                st.markdown("**Phase Breakdown**")
                for phase, count in sorted(phase_counts.items(), key=lambda x: x[1], reverse=True):
                    st.write(f"• **{phase}:** {count} execution(s)")

        st.divider()

        # Confidence scores
        st.markdown("### 🎯 Confidence Analysis")
        confidence_matches = re.findall(r"confidence[=:]\s*([\d.]+)", output, re.IGNORECASE)

        if confidence_matches:
            confidences = [float(c) for c in confidence_matches if 0 <= float(c) <= 1]
            if confidences:
                avg_confidence = sum(confidences) / len(confidences)
                col1, col2, col3 = st.columns(3, gap="large")

                with col1:
                    st.metric("Average Confidence", f"{avg_confidence:.2%}",
                             delta=f"{len(confidences)} samples analyzed", delta_color="off")
                with col2:
                    st.metric("Minimum Confidence", f"{min(confidences):.2f}")
                with col3:
                    st.metric("Maximum Confidence", f"{max(confidences):.2f}")
            else:
                st.info("No confidence scores found in execution output.", icon="ℹ️")
        else:
            st.info("No confidence analysis available for this execution.", icon="ℹ️")
    else:
        st.info("💡 No execution data yet. Run an orchestration to see detailed metrics.", icon="ℹ️")

with tab4:
    st.markdown("## 📤 Import Session")
    st.markdown("Upload an existing session JSON file to view and analyze its contents")
    st.caption("📋 Supported format: JSON files from previous orchestration runs")

    st.divider()

    uploaded_file = st.file_uploader(
        "Choose a session JSON file to import",
        type="json",
        label_visibility="collapsed",
        help="Select a valid JSON file from a previous orchestration session"
    )

    if uploaded_file:
        try:
            session_data = json.load(uploaded_file)

            st.markdown("### 📊 Session Data")

            # Summary metrics
            col1, col2, col3 = st.columns(3, gap="large")

            with col1:
                if "run_id" in session_data:
                    st.metric("🔑 Run ID", str(session_data["run_id"])[:16] + "...")

            with col2:
                if "timestamp" in session_data:
                    st.metric("⏰ Timestamp", session_data["timestamp"][:19])

            with col3:
                if "state" in session_data:
                    state = session_data["state"]
                    state_emoji = "✅" if state.lower() == "success" else "⚠️"
                    st.metric(f"{state_emoji} State", state)

            st.divider()

            st.markdown("### 📋 Full Session Content")
            st.json(session_data)

            # Download option
            json_str = json.dumps(session_data, indent=2)
            st.download_button(
                label="⬇️  Download Session JSON",
                data=json_str,
                file_name=uploaded_file.name,
                mime="application/json",
                use_container_width=True,
                help="Export this session data to a file"
            )
        except json.JSONDecodeError:
            st.error("❌ Invalid JSON file. Please upload a valid JSON file.", icon="❌")
        except Exception as e:
            st.error(f"❌ Error reading file: {str(e)}", icon="❌")
    else:
        st.info("📭 No file selected. Upload a JSON session file to get started.", icon="ℹ️")

# Footer
st.divider()
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.caption("🎼 **Symphony-IR**")
with col2:
    st.caption("🚀 Web GUI v0.1")
with col3:
    st.caption("🤖 Multi-Agent Orchestration")
with col4:
    st.caption("💡 Powered by Claude")
