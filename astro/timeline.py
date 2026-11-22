"""Timeline 2026-2030: tránsitos del libro + Daewoon + años Saju y tibetanos."""
from __future__ import annotations

import re
from datetime import date

from lunar_python import Solar

from .config import ROOT
from . import saju, tibetan

MONTHS = {"ene": 1, "feb": 2, "mar": 3, "abr": 4, "may": 5, "jun": 6, "jul": 7, "ago": 8, "sep": 9, "oct": 10, "nov": 11, "dic": 12}


def transits() -> list[dict]:
    rows, year = [], None
    text = (ROOT / "data/transitos-2026-2030.md").read_text(encoding="utf-8")
    for line in text.splitlines():
        if m := re.match(r"^## (\d{4})", line):
            year = int(m.group(1))
            continue
        m = re.match(r"^\| (\d{1,2}) (\w{3}) \| (.+?) \| (\w) \| (.+?) \|", line)
        if m and year:
            d, mon, name, kind, dur = m.groups()
            planet = name.split()[0]
            rows.append({"fecha": date(year, MONTHS[mon], int(d)), "transito": name, "tipo": "Lento" if kind == "L" else "Júpiter",
                         "planeta": planet, "duracion": dur})
    return rows


def years(start: int = 2026, end: int = 2030) -> list[dict]:
    out = []
    dw = saju.natal_chart()["daewoon"]
    for y in range(start, end + 1):
        gz = Solar.fromYmd(y, 6, 1).getLunar().getYearInGanZhiExact()
        decade = next((d["pilar"] for d in reversed(dw) if d["inicio"] <= y), "")
        tp = tibetan.year_profile(y)
        out.append({"anio": y, "saju": gz, "elementos_saju": saju.describe_pillar(gz)["elementos"],
                    "daewoon": decade, "tibetano": tp["nombre"], "mewa_anio": tp["mewa"]})
    return out
