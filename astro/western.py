"""Lente occidental: reusa calculate_transits.py (kerykeion 4.26.3) del skill semanal."""
from __future__ import annotations

from datetime import date, datetime
from functools import lru_cache

from . import calculate_transits as ct

SIGN_ELEMENT = {
    "Aries": "Fuego", "Leo": "Fuego", "Sagitario": "Fuego",
    "Tauro": "Tierra", "Virgo": "Tierra", "Capricornio": "Tierra",
    "Géminis": "Aire", "Libra": "Aire", "Acuario": "Aire",
    "Cáncer": "Agua", "Escorpio": "Agua", "Piscis": "Agua",
}


@lru_cache(maxsize=1)
def natal_positions() -> dict:
    n = ct.NATAL
    sub = ct.make_subject(n["year"], n["month"], n["day"], n["hour"], n["minute"])
    return ct.get_planet_positions(sub)


def sign_of(pos: float) -> tuple[str, float]:
    return ct.SIGN_NAMES[ct.SIGN_LIST[int(pos / 30) % 12]], round(pos % 30, 2)


def natal_table() -> list[dict]:
    rows = []
    for k, v in natal_positions().items():
        s, deg = sign_of(v)
        rows.append({"punto": ct.PLANET_LABELS[k], "signo": s, "grado": deg, "elemento": SIGN_ELEMENT[s]})
    return rows


@lru_cache(maxsize=512)
def day_info(d: date) -> dict:
    t = ct.make_subject(d.year, d.month, d.day, 12, 0)
    pos = ct.get_planet_positions(t)
    moving = {k: v for k, v in pos.items() if k not in ("ASC", "MC")}  # ASC/MC de tránsito no aplican a mediodía
    aspects = ct.find_aspects(moving, natal_positions(), ct.TRANSIT_ORBS, "Tránsito")
    slow = {"Pluto", "Neptune", "Uranus", "Saturn", "Jupiter"}
    moon_sign, moon_deg = sign_of(pos["Moon"])
    sun_sign, _ = sign_of(pos["Sun"])
    planets = []
    for k, v in pos.items():
        if k in ("ASC", "MC"):
            continue
        s, deg = sign_of(v)
        planets.append({"planeta": ct.PLANET_LABELS[k], "signo": s, "grado": deg})

    def fmt(a):
        return {
            "aspecto": f"{a['moving_label']} {a['aspect_symbol']} {a['natal_label']} natal",
            "orbe": a["orb"],
            "exacto": a["exact"],
            "lento": a["moving"] in slow,
        }

    return {
        "luna": {"signo": moon_sign, "grado": moon_deg, "fase": ct.get_moon_phase(datetime(d.year, d.month, d.day)),
                 "elemento": SIGN_ELEMENT[moon_sign]},
        "sol": {"signo": sun_sign, "elemento": SIGN_ELEMENT[sun_sign]},
        "lentos": [fmt(a) for a in aspects if a["moving"] in slow][:8],
        "rapidos": [fmt(a) for a in aspects if a["moving"] not in slow][:6],
        "planetas": planets,
    }


def week(d: date) -> dict:
    """Cálculo semanal completo (progresiones y arco solar), igual que el skill."""
    return ct.calculate_week(d.year, d.month, d.day)
