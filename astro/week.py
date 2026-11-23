"""Paquete semanal para el skill astrology-week-report.

Junta en un solo JSON lo que el skill necesita y que antes Claude tenía que recordar:
occidental (tránsitos, progresiones, arco solar), eventos exactos (lunaciones,
ingresos, estaciones), Saju y calendario tibetano/Bön por día.

Uso:  python -m astro.week 2026 11 23      (cualquier fecha; se ajusta al lunes)
"""
from __future__ import annotations

import json
import sys
from datetime import date, datetime, timedelta, timezone
from zoneinfo import ZoneInfo

import swisseph as swe

from . import bridge, saju, tibetan
from . import calculate_transits as ct
from .config import bon_rules, natal

_FLAGS = swe.FLG_MOSEPH | swe.FLG_SPEED  # Moshier: no requiere archivos de efemérides
_SIGNS = ["Aries", "Tauro", "Géminis", "Cáncer", "Leo", "Virgo",
          "Libra", "Escorpio", "Sagitario", "Capricornio", "Acuario", "Piscis"]
_PLANETS = {swe.SUN: "Sol", swe.MERCURY: "Mercurio", swe.VENUS: "Venus", swe.MARS: "Marte",
            swe.JUPITER: "Júpiter", swe.SATURN: "Saturno", swe.URANUS: "Urano",
            swe.NEPTUNE: "Neptuno", swe.PLUTO: "Plutón"}
_PHASES = {0: "Luna nueva", 90: "Cuarto creciente", 180: "Luna llena", 270: "Cuarto menguante"}
_STEP = 1 / 24  # búsqueda por hora, luego bisección


def _tz() -> ZoneInfo:
    return ZoneInfo(natal()["nacimiento"]["tz"])


def _jd(dt_utc: datetime) -> float:
    return swe.julday(dt_utc.year, dt_utc.month, dt_utc.day,
                      dt_utc.hour + dt_utc.minute / 60 + dt_utc.second / 3600)


def _local(jd: float) -> str:
    y, m, d, h = swe.revjul(jd)
    dt = datetime(y, m, d, tzinfo=timezone.utc) + timedelta(hours=h)
    return dt.astimezone(_tz()).strftime("%Y-%m-%d %H:%M")


def _lon(jd: float, p: int) -> tuple[float, float]:
    x = swe.calc_ut(jd, p, _FLAGS)[0]
    return x[0], x[3]


def _fmt_pos(lon: float) -> str:
    return f"{_SIGNS[int(lon // 30)]} {int(lon % 30)}°{int((lon % 1) * 60):02d}'"


def _bisect(f, a: float, b: float) -> float:
    for _ in range(40):
        m = (a + b) / 2
        if (f(a) > 0) == (f(m) > 0):
            a = m
        else:
            b = m
    return (a + b) / 2


def _signed(x: float) -> float:
    return (x + 180) % 360 - 180


def events(start: date) -> list[dict]:
    """Lunaciones, ingresos de signo y estaciones entre el lunes 00:00 y el domingo 24:00 locales."""
    t0 = datetime(start.year, start.month, start.day, tzinfo=_tz()).astimezone(timezone.utc)
    j0, j1 = _jd(t0), _jd(t0 + timedelta(days=7))
    out = []
    j = j0
    while j < j1:
        k = j + _STEP
        elong = lambda x: (_lon(x, swe.MOON)[0] - _lon(x, swe.SUN)[0]) % 360
        for ang, name in _PHASES.items():
            f = lambda x, a=ang: _signed(elong(x) - a)
            if f(j) < 0 <= f(k) and abs(f(j)) < 30:
                t = _bisect(f, j, k)
                out.append({"tipo": "lunación", "evento": name, "hora_local": _local(t),
                            "posicion": _fmt_pos(_lon(t, swe.MOON)[0])})
        for p, name in _PLANETS.items():
            (la, sa), (lb, sb) = _lon(j, p), _lon(k, p)
            if int(la // 30) != int(lb // 30):
                sa_i, sb_i = int(la // 30), int(lb // 30)
                cusp = sb_i * 30 if sb_i == (sa_i + 1) % 12 else sa_i * 30
                t = _bisect(lambda x, c=cusp: _signed(_lon(x, p)[0] - c), j, k)
                out.append({"tipo": "ingreso", "evento": f"{name} entra a {_SIGNS[int(lb // 30)]}"
                            + (" (retrógrado)" if sb < 0 else ""), "hora_local": _local(t)})
            if (sa > 0) != (sb > 0):
                t = _bisect(lambda x: _lon(x, p)[1], j, k)
                out.append({"tipo": "estación", "evento": f"{name} estaciona {'retrógrado' if sb < 0 else 'directo'}",
                            "hora_local": _local(t), "posicion": _fmt_pos(_lon(t, p)[0])})
        j = k
    return sorted(out, key=lambda e: e["hora_local"])


def retrogrades(d: date) -> list[str]:
    jd = _jd(datetime(d.year, d.month, d.day, 12, tzinfo=_tz()).astimezone(timezone.utc))
    return [n for p, n in _PLANETS.items() if p != swe.SUN and _lon(jd, p)[1] < 0]


def _day(d: date) -> dict:
    s, t, b = saju.day_info(d), tibetan.day_info(d), bridge.today(d)
    p = t["practica"]
    return {
        "fecha": d.isoformat(),
        "saju": {"pilar": s["dia"]["pilar"], "ten_god": list(s["ten_god_dia"]),
                 "aporta_ausentes": s["aporta_ausentes"]},
        "tibetano": {
            "mes": t["mes"], "dia_lunar": t["dia_lunar"], "dia_doble": t["dia_doble"],
            "dia_previo_omitido": t["dia_previo_omitido"], "dia_sexagenario": t["dia_sexagenario"],
            "mewa": t["mewa_dia"], "parkha": t["parkha_dia"],
            "practica": ({k: p[k] for k in ("titulo", "sugerencia", "purificar", "mayor")} if p else None),
            "practica_validada": bool(p) and (t["validado"] or t["dia_lunar"] in (15, 30)),
            "festivales": t["festivales"], "dias_personales": t["dias_personales"],
        },
        "puente": {"lectura": b["lectura"], "dominante": b["dominante"], "day_master": b["day_master_vs_dia"]},
    }


def _current_daewoon(d: date) -> str | None:
    past = [x for x in saju.natal_chart()["daewoon"] if x["inicio"] <= d.year]
    return f"{past[-1]['pilar']} ({past[-1]['inicio']}-{past[-1]['inicio'] + 10})" if past else None


def next_bon_days(after: date, days: int = 21) -> list[dict]:
    """Días mayores (8, 15, 22, 30), lu (29) y festividades en las semanas siguientes."""
    out = []
    for i in range(1, days + 1):
        d = after + timedelta(days=i)
        t = tibetan.day_info(d)
        p = t["practica"]
        if (p and (p["mayor"] or t["dia_lunar"] == 29)) or t["festivales"] != tibetan.day_info(d - timedelta(1))["festivales"]:
            out.append({"fecha": d.isoformat(), "dia_semana": t["dia_semana"], "dia_lunar": t["dia_lunar"],
                        "titulo": p["titulo"] if p else None, "festivales": t["festivales"],
                        "dias_personales": t["dias_personales"]})
    return out


def build(any_day: date) -> dict:
    start = any_day - timedelta(days=any_day.weekday())
    end = start + timedelta(days=6)
    s0 = saju.day_info(start)
    rules = bon_rules()
    return {
        "semana": {"inicio": start.isoformat(), "fin": end.isoformat(), "zona": natal()["nacimiento"]["tz"]},
        "occidental": ct.calculate_week(start.year, start.month, start.day),
        "eventos": events(start),
        "retrogrados_lunes": retrogrades(start),
        "saju_contexto": {"day_master": "丁", "mes": s0["mes"]["pilar"], "ten_god_mes": list(s0["ten_god_mes"]),
                          "anio": s0["anio"]["pilar"], "ten_god_anio": list(s0["ten_god_anio"]),
                          "daewoon": _current_daewoon(start), "termino_solar": s0["termino_solar"]},
        "tibetano_contexto": {"perfil_natal": tibetan.natal_profile()["nombre"], "motor": tibetan.day_info(start)["motor"]},
        "dias": [_day(start + timedelta(days=i)) for i in range(7)],
        "proximos_bon": next_bon_days(end),
        "shen": {"combinacion_del_dia": "no calculada: remitir a la app Shen", "url": rules.get("app_shen_url")},
    }


if __name__ == "__main__":
    y, m, d = (int(x) for x in sys.argv[1:4]) if len(sys.argv) >= 4 else date.today().timetuple()[:3]
    print(json.dumps(build(date(y, m, d)), ensure_ascii=False, indent=2))
