#!/usr/bin/env python3
"""Run the bundled Nutmeg CLI without an installed Codex skill or original repo."""
from pathlib import Path
import runpy

if __name__=="__main__":
    runpy.run_path(str(Path(__file__).resolve().parents[1]/"vendor/nutmeg/core/nutmeg.py"),run_name="__main__")
