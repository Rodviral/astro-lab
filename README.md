# Astro Lab

Visualizador personal que compara, día a día, tres lentes: **astrología occidental**, **Saju** (cuatro pilares) y **calendario tibetano / Yungdrung Bön**. Corre solo en tu computadora. Proyecto personal, separado del trabajo.

| Lente | Motor | Qué muestra |
|---|---|---|
| Occidental | kerykeion 4.26.3 (mismo script del skill semanal) | Luna, tránsitos lentos y rápidos a la carta natal, timeline 2026-2030 |
| Saju | lunar-python (MIT) | Pilar del día, mes y año; Ten God frente a tu Day Master 丁; Daewoon |
| Tibetano / Bön | caltib (MIT) + `data/bon_rules.yaml` | Día lunar, día sexagenario, elementos, mewa, parkha, práctica sugerida, festividades |
| Puente | `astro/bridge.py` | Qué elemento domina hoy en cada sistema y si coinciden |
| Oráculo Mo | Formulario + skill `sipe-gyalmo-oracle` | Registras tu tirada; la app arma el texto para Claude |

## Prerrequisitos

| Elemento | Detalle |
|---|---|
| Python 3.10+ | `python3 --version` |
| Este repo en tu Mac | `git clone https://github.com/Rodviral/astro-lab` |

## Instalación (una sola vez)

```bash
cd astro-lab
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Uso diario

```bash
cd astro-lab
source .venv/bin/activate
streamlit run app.py
```

Se abre en el navegador (`http://localhost:8501`). Pestañas: **Hoy**, **Mes**, **Timeline 2026-2030**, **Carta comparada**, **Similitudes**, **Diario y oráculo**. El botón "Guardar nota del día" escribe en la carpeta `vault_astro` de `config/natal.yaml`.

## Validación

```bash
python -m pytest -q
```

| Prueba | Criterio |
|---|---|
| Saju natal | 辛酉 · 丙申 · 丁卯 · 丙午 (HANDOFF sección 3) |
| Perfil tibetano | Pájaro de Metal hembra, mewa 1 Blanco |
| Saju vs tibetano | El elemento del día coincide en ambos sistemas (mismo ciclo de 60) |
| Occidental | Semana 2026-11-23: arco solar ≈ 44.02, Saturno ☍ Júpiter orbe ≈ 0.77 |
| Timeline | 166 tránsitos cargados |

**Pendiente manual:** comparar 30 días de "día lunar" y "práctica" con la app **Bon Calendar** (Gyalshen Institute) y luego poner `validado_dias_lunares: true` en `data/bon_rules.yaml`.

## Qué falta llenar (en `data/bon_rules.yaml`)

| Campo | Fuente sugerida |
|---|---|
| `dias_personales` (la / sog / shé) para el signo Pájaro | Shen Calendar Key o app Bon Calendar |
| `perfil_natal` (la, sog, lü, wangthang, lungta) | Tu maestro o un texto de astrología elemental |
| Más festividades | App Bon Calendar |

## Troubleshooting

| Síntoma | Causa | Arreglo |
|---|---|---|
| `ImportError: AstrologicalSubject` | kerykeion v6 | `pip install kerykeion==4.26.3` |
| Día lunar difiere 1 día de la app Bon | Bön vs Phugpa, día doble u omitido | Cambiar `motor_tibetano` en `config/natal.yaml` o anotar la corrección |
| No guarda la nota | Ruta del vault | Revisar `vault_astro` en `config/natal.yaml` |
| Aviso rojo "Saju no coincide" | Cambió la hora natal o la librería | Revisar `config/natal.yaml` |

## Privacidad

El diario de práctica y las consultas Mo se guardan en `diario/`, que está fuera de git. Nada sale de tu equipo.
