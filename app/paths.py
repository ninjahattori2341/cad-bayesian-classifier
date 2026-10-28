"""Single source of truth for repository paths."""
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent
ROOT = APP_DIR.parent
PAPER_DIR = ROOT / "paper"
DATA_CSV = PAPER_DIR / "heart_cleveland_clean.csv"
RESULTS_JSON = PAPER_DIR / "results.json"

def require_inputs() -> None:
    missing = [p for p in (DATA_CSV, RESULTS_JSON) if not p.is_file()]
    if missing:
        raise FileNotFoundError("Missing required input file(s): " + ", ".join(str(p.relative_to(ROOT)) for p in missing))
