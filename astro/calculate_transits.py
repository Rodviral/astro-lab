#!/usr/bin/env python3
"""
Astrology Week Calculator for Rodrigo
Calculates: Transits, Secondary Progressions, Solar Arc Directions
Natal: 17 Aug 1981, 12:43, Mexico City
"""

import sys
import json
from datetime import datetime, timedelta
from math import floor

try:
    from kerykeion import AstrologicalSubject
except ImportError:
    import subprocess
    subprocess.run([sys.executable, '-m', 'pip', 'install', 'kerykeion==4.26.3', '-q'])  # PATCH: v6 elimina AstrologicalSubject
    from kerykeion import AstrologicalSubject

# ─────────────────────────────────────────────
# NATAL DATA (hardcoded)
# ─────────────────────────────────────────────
NATAL = {
    'name': 'Rodrigo',
    'year': 1981, 'month': 8, 'day': 17,
    'hour': 12, 'minute': 43,
    'lat': 19.4326, 'lng': -99.1332,
    'tz': 'America/Mexico_City'
}

PLANET_LABELS = {
    'Sun': 'Sol', 'Moon': 'Luna', 'Mercury': 'Mercurio',
    'Venus': 'Venus', 'Mars': 'Marte', 'Jupiter': 'Júpiter',
    'Saturn': 'Saturno', 'Uranus': 'Urano', 'Neptune': 'Neptuno',
    'Pluto': 'Plutón', 'ASC': 'ASC', 'MC': 'MC'
}

ASPECT_SYMBOLS = {
    'Conjunction': '☌', 'Sextile': '⚹', 'Square': '□',
    'Trine': '△', 'Opposition': '☍', 'Quincunx': '⚻'
}

SIGN_NAMES = {
    'Ari': 'Aries', 'Tau': 'Tauro', 'Gem': 'Géminis', 'Can': 'Cáncer',
    'Leo': 'Leo', 'Vir': 'Virgo', 'Lib': 'Libra', 'Sco': 'Escorpio',
    'Sag': 'Sagitario', 'Cap': 'Capricornio', 'Aqu': 'Acuario', 'Pis': 'Piscis'
}

SIGN_LIST = ['Ari','Tau','Gem','Can','Leo','Vir','Lib','Sco','Sag','Cap','Aqu','Pis']

# Orbs by planet type
TRANSIT_ORBS = {
    'Pluto': 3, 'Neptune': 3, 'Uranus': 3, 'Saturn': 5,
    'Jupiter': 5, 'Mars': 5, 'Sun': 5, 'Venus': 4,
    'Mercury': 4, 'Moon': 3
}

PROGRESSION_ORBS = 1.5  # tighter orbs for progressions
SOLAR_ARC_ORBS = 1.5

ASPECT_TARGETS = {
    'Conjunction': 0, 'Sextile': 60, 'Square': 90,
    'Trine': 120, 'Quincunx': 150, 'Opposition': 180
}

PLANET_PRIORITY = {
    'Pluto': 1, 'Neptune': 1, 'Uranus': 1, 'Saturn': 1,
    'Jupiter': 2, 'Mars': 2, 'Sun': 3, 'Mercury': 3,
    'Venus': 3, 'Moon': 4
}


def get_aspect(diff, max_orb=8):
    diff = diff % 360
    if diff > 180:
        diff = 360 - diff
    for asp, target in ASPECT_TARGETS.items():
        orb = abs(diff - target)
        if orb <= max_orb:
            return asp, round(orb, 2)
    return None, None


def make_subject(year, month, day, hour=12, minute=0):
    return AstrologicalSubject(
        'point', year, month, day, hour, minute,
        lat=NATAL['lat'], lng=NATAL['lng'],
        tz_str=NATAL['tz'], city='Mexico City'
    )


def get_planet_positions(subject):
    return {
        'Sun': subject.sun['abs_pos'],
        'Moon': subject.moon['abs_pos'],
        'Mercury': subject.mercury['abs_pos'],
        'Venus': subject.venus['abs_pos'],
        'Mars': subject.mars['abs_pos'],
        'Jupiter': subject.jupiter['abs_pos'],
        'Saturn': subject.saturn['abs_pos'],
        'Uranus': subject.uranus['abs_pos'],
        'Neptune': subject.neptune['abs_pos'],
        'Pluto': subject.pluto['abs_pos'],
        'ASC': subject.first_house['abs_pos'],
        'MC': subject.tenth_house['abs_pos'],
    }


def calculate_secondary_progressions(target_date):
    """
    Secondary Progressions: 1 day after birth = 1 year of life.
    Age in years = days to add to birth date.
    """
    # PATCH 2026-11-21: conservar la fracción de día (antes se truncaba a día entero,
    # lo que desplazaba el arco solar ~0.26° y la Luna progresada varios grados).
    birth = datetime(NATAL['year'], NATAL['month'], NATAL['day'], NATAL['hour'], NATAL['minute'])
    target = datetime(target_date.year, target_date.month, target_date.day, NATAL['hour'], NATAL['minute'])
    age_days = (target - birth).total_seconds() / 86400 / 365.2422
    progressed_date = birth + timedelta(days=age_days)
    
    prog = make_subject(
        progressed_date.year, progressed_date.month, progressed_date.day,
        progressed_date.hour, progressed_date.minute
    )
    return get_planet_positions(prog), progressed_date


def calculate_solar_arc(target_date):
    """
    Solar Arc: progressed Sun position - natal Sun position = arc applied to all natal planets.
    """
    natal_sub = make_subject(NATAL['year'], NATAL['month'], NATAL['day'], NATAL['hour'], NATAL['minute'])
    natal_sun = natal_sub.sun['abs_pos']
    
    # PATCH 2026-11-21: conservar la fracción de día (antes se truncaba a día entero,
    # lo que desplazaba el arco solar ~0.26° y la Luna progresada varios grados).
    birth = datetime(NATAL['year'], NATAL['month'], NATAL['day'], NATAL['hour'], NATAL['minute'])
    target = datetime(target_date.year, target_date.month, target_date.day, NATAL['hour'], NATAL['minute'])
    age_days = (target - birth).total_seconds() / 86400 / 365.2422
    
    # Progressed Sun = natal Sun + ~1° per year
    # More precisely: use secondary progression of Sun
    progressed_date = birth + timedelta(days=age_days)
    prog_sub = make_subject(
        progressed_date.year, progressed_date.month, progressed_date.day,
        progressed_date.hour, progressed_date.minute
    )
    solar_arc = (prog_sub.sun['abs_pos'] - natal_sun) % 360
    
    # Apply arc to natal positions
    natal_positions = get_planet_positions(natal_sub)
    solar_arc_positions = {
        planet: (pos + solar_arc) % 360
        for planet, pos in natal_positions.items()
    }
    return solar_arc_positions, round(solar_arc, 2)


def find_aspects(moving_positions, natal_positions, max_orb, layer_label, priority_map=None):
    """Find all aspects between two sets of positions"""
    aspects = []
    for m_planet, m_pos in moving_positions.items():
        if m_planet in ('ASC', 'MC') and layer_label != 'Tránsito':
            continue
        p_orb = max_orb
        if isinstance(max_orb, dict):
            p_orb = max_orb.get(m_planet, 5)
        
        for n_planet, n_pos in natal_positions.items():
            diff = abs(m_pos - n_pos)
            aspect, orb = get_aspect(diff, p_orb)
            if aspect:
                priority = (priority_map or PLANET_PRIORITY).get(m_planet, 3)
                aspects.append({
                    'layer': layer_label,
                    'moving': m_planet,
                    'moving_label': PLANET_LABELS.get(m_planet, m_planet),
                    'aspect': aspect,
                    'aspect_symbol': ASPECT_SYMBOLS.get(aspect, aspect),
                    'natal': n_planet,
                    'natal_label': PLANET_LABELS.get(n_planet, n_planet),
                    'orb': orb,
                    'exact': orb <= 1.0,
                    'priority': priority
                })
    aspects.sort(key=lambda x: (x['priority'], x['orb']))
    return aspects


def get_moon_phase(date):
    """Approximate lunar phase"""
    # Known new moon reference: Jan 29, 2025
    ref_new_moon = datetime(2025, 1, 29)
    lunar_cycle = 29.53059
    days_since = (date - ref_new_moon).days
    phase_day = days_since % lunar_cycle
    
    if phase_day < 1.5: return "🌑 Luna Nueva"
    elif phase_day < 7.4: return "🌒 Cuarto Creciente"
    elif phase_day < 8.9: return "🌓 Primer Cuarto"
    elif phase_day < 14.8: return "🌔 Gibosa Creciente"
    elif phase_day < 16.3: return "🌕 Luna Llena"
    elif phase_day < 22.1: return "🌖 Gibosa Menguante"
    elif phase_day < 23.6: return "🌗 Último Cuarto"
    else: return "🌘 Luna Menguante"


def calculate_week(start_year, start_month, start_day):
    """Full weekly calculation: transits + progressions + solar arcs"""
    
    # Natal baseline
    natal_sub = make_subject(NATAL['year'], NATAL['month'], NATAL['day'], NATAL['hour'], NATAL['minute'])
    natal_positions = get_planet_positions(natal_sub)
    
    start_date = datetime(start_year, start_month, start_day)
    
    result = {
        'week_start': start_date.strftime('%Y-%m-%d'),
        'week_end': (start_date + timedelta(days=6)).strftime('%Y-%m-%d'),
        'natal': {
            k: {'pos': round(v, 2), 'sign': SIGN_NAMES.get(SIGN_LIST[int(v/30) % 12], '?')}
            for k, v in natal_positions.items()
        },
        'days': [],
        'week_summary': {
            'slow_planet_aspects': [],  # Saturno, Urano, Neptuno, Plutón — persistentes toda la semana
            'progression_aspects': [],
            'solar_arc_aspects': [],
            'solar_arc_value': None
        }
    }
    
    # ── Progressions & Solar Arc (weekly, not daily — they barely move) ──
    midweek = start_date + timedelta(days=3)
    prog_positions, prog_date = calculate_secondary_progressions(midweek)
    solar_arc_positions, solar_arc_val = calculate_solar_arc(midweek)
    
    result['week_summary']['solar_arc_value'] = solar_arc_val
    result['week_summary']['progression_date'] = prog_date.strftime('%d %b %Y')
    
    prog_aspects = find_aspects(prog_positions, natal_positions, PROGRESSION_ORBS, 'Progresión Secundaria')
    sa_aspects = find_aspects(solar_arc_positions, natal_positions, SOLAR_ARC_ORBS, 'Arco Solar')
    
    result['week_summary']['progression_aspects'] = prog_aspects[:8]
    result['week_summary']['solar_arc_aspects'] = sa_aspects[:8]
    
    # ── Day-by-day transits ──
    slow_planets = {'Pluto', 'Neptune', 'Uranus', 'Saturn'}
    slow_aspects_seen = set()
    
    for i in range(7):
        day_dt = start_date + timedelta(days=i)
        t = make_subject(day_dt.year, day_dt.month, day_dt.day, 12, 0)
        transit_pos = get_planet_positions(t)
        
        moon_sign_idx = int(transit_pos['Moon'] / 30) % 12
        moon_sign = SIGN_LIST[moon_sign_idx]
        moon_deg = round(transit_pos['Moon'] % 30, 1)
        moon_phase = get_moon_phase(day_dt)
        
        # Get all aspects with per-planet orbs
        all_aspects = find_aspects(transit_pos, natal_positions, TRANSIT_ORBS, 'Tránsito')
        
        # Separate fast vs slow planet aspects
        fast_aspects = [a for a in all_aspects if a['moving'] not in slow_planets]
        slow_aspects = [a for a in all_aspects if a['moving'] in slow_planets]
        
        # Deduplicate slow planet aspects across the week
        for a in slow_aspects:
            key = f"{a['moving']}-{a['aspect']}-{a['natal']}"
            if key not in slow_aspects_seen:
                slow_aspects_seen.add(key)
                result['week_summary']['slow_planet_aspects'].append(a)
        
        day_data = {
            'date': day_dt.strftime('%Y-%m-%d'),
            'day_name': day_dt.strftime('%A'),
            'day_name_es': ['Lunes','Martes','Miércoles','Jueves','Viernes','Sábado','Domingo'][day_dt.weekday()],
            'moon': {
                'sign': moon_sign,
                'sign_full': SIGN_NAMES.get(moon_sign, moon_sign),
                'degree': moon_deg,
                'phase': moon_phase
            },
            'key_aspects': fast_aspects[:4],
            'all_aspects_count': len(all_aspects)
        }
        result['days'].append(day_data)
    
    # Sort week-level slow aspects by orb
    result['week_summary']['slow_planet_aspects'].sort(key=lambda x: x['orb'])
    
    return result


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────
if __name__ == '__main__':
    if len(sys.argv) >= 4:
        y, m, d = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
    else:
        # Default: current week (Monday)
        today = datetime.now()
        days_since_monday = today.weekday()
        monday = today - timedelta(days=days_since_monday)
        y, m, d = monday.year, monday.month, monday.day
    
    data = calculate_week(y, m, d)
    print(json.dumps(data, ensure_ascii=False, indent=2))
