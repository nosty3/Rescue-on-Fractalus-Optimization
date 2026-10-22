"""Compatibility entry point: rebuild the current optimized game."""
import runpy
from pathlib import Path
runpy.run_path(str(Path(__file__).with_name("rebuild_current.py")),run_name="__main__")
