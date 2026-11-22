"""Calendario tibetano (caltib) + reglas Bön (data/bon_rules.yaml)."""
from __future__ import annotations

import warnings
from datetime import date
from functools import lru_cache

from .config import bon_rules, natal

with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    import caltib
    from caltib.engines.trad_attr import TraditionalAttributeEngine

ANIMALS = ["Ratón", "Buey", "Tigre", "Liebre", "Dragón", "Serpiente", "Caballo", "Oveja", "Mono", "Pájaro", "Perro", "Cerdo"]
ELEMENTS = ["Madera", "Fuego", "Tierra", "Metal", "Agua"]
MEWA_COLORS = ["Blanco", "Negro", "Azul", "Verde", "Amarillo", "Blanco", "Rojo", "Blanco", "Rojo"]
TRIGRAMS = ["Li", "Khön", "Dwa", "Khen", "Kham", "Gin", "Zin", "Zön"]
WEEKDAYS = ["Domingo", "Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado"]

# Relación entre elementos (ciclo de generación / control)
_GEN = {"Madera": "Fuego", "Fuego": "Tierra", "Tierra": "Metal", "Metal": "Agua", "Agua": "Madera"}
_CTRL = {"Madera": "Tierra", "Tierra": "Agua", "Agua": "Fuego", "Fuego": "Metal", "Metal": "Madera"}


def element_relation(a: str, b: str) -> str:
    if a == b:
        return "amigo (mismo elemento)"
    if _GEN[a] == b or _GEN[b] == a:
        return "madre-hijo (se nutren)"
    if _CTRL[a] == b or _CTRL[b] == a:
        return "enemigos (uno controla al otro)"
    return "neutral"


def _engine() -> str:
    return natal().get("motor_tibetano", "phugpa")


def year_profile(tib_year: int) -> dict:
    a = TraditionalAttributeEngine(_engine()).get_year_attributes(tib_year)
    mewa = a["mewa"]
    return {
        "animal": ANIMALS[a["animal"]],
        "elemento": ELEMENTS[a["element"]],
        "genero": "macho" if a["gender"] == 0 else "hembra",
        "mewa": f"{mewa} {MEWA_COLORS[mewa - 1]}",
        "nombre": f"{ANIMALS[a['animal']]} de {ELEMENTS[a['element']]} {'macho' if a['gender'] == 0 else 'hembra'}",
    }


def natal_profile() -> dict:
    d = natal()["nacimiento"]["fecha"]
    tib = day_raw(d)
    prof = year_profile(tib.tibetan.year)
    rules = bon_rules()
    prof["perfil_elemental"] = rules.get("perfil_natal", {})
    prof["perfil_validado"] = rules.get("validado_perfil_natal", False)
    prof["parkha"] = None  # pendiente: requiere fórmula de parkha natal por sexo y edad
    return prof


@lru_cache(maxsize=4096)
def day_raw(d: date):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        return caltib.day_info(d, engine=_engine())


def day_info(d: date) -> dict:
    info = day_raw(d)
    t = info.tibetan
    civ = info.civil_attributes or {}
    rules = bon_rules()
    wd = civ.get("day_of_week", (d.isoweekday() % 7))
    wd_el = rules["elemento_dia_semana"][wd]
    day_el = ELEMENTS[civ["element"]]
    practice = rules["dias_lunares"].get(t.tithi)
    festivals = [
        f["nombre"] for f in rules.get("festivales", [])
        if f["mes"] == t.month and ("dia" not in f or f["dia"] <= t.tithi <= f.get("dia_fin", f["dia"]))
    ]

    personal = []
    for key, label in (("la", "Día la (alma): favorable para lo espiritual"),
                       ("sog", "Día sog (fuerza vital): favorable para acciones virtuosas"),
                       ("she", "Día shé (obstáculos): evitar inicios importantes; los obstáculos se someten con ritual")):
        if rules["dias_personales"].get(key) == wd:
            personal.append(label)

    mewa = civ.get("mewa")
    return {
        "anio_tibetano": t.year,
        "anio": year_profile(t.year),
        "mes": t.month,
        "mes_bisiesto": t.is_leap_month,
        "dia_lunar": t.tithi,
        "dia_doble": t.occ == 2,
        "dia_previo_omitido": t.previous_tithi_skipped,
        "dia_semana": WEEKDAYS[wd],
        "elemento_dia_semana": wd_el,
        "dia_sexagenario": f"{ANIMALS[civ['animal']]} de {day_el}",
        "elemento_dia": day_el,
        "relacion_elementos": element_relation(wd_el, day_el),  # jung tsi; no es la combinación Shen
        "app_shen_url": rules.get("app_shen_url"),
        "mewa_dia": f"{mewa} {MEWA_COLORS[mewa - 1]}" if mewa else None,
        "parkha_dia": TRIGRAMS[civ["trigram"]] if "trigram" in civ else None,
        "practica": practice,
        "festivales": festivals,
        "dias_personales": personal,
        "dias_personales_configurados": any(v is not None for v in rules["dias_personales"].values()),
        "validado": rules.get("validado_dias_lunares", False),
        "motor": _engine(),
    }
