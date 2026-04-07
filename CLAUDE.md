# Tarea 1 - Diseño Sismorresistente | Catálogo Sísmico del Ecuador

## Contexto del proyecto
- **Materia:** Diseño Sismorresistente
- **Docente:** MSc. Miguel Rivera
- **Estudiante:** Pablo Baez — 8vo Nivel "A" — Ing. Civil — PUCE
- **Periodo:** Primer Periodo 2026
- **Repo GitHub:** https://github.com/devilS1n/Tarea1-Sismoresistente
- **Fecha de inicio:** 2026-04-01
- **Última actualización:** 2026-04-07

## Indicación especial del profesor
- **Solo usar el Catálogo Homogeneizado hasta 2009** (mensaje del Ing. Rivera por WhatsApp: "por favor hagan hasta 2009"). No usar los catálogos 2010-2011 ni 2012-2025.

## Estado del proyecto: COMPLETO - Listo para entregar

### Entregables finales
1. **`tarea1_sismoresistente.py`** — Script principal (entrega al profesor)
2. **`Tarea1_DisenoSismorresistente_PabloBaez.pdf`** — Informe exportado a PDF (entrega al profesor)
3. **`csv/CatalogoHomogenizado.txt`** — Datos del catálogo (incluir para que el profesor pueda ejecutar el script)

### Carpeta de entrega
```
Baez_Pablo_Tarea1/
├── tarea1_sismoresistente.py
├── Tarea1_DisenoSismorresistente_PabloBaez.pdf   ← pendiente: exportar Word a PDF
└── csv/
    └── CatalogoHomogenizado.txt
```

## Datos de entrada
- **Archivo:** `csv/CatalogoHomogenizado.txt` (descargado del IGEPN el 2026-04-01)
- **Formato:** CSV con comillas, 16 columnas
- **Columnas clave:** `OBJECTID`, `ID`, `Fecha`, `Latitud`, `Longitud`, `Profundidad`, `Mw`, `AA` (año), `Mes`, `Dia`, `Hora`, `Minuto`, `Segundo`, `Catalogo`, `Fuente`, `Shape`
- **Registros totales:** 10,823
- **Registros con profundidad negativa:** 81 (eliminados — todos IGEPN/FONT, 1997-2007, sismos muy superficiales con error de localización)
- **Registros válidos:** 10,742 eventos (después de filtrar profundidad < 0)
- **Período:** 1901 - 2009
- **Rango Mw:** 3.0 - 8.35
- **Rango Profundidad:** 0 - 418 km
- **Magnitud ya homogeneizada a Mw** — no requiere conversión de tipos de magnitud
- **Referencia:** Beauval, C., et al. (2013). "An Earthquake Catalog for Seismic Hazard Assessment in Ecuador." BSSA, 103(2A), 773-786.
- **Referencia de cita obligatoria:** archivo `csv/DataUse.txt` dentro del RAR descargado del IGEPN
- **Archivo complementario:** `csv/complementhistoriqueJune2013Tab.txt` — eventos históricos desde 1587 (no usado, solo el catálogo principal)

## Estructura de archivos

```
TAREA 1/
├── tarea1_sismoresistente.py    # Script principal con menú interactivo (6 literales)
├── generar_informe.py           # Genera el informe Word automáticamente
├── Tarea1_DisenoSismorresistente_PabloBaez.docx  # Informe Word generado
├── Tarea 1 - Diseño Sismorresistente.pdf          # Enunciado original del profesor
├── Disclaimer_IGEPN.pdf
├── CLAUDE.md                    # Este archivo
├── .gitignore                   # Excluye .rar, __pycache__
├── Baez_Pablo_Tarea1/           # Carpeta de entrega al profesor
├── csv/
│   ├── CatalogoHomogenizado.txt           # DATOS PRINCIPALES
│   ├── complementhistoriqueJune2013Tab.txt
│   ├── Beauval et al 2013.pdf
│   ├── DataUse.txt
│   └── explanations_earthquakeCatalog_Ecuador.pdf
└── figuras/
    ├── literal1_mapa_sismico.png              # Mapa scatter por rangos de Mw
    ├── literal1_mapa_interactivo.html         # Mapa de calor Folium
    ├── literal3_histograma_magnitudes.png     # Histograma 7 intervalos
    ├── literal4_distribucion_magnitudes.png   # Curva normal Mw + P16/P84
    └── literal5_distribucion_profundidades.png # Curva normal Prof + P16/P84
```

## Script principal: tarea1_sismoresistente.py

### Estructura
- **Menú interactivo:** opciones 1-6 para cada literal, 0 para todo, q para salir
- **Función `cargar_catalogo()`:** lee CSV, filtra profundidad >= 0 y Mw >= 3.0
- **6 funciones literales:** `literal_1_mapa_calor()` a `literal_6_conclusiones()`
- **Cada función:** imprime resultados en consola + genera/guarda gráfico PNG + muestra con plt.show()
- **Backend matplotlib:** TkAgg (ventanas emergentes en VS Code)
- **Encoding:** todos los print() usan caracteres ASCII para compatibilidad con terminales Windows (cp1252). Los gráficos de matplotlib sí usan Unicode (μ, σ, °) porque matplotlib lo maneja internamente.

### Librerías instaladas (Python 3.14)
- pandas 2.3.3, numpy 2.4.1, matplotlib 3.10.8, scipy 1.17.1
- folium 0.20.0, geopandas 1.1.3, python-docx 1.2.0
- **cartopy NO disponible** (no compila en Python 3.14 Windows) → se usa geopandas + Natural Earth

### Detalle por literal

| Literal | Función | Gráfico | Notas |
|---------|---------|---------|-------|
| 1 | `literal_1_mapa_calor(df)` | Mapa scatter + mapa Folium HTML | Filtra Mw >= 4, 3 rangos: >7 (rojo), 5-7 (naranja), 4-5 (amarillo). Descarga Natural Earth online. |
| 2 | `literal_2_eventos_relevantes(df)` | Solo texto en consola | Evento más antiguo (1901), mayor Mw (1906, Mw 8.35, Esmeraldas), top 10, interpretación. |
| 3 | `literal_3_histograma(df)` | Histograma barras | 7 intervalos: 4-4.5, 4.5-5, 5-5.5, 5.5-6, 6-6.5, 6.5-7, >7. Etiquetas sobre barras. |
| 4 | `literal_4_estadisticas_magnitud(df)` | Curva normal + líneas verticales | scipy.stats.norm.fit(), líneas: promedio (verde), mediana (azul), P16 y P84 (naranja). Cuadro de estadísticos. |
| 5 | `literal_5_estadisticas_profundidad(df)` | Curva normal + líneas verticales | P16 se limita a >= 0 (profundidad no puede ser negativa). Mismo formato que literal 4. |
| 6 | `literal_6_conclusiones(df)` | Solo texto en consola | 6 conclusiones técnicas sobre sismicidad y peligro sísmico. |

### Comentarios en el código
- **Estilo propio del estudiante:** comentarios cortos, informales, que muestran decisiones propias
- Antes de cada función: `# Literal X: [resumen de lo que pide la tarea]`
- Dentro del código solo donde hay decisión no obvia (4-5 comentarios en todo el script)
- Sin barras decorativas, sin citas APA, sin docstrings largos
- Sin caracteres Unicode en print() (compatibilidad cp1252 Windows)

### Resultados estadísticos clave
- **Magnitudes:** Media=3.69, Mediana=3.40, Desv.Est.=0.70, P16=2.99, P84=4.38
- **Profundidades:** Media=40.2 km, Mediana=18.2 km, Desv.Est.=49.4 km, P16=0.0 km (ajustado de -8.9), P84=89.3 km
- **Distribución por rangos (Mw>=4):** >7: 22 | 5-7: 534 | 4-5: 2581 | Total: 3137
- **Total con Mw>=3:** 10,742 eventos

## Script informe: generar_informe.py

### Estructura
- Replica la carátula PUCE (formato idéntico a `OCTAVO NIVEL/CIMENTACIONES/PRIMER PARCIAL/TAREA 1/Consulta_Terminologia_Cimentaciones.docx`)
- Carátula: Times New Roman 14pt, centrado, negrita en etiquetas
- Contenido: Times New Roman 12pt, interlineado doble, sangría 1.27 cm, justificado
- Títulos nivel 1: centrado negrita | Títulos nivel 2: izquierda negrita
- Márgenes: 2.5 cm (todos)
- Inserta las 4 imágenes PNG de la carpeta `figuras/`
- Incluye tabla de top 10 eventos
- Referencias APA 7 con sangría francesa
- Genera: `Tarea1_DisenoSismorresistente_PabloBaez.docx`

### Correcciones aplicadas al informe (2026-04-07)
1. "mapa de dispersión" → "mapa de calor" (usar terminología del profesor)
2. Eliminado "tal como lo establece el enunciado de la tarea" (no referenciar el enunciado en un informe)
3. "Este mapa se entrega como archivo HTML adjunto" → "se genera automáticamente al ejecutar el script"
4. Eliminado "definidos por el enunciado de la tarea"
5. Números con punto de miles (1.499, 10.742) → sin punto o con espacio (1499, 10 742) para evitar confusión con decimales

## Verificación de literales (2026-04-07)

Todos los literales fueron verificados contra el enunciado de la tarea:

| Literal | Requisito | Estado |
|---------|-----------|--------|
| 1 | Mapa de calor con rangos Mw>7, 5-7, >4 + excluir Mw<3 | APROBADO |
| 2 | Evento más antiguo + mayor magnitud (año, ubicación, provincia) + top eventos + comentarios | APROBADO |
| 3 | Histograma 7 intervalos (4-4.5 a >7) + interpretación | APROBADO |
| 4 | Media, mediana, desv.est. + curva normal + líneas P16, promedio, P84 etiquetadas + interpretación | APROBADO |
| 5 | Media, mediana, desv.est. profundidades + curva normal + líneas P16, promedio, P84 + interpretación | APROBADO |
| 6 | Conclusiones técnicas sobre sismicidad + relación con peligro sísmico | APROBADO |

### Requisitos de entrega verificados
- Script Python con lectura, procesamiento, cálculos y gráficos: OK
- Informe escrito con resultados, figuras e interpretaciones: OK
- Gráficos con título central, nombre de ejes y leyenda: OK

## Posibles mejoras pendientes
- Agregar la relación de Gutenberg-Richter (log N = a - bM) como análisis complementario
- Mejorar la determinación de provincia del evento (actualmente aproximada por coordenadas)
- Incluir un mapa de sección transversal (profundidad vs longitud) para visualizar la subducción
- Si cartopy se hace disponible para Python 3.14, reemplazar geopandas por cartopy para mapas más profesionales
- El mapa descarga Natural Earth online cada ejecución — se podría cachear localmente

## Formato de entrega al profesor
1. **Archivo .py** → el script principal
2. **Archivo .pdf** → el informe Word exportado a PDF desde Word (Archivo → Guardar como → PDF)
3. **Carpeta csv/** → con el catálogo para que el profesor pueda ejecutar el script
