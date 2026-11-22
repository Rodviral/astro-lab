"""Astro Lab: visualizador comparativo (Occidental · Saju · Tibetano/Bön).

Correr con:  streamlit run app.py
"""
from __future__ import annotations

import calendar
from datetime import date, timedelta

import altair as alt
import pandas as pd
import streamlit as st

from astro import bridge, daily, journal, saju, tibetan, timeline, western

st.set_page_config(page_title="Astro Lab", page_icon="☸", layout="wide")

with st.sidebar:
    st.title("☸ Astro Lab")
    d = st.date_input("Fecha", value=date.today())
    st.caption("Occidental (kerykeion) · Saju (lunar-python) · Tibetano (caltib) · Reglas Bön (data/bon_rules.yaml)")
    diffs = saju.check_expected()
    if diffs:
        st.error("El Saju calculado no coincide con el HANDOFF:\n\n" + "\n".join(diffs))

tab_hoy, tab_mes, tab_tl, tab_natal, tab_sim, tab_diario = st.tabs(
    ["Hoy", "Mes", "Timeline 2026-2030", "Carta comparada", "Similitudes", "Diario y oráculo"])


@st.cache_data(show_spinner="Calculando…")
def compose(day: date) -> dict:
    return daily.compose(day)


# ── HOY ───────────────────────────────────────────────
with tab_hoy:
    c = compose(d)
    w, s, t, b = c["western"], c["saju"], c["tibetan"], c["bridge"]
    st.subheader(f"{t['dia_semana']} {d:%d/%m/%Y} · día lunar {t['dia_lunar']} · {s['dia']['pilar']} · {w['luna']['fase']}")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("#### Occidental")
        st.metric("Luna", f"{w['luna']['signo']} {w['luna']['grado']}°", w["luna"]["elemento"])
        if w["lentos"]:
            st.markdown("**Tránsitos lentos**")
            st.dataframe(pd.DataFrame(w["lentos"])[["aspecto", "orbe", "exacto"]], hide_index=True, width="stretch")
        if w["rapidos"]:
            st.markdown("**Tránsitos rápidos**")
            st.dataframe(pd.DataFrame(w["rapidos"])[["aspecto", "orbe"]], hide_index=True, width="stretch")
    with col2:
        st.markdown("#### Saju")
        st.metric("Pilar del día", s["dia"]["pilar"], s["dia"]["elementos"])
        st.markdown(
            f"| | Pilar | Ten God vs 丁 |\n|---|---|---|\n"
            f"| Día | {s['dia']['pilar']} | {s['ten_god_dia'][0]} {s['ten_god_dia'][1]}: {s['ten_god_dia'][2]} |\n"
            f"| Mes | {s['mes']['pilar']} | {s['ten_god_mes'][0]} {s['ten_god_mes'][1]}: {s['ten_god_mes'][2]} |\n"
            f"| Año | {s['anio']['pilar']} | {s['ten_god_anio'][0]} {s['ten_god_anio'][1]}: {s['ten_god_anio'][2]} |")
        st.caption(f"Término solar: {s['termino_solar']}")
        if s["aporta_ausentes"]:
            st.success(f"Hoy entra {', '.join(s['aporta_ausentes'])}, ausente en tu carta.")
    with col3:
        st.markdown("#### Tibetano / Bön")
        st.metric("Día lunar", f"{t['dia_lunar']} · mes {t['mes']}", t["anio"]["nombre"])
        st.markdown(
            f"| Campo | Hoy |\n|---|---|\n"
            f"| Día sexagenario | {t['dia_sexagenario']} |\n"
            f"| Elemento del día de la semana | {t['elemento_dia_semana']} |\n"
            f"| Relación | {t['relacion_elementos']} |\n"
            f"| Mewa / Parkha del día | {t['mewa_dia']} · {t['parkha_dia']} |")
        if t["dia_doble"]:
            st.info("Día doble (el día lunar se repite).")
        if t["dia_previo_omitido"]:
            st.info("El día lunar anterior se omitió.")
        for f in t["festivales"]:
            st.success(f"Festividad: {f}")
        if not t["dias_personales_configurados"]:
            st.caption("Días la / sog / shé sin configurar (data/bon_rules.yaml).")
        for p in t["dias_personales"]:
            st.warning(p)

    st.divider()
    st.markdown("#### Puente entre sistemas")
    st.dataframe(pd.DataFrame(b["filas"]), hide_index=True, width="stretch")
    st.markdown(f"**{b['lectura']}** {b['day_master_vs_dia']}.")
    st.caption("Supuesto: para comparar, Aire occidental se lee como Madera (movimiento). No es una regla tradicional.")

    st.markdown("#### Práctica sugerida")
    if t["practica"]:
        p = t["practica"]
        st.markdown(f"**{p['titulo']}** {'· día auspicioso mayor' if p['mayor'] else ''}\n\n"
                    f"- Enseñanza: {p['ensenanza']}\n- Purificar: {p['purificar']}\n- Sugerencia: {p['sugerencia']}")
    else:
        st.markdown("Día sin práctica especial en el calendario. Práctica regular.")
    if not t["validado"]:
        st.caption("⚠️ Reglas Bön sin validar contra la app Bon Calendar. Tu lama tiene la última palabra.")

    st.markdown("#### Checklist")
    for x in c["checklist"]:
        st.checkbox(x, key=f"chk-{d}-{x}")
    st.markdown("**Palabras clave:** " + " · ".join(c["palabras_clave"]))

    if st.button("Guardar nota del día en el vault"):
        try:
            path = journal.write_daily_note(d, daily.to_markdown(d, c))
            st.success(f"Guardada en {path}")
        except OSError as e:
            st.error(f"No se pudo escribir: {e}")

# ── MES ───────────────────────────────────────────────
with tab_mes:
    first = d.replace(day=1)
    n_days = calendar.monthrange(d.year, d.month)[1]
    rows = []
    for i in range(n_days):
        day = first + timedelta(days=i)
        tt, ss = tibetan.day_info(day), saju.day_info(day)
        rows.append({
            "fecha": day.strftime("%a %d"),
            "día lunar": tt["dia_lunar"],
            "práctica Bön": (tt["practica"]["titulo"] + (" ★" if tt["practica"]["mayor"] else "")) if tt["practica"] else "",
            "festividad": ", ".join(tt["festivales"]),
            "la/sog/shé": " · ".join(x.split(":")[0] for x in tt["dias_personales"]),
            "elementos": tt["relacion_elementos"].split(" ")[0],
            "Saju": ss["dia"]["pilar"],
            "Ten God": f"{ss['ten_god_dia'][0]} {ss['ten_god_dia'][1]}",
        })
    st.subheader(f"{calendar.month_name[d.month]} {d.year}")
    st.dataframe(pd.DataFrame(rows), hide_index=True, width="stretch", height=36 * (n_days + 1))
    st.caption("★ = uno de los 4 días auspiciosos mayores del mes (8, 15, 22, 30).")

# ── TIMELINE ──────────────────────────────────────────
with tab_tl:
    tr = pd.DataFrame(timeline.transits())
    planets = sorted(tr["planeta"].unique())
    pick = st.multiselect("Planetas", planets, default=[p for p in planets if p != "Júpiter"])
    view = tr[tr["planeta"].isin(pick)]
    chart = alt.Chart(view).mark_circle(size=90).encode(
        x=alt.X("fecha:T", title=None),
        y=alt.Y("planeta:N", title=None),
        color=alt.Color("tipo:N", legend=alt.Legend(orient="top")),
        tooltip=["fecha:T", "transito:N", "duracion:N"],
    ).properties(height=280)
    today_rule = alt.Chart(pd.DataFrame({"fecha": [pd.Timestamp(d)]})).mark_rule(strokeDash=[4, 4]).encode(x="fecha:T")
    st.altair_chart(chart + today_rule, width="stretch")
    st.markdown("**Años en los tres sistemas**")
    st.dataframe(pd.DataFrame(timeline.years()), hide_index=True, width="stretch")
    with st.expander("Lista completa de tránsitos"):
        st.dataframe(view, hide_index=True, width="stretch")

# ── CARTA COMPARADA ───────────────────────────────────
with tab_natal:
    nc, tp = saju.natal_chart(), tibetan.natal_profile()
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("#### Occidental")
        st.dataframe(pd.DataFrame(western.natal_table()), hide_index=True, width="stretch")
    with c2:
        st.markdown("#### Saju")
        st.dataframe(pd.DataFrame([{"pilar": k, **saju.describe_pillar(v)} for k, v in nc["pilares"].items()])
                     [["pilar", "tallo", "rama", "elementos"]], hide_index=True, width="stretch")
        st.bar_chart(pd.Series(nc["conteo_elementos"], name="conteo"))
        st.markdown("**Daewoon**")
        st.dataframe(pd.DataFrame(nc["daewoon"]), hide_index=True, width="stretch")
        st.caption("El HANDOFF estima el inicio de 辛卯 en 2025; lunar-python da 2024. Diferencia de método de redondeo.")
    with c3:
        st.markdown("#### Tibetano")
        st.markdown(f"| Campo | Valor |\n|---|---|\n| Año | {tp['nombre']} |\n| Mewa natal | {tp['mewa']} |\n"
                    f"| Parkha natal | {tp['parkha'] or 'pendiente'} |")
        st.markdown("**Perfil elemental (la, sog, lü, wangthang, lungta)**")
        pe = tp["perfil_elemental"]
        st.markdown("| Campo | Elemento |\n|---|---|\n" + "\n".join(f"| {k} | {v or 'pendiente'} |" for k, v in pe.items()))
        if not tp["perfil_validado"]:
            st.caption("Completar en data/bon_rules.yaml con tu maestro o una fuente fiable.")

# ── SIMILITUDES ───────────────────────────────────────
with tab_sim:
    st.dataframe(pd.DataFrame(bridge.SIMILITUDES), hide_index=True, width="stretch")

# ── DIARIO Y ORÁCULO ──────────────────────────────────
with tab_diario:
    c = compose(d)
    left, right = st.columns(2)
    with left:
        st.markdown("#### Registrar práctica")
        with st.form("practica"):
            what = st.text_input("¿Qué practicaste?")
            mins = st.number_input("Minutos", 0, 600, 20)
            notes = st.text_area("Notas")
            if st.form_submit_button("Guardar") and what:
                journal.add({"tipo": "practica", "fecha": d, "practica": what, "minutos": mins, "notas": notes,
                             "dia_lunar": c["tibetan"]["dia_lunar"]})
                st.success("Guardado.")
    with right:
        st.markdown("#### Consulta Mo (Sipé Gyalmo)")
        st.caption("Haz tu práctica y la tirada como te fue transmitido. Aquí solo registras el resultado.")
        with st.form("mo"):
            q = st.text_input("Pregunta")
            throw = st.text_input("Resultado de la tirada")
            if st.form_submit_button("Preparar consulta") and q and throw:
                journal.add({"tipo": "mo", "fecha": d, "pregunta": q, "tirada": throw,
                             "dia_lunar": c["tibetan"]["dia_lunar"]})
                st.markdown("Copia esto en Claude:")
                st.code(journal.oracle_prompt(d, q, throw, c["tibetan"], c["saju"]), language=None)
    st.markdown("#### Historial")
    log = journal.entries()
    if log:
        st.dataframe(pd.DataFrame(log[::-1]), hide_index=True, width="stretch")
    else:
        st.caption("Sin registros todavía. Se guardan solo en tu equipo (carpeta diario/).")
