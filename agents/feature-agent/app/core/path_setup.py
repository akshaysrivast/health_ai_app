from __future__ import annotations

import sys
from pathlib import Path


def configure_import_path() -> None:
    repo_root = Path(__file__).resolve().parents[4]
    root_str = str(repo_root)
    if root_str not in sys.path:
        sys.path.insert(0, root_str)
