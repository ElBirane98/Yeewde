from __future__ import annotations

import os
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKIP_DIRS = {".git", ".venv", "node_modules"}
TARGET_DIR_NAMES = {"__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache"}
TARGET_EXTENSIONS = {".pyc", ".pyo"}

removed: list[Path] = []

for dirpath, dirnames, filenames in os.walk(ROOT):
    dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
    for dirname in list(dirnames):
        if dirname in TARGET_DIR_NAMES:
            full = Path(dirpath) / dirname
            shutil.rmtree(full, ignore_errors=True)
            removed.append(full)
            dirnames.remove(dirname)

    for filename in filenames:
        if Path(filename).suffix.lower() in TARGET_EXTENSIONS:
            full = Path(dirpath) / filename
            try:
                full.unlink()
                removed.append(full)
            except FileNotFoundError:
                pass

print(f"Removed {len(removed)} artifact(s)")
for item in removed:
    print(item)
