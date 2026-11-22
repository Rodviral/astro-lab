# Astro Lab — instrucciones para Claude

Proyecto personal de Rodrigo (astrología comparada + Yungdrung Bön). No mezclar con Okra, DItia ni el knowledge graph laboral.

- **Calcular, no recordar.** Toda posición, pilar o fecha lunar sale del código (`astro/`). Claude narra y compara; nunca inventa un día de práctica ni un elemento.
- **Reglas Bön** viven en `data/bon_rules.yaml`, en español. Lo marcado `validado: false` se presenta como sugerencia, no como regla. La última palabra es del lama de Rodrigo.
- **Oráculo Mo:** el ritual y la tirada los hace Rodrigo. Claude solo interpreta con el skill `sipe-gyalmo-oracle`. Las consultas se quedan en `diario/` (fuera de git).
- **Estilo:** español, términos técnicos en inglés. Tablas > bullets > prosa. Antideterminista.
- **Validación:** `python -m pytest -q` debe pasar antes de cualquier cambio.
- kerykeion fijado en 4.26.3 (la v6 rompe `calculate_transits.py`).
