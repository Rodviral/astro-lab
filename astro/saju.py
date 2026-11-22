"""Saju (Cuatro Pilares) con lunar-python."""
from __future__ import annotations

from datetime import date

from lunar_python import Solar

from .config import natal

STEMS = "甲乙丙丁戊己庚辛壬癸"
BRANCHES = "子丑寅卯辰巳午未申酉戌亥"

STEM_ELEMENT = ["Madera", "Madera", "Fuego", "Fuego", "Tierra", "Tierra", "Metal", "Metal", "Agua", "Agua"]
BRANCH_ELEMENT = ["Agua", "Tierra", "Madera", "Madera", "Tierra", "Fuego", "Fuego", "Tierra", "Metal", "Metal", "Tierra", "Agua"]
BRANCH_ANIMAL = ["Rata", "Buey", "Tigre", "Conejo", "Dragón", "Serpiente", "Caballo", "Cabra", "Mono", "Gallo", "Perro", "Cerdo"]

ELEMENTS = ["Madera", "Fuego", "Tierra", "Metal", "Agua"]  # ciclo de generación

# Ten Gods (십신): (relación, misma polaridad) -> (hanja, coreano, español)
TEN_GODS = {
    ("igual", True): ("比肩", "비견", "Hombro: pares, autonomía"),
    ("igual", False): ("劫財", "겁재", "Rival: competencia por recursos"),
    ("produce", True): ("食神", "식신", "Expresión serena, producción"),
    ("produce", False): ("傷官", "상관", "Expresión rebelde, rompe reglas"),
    ("controla", True): ("偏財", "편재", "Riqueza indirecta: tratos, comisiones"),
    ("controla", False): ("正財", "정재", "Riqueza directa: ingreso estable"),
    ("controlado", True): ("七殺", "편관", "Presión, reto, autoridad dura"),
    ("controlado", False): ("正官", "정관", "Orden, reputación, reglas"),
    ("nutrido", True): ("偏印", "편인", "Recurso no convencional, intuición"),
    ("nutrido", False): ("正印", "정인", "Recurso, mentores, estudio"),
}


def relation(dm_el: str, other_el: str) -> str:
    i, j = ELEMENTS.index(dm_el), ELEMENTS.index(other_el)
    d = (j - i) % 5
    return {0: "igual", 1: "produce", 2: "controla", 3: "controlado", 4: "nutrido"}[d]


def ten_god(dm_stem: str, other_stem: str) -> tuple[str, str, str]:
    a, b = STEMS.index(dm_stem), STEMS.index(other_stem)
    rel = relation(STEM_ELEMENT[a], STEM_ELEMENT[b])
    return TEN_GODS[(rel, a % 2 == b % 2)]


def describe_pillar(gz: str) -> dict:
    s, b = STEMS.index(gz[0]), BRANCHES.index(gz[1])
    return {
        "pilar": gz,
        "tallo": f"{gz[0]} {STEM_ELEMENT[s]} {'yang' if s % 2 == 0 else 'yin'}",
        "rama": f"{gz[1]} {BRANCH_ANIMAL[b]}",
        "elementos": f"{STEM_ELEMENT[s]} / {BRANCH_ELEMENT[b]}",
        "elemento_tallo": STEM_ELEMENT[s],
        "elemento_rama": BRANCH_ELEMENT[b],
    }


def natal_chart() -> dict:
    n = natal()["nacimiento"]
    d = n["fecha"]
    hh, mm = map(int, n["hora"].split(":"))
    lunar = Solar.fromYmdHms(d.year, d.month, d.day, hh, mm, 0).getLunar()
    ec = lunar.getEightChar()
    pillars = {"hora": ec.getTime(), "dia": ec.getDay(), "mes": ec.getMonth(), "anio": ec.getYear()}
    yun = ec.getYun(1 if n.get("sexo", "M") == "M" else 0)
    daewoon = [
        {"pilar": dy.getGanZhi(), "inicio": dy.getStartYear(), "edad": dy.getStartAge()}
        for dy in yun.getDaYun()[1:9]
    ]
    count = {e: 0 for e in ELEMENTS}
    for gz in pillars.values():
        p = describe_pillar(gz)
        count[p["elemento_tallo"]] += 1
        count[p["elemento_rama"]] += 1
    return {"pilares": pillars, "day_master": pillars["dia"][0], "daewoon": daewoon, "conteo_elementos": count}


def check_expected() -> list[str]:
    """Compara con el Saju corregido del HANDOFF. Devuelve lista de diferencias."""
    exp = natal().get("saju_esperado", {})
    got = natal_chart()["pilares"]
    return [f"{k}: esperado {v}, calculado {got[k]}" for k, v in exp.items() if got.get(k) != v]


def day_info(d: date) -> dict:
    lunar = Solar.fromYmdHms(d.year, d.month, d.day, 12, 0, 0).getLunar()
    dm = natal_chart()["day_master"]
    day_gz = lunar.getDayInGanZhi()
    month_gz = lunar.getMonthInGanZhiExact()
    year_gz = lunar.getYearInGanZhiExact()
    out = {
        "dia": describe_pillar(day_gz),
        "mes": describe_pillar(month_gz),
        "anio": describe_pillar(year_gz),
        "ten_god_dia": ten_god(dm, day_gz[0]),
        "ten_god_mes": ten_god(dm, month_gz[0]),
        "ten_god_anio": ten_god(dm, year_gz[0]),
        "termino_solar": lunar.getPrevJieQi(True).getName(),
    }
    # Tierra y Agua están ausentes en la carta: marcar si el día las aporta
    present = {out["dia"]["elemento_tallo"], out["dia"]["elemento_rama"]}
    out["aporta_ausentes"] = sorted(present & {"Tierra", "Agua"})
    return out
