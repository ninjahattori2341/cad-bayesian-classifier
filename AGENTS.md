# AGENTS.md
- Run `ruff check . && python -m pytest -q` before every commit.
- `paper/` data, results, paper, and figures are frozen.
- All user-facing wording lives in `app/copy.py`.
- Never reference paths outside the repo; use `app/paths.py`.
