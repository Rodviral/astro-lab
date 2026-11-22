"""Compone el resumen del día (datos + checklist por reglas). No inventa: solo usa lo calculado."""
from __future__ import annotations

from datetime import date

from . import bridge, saju, tibetan, western


def compose(d: date) -> dict:
    w, s, t, b = western.day_info(d), saju.day_info(d), tibetan.day_info(d), bridge.today(d)
    checklist = []
    if t["practica"]:
        checklist.append(f"Practicar: {t['practica']['sugerencia']} (día lunar {t['dia_lunar']})")
        checklist.append(f"Purificar: {t['practica']['purificar'].lower()}")
    for f in t["festivales"]:
        checklist.append(f"Observar festividad: {f}")
    for p in t["dias_personales"]:
        checklist.append(p)
    exact_slow = [a for a in w["lentos"] if a["exacto"]]
    if exact_slow:
        checklist.append(f"Revisar decisiones de fondo: {exact_slow[0]['aspecto']} (orbe {exact_slow[0]['orbe']}°)")
    checklist.append(f"Usar la energía {s['ten_god_dia'][2].split(':')[0].lower()} del día ({s['ten_god_dia'][0]} {s['ten_god_dia'][1]})")
    if s["aporta_ausentes"]:
        checklist.append(f"Aprovechar que hoy entra {', '.join(s['aporta_ausentes'])}, ausente en tu carta")
    keywords = [w["luna"]["elemento"], s["dia"]["elemento_tallo"], b["dominante"], s["ten_god_dia"][0]]
    return {"western": w, "saju": s, "tibetan": t, "bridge": b, "checklist": checklist,
            "palabras_clave": list(dict.fromkeys(keywords))}


def to_markdown(d: date, c: dict) -> str:
    w, s, t, b = c["western"], c["saju"], c["tibetan"], c["bridge"]
    lines = [f"# Astro comparativo · {d.isoformat()}", ""]
    lines += ["| Sistema | Hoy |", "|---|---|",
              f"| Occidental | Luna en {w['luna']['signo']} {w['luna']['grado']}° · {w['luna']['fase']} |",
              f"| Saju | Día {s['dia']['pilar']} · {s['ten_god_dia'][0]} {s['ten_god_dia'][1]} ({s['ten_god_dia'][2]}) |",
              f"| Tibetano | Día lunar {t['dia_lunar']}, mes {t['mes']} · {t['dia_sexagenario']} |",
              f"| Puente | {b['lectura']} |", ""]
    if w["lentos"]:
        lines += ["**Tránsitos lentos**", "", "| Aspecto | Orbe |", "|---|---|"]
        lines += [f"| {a['aspecto']} | {a['orbe']}° |" for a in w["lentos"][:5]]
        lines.append("")
    if t["practica"]:
        p = t["practica"]
        lines += [f"**Práctica Bön:** {p['titulo']}. {p['sugerencia']}. Purificar: {p['purificar'].lower()}.", ""]
    lines += ["**Checklist**", ""] + [f"- [ ] {x}" for x in c["checklist"]] + [""]
    lines += ["**Palabras clave:** " + " · ".join(c["palabras_clave"]), ""]
    if not t["validado"]:
        lines += ["> Prácticas por día lunar sin validar del todo; festividades y días la/sog/shé según la app Shen (FPYB).", ""]
    return "\n".join(lines)
