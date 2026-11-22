"""Carga de configuración y datos (YAML)."""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent


@lru_cache(maxsize=None)
def load_yaml(rel_path: str) -> dict:
    with open(ROOT / rel_path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def natal() -> dict:
    return load_yaml("config/natal.yaml")


def bon_rules() -> dict:
    return load_yaml("data/bon_rules.yaml")
