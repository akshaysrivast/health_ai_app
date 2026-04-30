from __future__ import annotations

import os
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[4]
DEFAULT_RULES_FILE = REPO_ROOT / "agents" / "diagnosis-agent" / "config" / "diagnosis_rules.json"
DEFAULT_RULE_ENGINE_FILE = REPO_ROOT / "shared" / "rule-engine" / "rule_engine.py"


def get_rules_file_path() -> Path:
    return Path(os.getenv("DIAGNOSIS_RULES_FILE", str(DEFAULT_RULES_FILE)))


def get_rule_engine_file_path() -> Path:
    return Path(os.getenv("RULE_ENGINE_FILE", str(DEFAULT_RULE_ENGINE_FILE)))


def is_llm_refinement_enabled() -> bool:
    return os.getenv("ENABLE_DIAGNOSIS_LLM_REFINEMENT", "false").lower() in {"1", "true", "yes"}
