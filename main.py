import subprocess
import sys
from pathlib import Path

APP_FILE = Path(__file__).parent / "ui.py"

if __name__ == "__main__":
    subprocess.run([
        sys.executable,
        "-m",
        "streamlit",
        "run",
        str(APP_FILE),
        "--server.address",
        "0.0.0.0",
        "--server.port",
        "8501",
    ])

