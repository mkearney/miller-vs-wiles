"""Entry point: python run.py"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))
from mvw.analysis import run  # noqa: E402

if __name__ == "__main__":
    r = run()
    print(json.dumps({k: r[k] for k in ["style_summary", "separability", "perception_means"]}, indent=2, default=float))
