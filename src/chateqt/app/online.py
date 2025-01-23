"""Online module for the chatbot."""

import logging
from pathlib import Path
import subprocess
import sys

import typer

app = typer.Typer()
logger = logging.getLogger(__name__)
# logger.setLevel(logging.INFO)


@app.command()
def run() -> None:
    """Spawns a Streamlit process to run the chatbot UI."""
    script_path = Path(__file__).parent.parent / "core" / "_query.py"
    command = [sys.executable, "-m", "streamlit", "run", str(script_path)]
    subprocess.run(command, check=True)  # noqa: S603
