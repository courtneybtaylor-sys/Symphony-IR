#!/usr/bin/env python3
"""Streamlit entry point for Symphony-IR GUI.

Delegates execution to app.py which contains the full implementation.
Run with: streamlit run gui/streamlit_app.py
"""
from pathlib import Path

_app = Path(__file__).parent / "app.py"
exec(compile(_app.read_text(encoding="utf-8"), str(_app), "exec"))
