"""Diario de práctica y consultas Mo. Se guarda solo en local (carpeta diario/, fuera de git)."""
from __future__ import annotations

import json
from datetime import date, datetime
from pathlib import Path

from .config import ROOT, natal

LOG = ROOT / "diario" / "practica.jsonl"


def add(entry: dict) -> None:
    LOG.parent.mkdir(exist_ok=True)
    entry = {"registrado": datetime.now().isoformat(timespec="minutes"), **entry}
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False, default=str) + "\n")


def entries() -> list[dict]:
    if not LOG.exists():
        return []
    with open(LOG, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def oracle_prompt(d: date, question: str, throw: str, tib: dict, saju_day: dict) -> str:
    """Texto para pegar en Claude: activa el skill sipe-gyalmo-oracle con el contexto del día."""
    return (
        "Usa el skill sipe-gyalmo-oracle para interpretar esta consulta Mo.\n"
        f"Fecha: {d.isoformat()} · Día lunar tibetano {tib['dia_lunar']} del mes {tib['mes']} "
        f"({tib['anio']['nombre']}) · Día {tib['dia_sexagenario']} · Elemento del día de la semana: {tib['elemento_dia_semana']}\n"
        f"Saju del día: {saju_day['dia']['pilar']} ({saju_day['ten_god_dia'][2]})\n"
        f"Pregunta: {question}\n"
        f"Resultado de la tirada: {throw}\n"
        "Responde en español, sin determinismo, con una acción concreta para hoy."
    )


def write_daily_note(d: date, body_md: str) -> Path:
    folder = Path(natal()["vault_astro"]).expanduser()
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / f"{d.isoformat()}.md"
    front = (
        "---\n"
        f"date: {d.isoformat()}\n"
        "project: astro\n"
        "output_type: daily\n"
        "tags: [astro, diario, comparativo]\n"
        "---\n\n"
    )
    path.write_text(front + body_md, encoding="utf-8")
    return path
