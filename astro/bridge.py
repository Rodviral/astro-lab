"""Puente entre sistemas: compara elementos y ciclos del día."""
from __future__ import annotations

from datetime import date

from . import saju, tibetan, western

# Equivalencias fijas entre sistemas (para la pestaña "Similitudes")
SIMILITUDES = [
    {"concepto": "Ciclo de 60", "saju": "60 pares tallo-rama (갑자)", "tibetano": "Rabjung: 12 animales × 5 elementos",
     "occidental": "No existe", "nota": "Tu año 辛酉 = Pájaro de Metal hembra: mismo año, mismo ciclo"},
    {"concepto": "Elementos", "saju": "5: Madera, Fuego, Tierra, Metal, Agua", "tibetano": "5: Madera, Fuego, Tierra, Hierro, Agua",
     "occidental": "4: Fuego, Tierra, Aire, Agua", "nota": "Metal = Hierro. Aire occidental no tiene equivalente directo"},
    {"concepto": "Animales", "saju": "12 ramas terrestres", "tibetano": "12 animales (Ratón… Cerdo)",
     "occidental": "12 signos (otra lógica: estaciones, no años)", "nota": "Gallo coreano = Pájaro tibetano"},
    {"concepto": "Trigramas", "saju": "I Ching (8 gua)", "tibetano": "Parkha (8): Li, Khön, Dwa, Khen, Kham, Gin, Zin, Zön",
     "occidental": "No existe", "nota": "Mismo origen chino"},
    {"concepto": "Cuadrado mágico", "saju": "9 estrellas (Lo Shu)", "tibetano": "Mewa (9 números con color)",
     "occidental": "No existe", "nota": "Tu mewa natal 1 Blanco = estrella 1 Agua"},
    {"concepto": "Ciclos largos", "saju": "Daewoon (décadas)", "tibetano": "Edad por parkha y mewa",
     "occidental": "Progresiones, arco solar, tránsitos lentos", "nota": "Comparar 辛卯 (2024-2034) con 2026-2030"},
    {"concepto": "Base del cálculo", "saju": "Calendario solar (24 términos)", "tibetano": "Lunisolar (Kalachakra / Bön)",
     "occidental": "Posiciones reales de planetas", "nota": "Occidente es el único que mide el cielo directo"},
    {"concepto": "Uso del día", "saju": "Pilar del día vs Day Master", "tibetano": "Día lunar, elementos, días la/sog/shé",
     "occidental": "Luna y aspectos a la carta", "nota": "La vista Hoy los pone lado a lado"},
]

# Equivalencia aproximada occidental -> 5 elementos (supuesto interpretativo, no tradicional)
WEST_TO_FIVE = {"Fuego": "Fuego", "Tierra": "Tierra", "Agua": "Agua", "Aire": "Madera"}


def today(d: date) -> dict:
    w = western.day_info(d)
    s = saju.day_info(d)
    t = tibetan.day_info(d)
    rows = [
        {"sistema": "Occidental", "dato": f"Luna en {w['luna']['signo']} {w['luna']['grado']}°", "elemento": w["luna"]["elemento"]},
        {"sistema": "Saju", "dato": f"Día {s['dia']['pilar']} ({s['dia']['rama']})", "elemento": s["dia"]["elemento_tallo"]},
        {"sistema": "Tibetano", "dato": t["dia_sexagenario"], "elemento": t["elemento_dia"]},
        {"sistema": "Tibetano (semana)", "dato": t["dia_semana"], "elemento": t["elemento_dia_semana"]},
    ]
    five = [WEST_TO_FIVE[w["luna"]["elemento"]], s["dia"]["elemento_tallo"], t["elemento_dia"], t["elemento_dia_semana"]]
    dominant = max(set(five), key=five.count)
    coincide = five.count(dominant)
    if coincide >= 3:
        lectura = f"Convergencia: {dominant} domina en {coincide} de 4 lecturas."
    elif coincide == 2:
        lectura = f"Tendencia parcial hacia {dominant}; el resto se dispersa."
    else:
        lectura = "Sin elemento común: día mixto, leer cada sistema por separado."
    # Day Master 丁 (Fuego yin): ¿el día le suma o le resta?
    dm = "Fuego"
    rel = tibetan.element_relation(dm, s["dia"]["elemento_tallo"])
    return {"filas": rows, "dominante": dominant, "lectura": lectura,
            "day_master_vs_dia": f"Tu Day Master 丁 (Fuego) y el día ({s['dia']['elemento_tallo']}): {rel}"}
