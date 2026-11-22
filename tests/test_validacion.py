"""Validaciones del plan: si alguna falla, no confíes en la app hasta revisarla."""
from datetime import date

from astro import saju, tibetan, timeline, western
from astro import calculate_transits as ct


def test_saju_natal_igual_al_handoff():
    assert saju.check_expected() == []
    assert saju.natal_chart()["day_master"] == "丁"


def test_conteo_elementos():
    c = saju.natal_chart()["conteo_elementos"]
    assert c == {"Madera": 1, "Fuego": 4, "Tierra": 0, "Metal": 3, "Agua": 0}


def test_perfil_tibetano_natal():
    p = tibetan.natal_profile()
    assert p["nombre"] == "Pájaro de Metal hembra"
    assert p["mewa"] == "1 Blanco"


def test_dia_saju_y_tibetano_coinciden():
    # Mismo ciclo de 60 días en ambos sistemas
    for d in (date(2026, 11, 22), date(2027, 2, 6), date(2028, 8, 17)):
        s, t = saju.day_info(d), tibetan.day_info(d)
        assert s["dia"]["elemento_tallo"] == t["elemento_dia"], d


def test_occidental_semana_validacion_handoff():
    wk = ct.calculate_week(2026, 11, 23)
    assert abs(wk["week_summary"]["solar_arc_value"] - 44.02) < 0.05
    sat = [a for a in wk["week_summary"]["slow_planet_aspects"]
           if a["moving"] == "Saturn" and a["natal"] == "Jupiter" and a["aspect"] == "Opposition"]
    assert sat and abs(sat[0]["orb"] - 0.77) < 0.05


def test_timeline_166_transitos():
    assert len(timeline.transits()) == 166


def test_occidental_dia():
    w = western.day_info(date(2026, 11, 22))
    assert w["luna"]["signo"]


def test_calendario_coincide_con_app_shen():
    # Capturas de la app Shen (FPYB): 21-nov-2026 = día lunar 12, mes Horda 10, sábado
    t = tibetan.day_info(date(2026, 11, 21))
    assert (t["mes"], t["dia_lunar"]) == (10, 12)
    assert "Gran debate de la Escuela Dialéctica" in t["festivales"]
    # 19-ene-2026 = día 1 del mes 12: Losar de Zhang Zhung
    t = tibetan.day_info(date(2026, 1, 19))
    assert (t["mes"], t["dia_lunar"]) == (12, 1)
    assert any("Zhang Zhung" in f for f in t["festivales"])


def test_dias_la_sog_she_pajaro():
    # Viernes la, jueves sog, martes shé (Key FPYB, fila Garuda/Monkey)
    assert any("la" in x for x in tibetan.day_info(date(2026, 11, 27))["dias_personales"])
    assert any("sog" in x for x in tibetan.day_info(date(2026, 11, 26))["dias_personales"])
    assert any("shé" in x for x in tibetan.day_info(date(2026, 11, 24))["dias_personales"])
