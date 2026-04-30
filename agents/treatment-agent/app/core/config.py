from __future__ import annotations

import os
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[4]
DEFAULT_PROTOCOLS_FILE = REPO_ROOT / "agents" / "treatment-agent" / "config" / "treatment_protocols.json"


def get_protocols_file_path() -> Path:
    return Path(os.getenv("TREATMENT_PROTOCOLS_FILE", str(DEFAULT_PROTOCOLS_FILE)))
