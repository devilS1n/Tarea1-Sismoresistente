# ============================================================================
# TAREA 1 - DISEÑO SISMORRESISTENTE
# Análisis del Catálogo Sísmico Homogeneizado del Ecuador (1901-2009)
# Autor: Pablo Baez
# Materia: Diseño Sismorresistente - Ing. Civil - PUCE
# Docente: MSc. Miguel Rivera
# Fecha: Abril 2026
# ============================================================================
# Fuente de datos: Instituto Geofísico de la Escuela Politécnica Nacional
# Referencia: Beauval, C., Yepes, H., Palacios, P., et al. (2013).
#   "An Earthquake Catalog for Seismic Hazard Assessment in Ecuador."
#   Bulletin of the Seismological Society of America, 103(2A), 773-786.
# ============================================================================

import os
import sys
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from scipy import stats
import folium
from folium.plugins import HeatMap
import geopandas as gpd
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# CONFIGURACION GLOBAL
# ============================================================================
# Ruta base del proyecto
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CATALOGO_PATH = os.path.join(BASE_DIR, 'csv', 'CatalogoHomogenizado.txt')
OUTPUT_DIR = os.path.join(BASE_DIR, 'figuras')

# Crear carpeta de figuras si no existe
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Estilo global de matplotlib
plt.rcParams.update({
    'font.family': 'serif',
    'font.serif': ['Times New Roman'],
    'font.size': 11,
    'axes.titlesize': 14,
    'axes.titleweight': 'bold',
    'axes.labelsize': 12,
    'figure.figsize': (10, 7),
    'figure.dpi': 150,
    'savefig.dpi': 300
})


# ============================================================================
# FASE 1: LECTURA Y LIMPIEZA DE DATOS
# ============================================================================
def cargar_catalogo():
    """Carga y limpia el catálogo sísmico homogeneizado."""
    print("\n" + "=" * 60)
    print("  CARGANDO CATÁLOGO SÍSMICO HOMOGENEIZADO (1901-2009)")
    print("=" * 60)

    df = pd.read_csv(CATALOGO_PATH)

    print(f"  Registros totales leídos: {len(df)}")

    # Limpiar profundidades negativas (errores de registro)
    negativos = len(df[df['Profundidad'] < 0])
    if negativos > 0:
        print(f"  Registros con profundidad negativa eliminados: {negativos}")
        df = df[df['Profundidad'] >= 0]

    # Filtrar eventos con Mw >= 3 (según indicación del literal 1)
    antes = len(df)
    df = df[df['Mw'] >= 3.0].copy()
    eliminados = antes - len(df)
    if eliminados > 0:
        print(f"  Registros con Mw < 3 eliminados: {eliminados}")

    print(f"  Registros válidos para análisis: {len(df)}")
    print(f"  Período: {df['AA'].min()} - {df['AA'].max()}")
    print(f"  Rango Mw: {df['Mw'].min():.2f} - {df['Mw'].max():.2f}")
    print(f"  Rango Profundidad: {df['Profundidad'].min():.1f} - {df['Profundidad'].max():.1f} km")
    print("  Catálogo cargado exitosamente.")

    return df


# ============================================================================
# LITERAL 1: ANÁLISIS ESPACIAL DE EVENTOS SÍSMICOS
# ============================================================================
def literal_1_mapa_calor(df):
    """Elabora mapa de calor de eventos sísmicos diferenciado por magnitud."""
    print("\n" + "=" * 60)
    print("  LITERAL 1: ANÁLISIS ESPACIAL DE EVENTOS SÍSMICOS")
    print("=" * 60)

    # Filtrar Mw >= 4 para el mapa (literal indica excluir < 3, pero rangos son >= 4)
    df_mapa = df[df['Mw'] >= 4.0].copy()
    print(f"  Eventos con Mw >= 4 para el mapa: {len(df_mapa)}")

    # Clasificar por rangos de magnitud
    mayor7 = df_mapa[df_mapa['Mw'] >= 7.0]
    entre5y7 = df_mapa[(df_mapa['Mw'] >= 5.0) & (df_mapa['Mw'] < 7.0)]
    mayor4 = df_mapa[(df_mapa['Mw'] >= 4.0) & (df_mapa['Mw'] < 5.0)]

    print(f"  - Magnitud > 7:       {len(mayor7)} eventos")
    print(f"  - Magnitud 5 a 7:     {len(entre5y7)} eventos")
    print(f"  - Magnitud 4 a 5:     {len(mayor4)} eventos")

    # --- MAPA ESTÁTICO CON GEOPANDAS + MATPLOTLIB ---
    print("\n  Generando mapa estático...")

    # Cargar mapa del mundo
    world = gpd.read_file(
        'https://naciscdn.org/naturalearth/110m/cultural/ne_110m_admin_0_countries.zip'
    )
    # Filtrar países de la región
    region = world[world['NAME'].isin([
        'Ecuador', 'Colombia', 'Peru', 'Brazil'
    ])]

    fig, ax = plt.subplots(figsize=(12, 9))

    # Dibujar países
    region.plot(ax=ax, color='#f0f0f0', edgecolor='#333333', linewidth=0.8)

    # Dibujar eventos por categoría (primero los pequeños, luego los grandes)
    ax.scatter(mayor4['Longitud'], mayor4['Latitud'],
               s=15, c='#FFD700', alpha=0.5, edgecolors='#B8860B',
               linewidth=0.3, label=f'Mw 4 - 5 ({len(mayor4)} eventos)', zorder=3)

    ax.scatter(entre5y7['Longitud'], entre5y7['Latitud'],
               s=50, c='#FF8C00', alpha=0.7, edgecolors='#CC4400',
               linewidth=0.4, label=f'Mw 5 - 7 ({len(entre5y7)} eventos)', zorder=4)

    ax.scatter(mayor7['Longitud'], mayor7['Latitud'],
               s=150, c='#DC143C', alpha=0.9, edgecolors='#8B0000',
               linewidth=0.6, label=f'Mw > 7 ({len(mayor7)} eventos)', zorder=5)

    # Configurar límites y etiquetas
    ax.set_xlim(-83, -74)
    ax.set_ylim(-6, 3)
    ax.set_xlabel('Longitud (°)')
    ax.set_ylabel('Latitud (°)')
    ax.set_title('Mapa de Eventos Sísmicos en el Ecuador\n'
                 'Catálogo Homogeneizado (1901-2009) - Magnitud Mw')
    ax.legend(loc='lower left', fontsize=10, framealpha=0.9)
    ax.grid(True, linestyle='--', alpha=0.4)
    ax.set_aspect('equal')

    # Guardar
    ruta_mapa = os.path.join(OUTPUT_DIR, 'literal1_mapa_sismico.png')
    fig.savefig(ruta_mapa)
    print(f"  Mapa estático guardado en: {ruta_mapa}")
    plt.show()

    # --- MAPA INTERACTIVO CON FOLIUM ---
    print("  Generando mapa interactivo (HTML)...")

    mapa = folium.Map(location=[-1.5, -78.5], zoom_start=7,
                      tiles='CartoDB positron')

    # Capa de calor con magnitud como peso
    heat_data = df_mapa[['Latitud', 'Longitud', 'Mw']].values.tolist()
    HeatMap(heat_data, radius=12, blur=8, max_zoom=13,
            min_opacity=0.3, gradient={
                0.2: 'blue', 0.4: 'lime', 0.6: 'yellow',
                0.8: 'orange', 1.0: 'red'
            }).add_to(mapa)

    # Marcar eventos Mw > 7 con círculos individuales
    for _, row in mayor7.iterrows():
        folium.CircleMarker(
            location=[row['Latitud'], row['Longitud']],
            radius=8,
            color='red',
            fill=True,
            fill_opacity=0.8,
            popup=f"Mw {row['Mw']:.1f} | {int(row['AA'])}-{int(row['Mes']):02d}-{int(row['Dia']):02d}"
        ).add_to(mapa)

    ruta_html = os.path.join(OUTPUT_DIR, 'literal1_mapa_interactivo.html')
    mapa.save(ruta_html)
    print(f"  Mapa interactivo guardado en: {ruta_html}")
    print("  (Ábrelo en tu navegador para explorarlo)")


# ============================================================================
# LITERAL 2: IDENTIFICACIÓN DE EVENTOS RELEVANTES
# ============================================================================
def literal_2_eventos_relevantes(df):
    """Identifica eventos más antiguos y de mayor magnitud."""
    print("\n" + "=" * 60)
    print("  LITERAL 2: IDENTIFICACIÓN DE EVENTOS RELEVANTES")
    print("=" * 60)

    # Evento más antiguo
    mas_antiguo = df.loc[df['AA'].idxmin()]
    print("\n  ── EVENTO SÍSMICO MÁS ANTIGUO ──")
    print(f"  Fecha:        {int(mas_antiguo['AA'])}/{int(mas_antiguo['Mes']):02d}/{int(mas_antiguo['Dia']):02d}")
    print(f"  Magnitud Mw:  {mas_antiguo['Mw']:.2f}")
    print(f"  Latitud:      {mas_antiguo['Latitud']:.2f}°")
    print(f"  Longitud:     {mas_antiguo['Longitud']:.2f}°")
    print(f"  Profundidad:  {mas_antiguo['Profundidad']:.1f} km")
    print(f"  Catálogo:     {mas_antiguo['Catalogo']}")
    print(f"  Fuente:       {mas_antiguo['Fuente']}")

    # Evento de mayor magnitud
    mayor_mag = df.loc[df['Mw'].idxmax()]
    print("\n  ── EVENTO SÍSMICO DE MAYOR MAGNITUD ──")
    print(f"  Fecha:        {int(mayor_mag['AA'])}/{int(mayor_mag['Mes']):02d}/{int(mayor_mag['Dia']):02d}")
    print(f"  Magnitud Mw:  {mayor_mag['Mw']:.2f}")
    print(f"  Latitud:      {mayor_mag['Latitud']:.2f}°")
    print(f"  Longitud:     {mayor_mag['Longitud']:.2f}°")
    print(f"  Profundidad:  {mayor_mag['Profundidad']:.1f} km")

    # Determinar provincia aproximada del mayor evento
    lat_mayor = mayor_mag['Latitud']
    lon_mayor = mayor_mag['Longitud']
    if lat_mayor > 0.5 and lon_mayor > -80.5:
        provincia = "Esmeraldas (zona costera norte)"
    elif lat_mayor > 0 and lon_mayor < -80.5:
        provincia = "Zona oceánica frente a Esmeraldas"
    elif lat_mayor < -1 and lon_mayor > -80:
        provincia = "Guayas / Santa Elena"
    else:
        provincia = "Zona costera del Ecuador"
    print(f"  Provincia:    {provincia}")
    print(f"  Catálogo:     {mayor_mag['Catalogo']}")
    print(f"  Fuente:       {mayor_mag['Fuente']}")
    print(f"\n  Nota: Este es el terremoto de Esmeraldas de 1906, uno de los")
    print(f"  más grandes registrados a nivel mundial en el siglo XX.")

    # Top 10 eventos de mayor magnitud
    print("\n  ── TOP 10 EVENTOS DE MAYOR MAGNITUD ──")
    top10 = df.nlargest(10, 'Mw')[['AA', 'Mes', 'Dia', 'Latitud', 'Longitud',
                                     'Profundidad', 'Mw', 'Catalogo', 'Fuente']].copy()
    top10.index = range(1, 11)
    top10.columns = ['Año', 'Mes', 'Día', 'Lat', 'Lon', 'Prof(km)', 'Mw',
                     'Catálogo', 'Fuente']
    print(top10.to_string())

    # Comentarios interpretativos
    print("\n  ── INTERPRETACIÓN ──")
    print("  1. El evento más antiguo del catálogo data de 1901, lo que evidencia")
    print("     que Ecuador cuenta con registros sísmicos instrumentales desde")
    print("     inicios del siglo XX, complementados con datos de catálogos")
    print("     internacionales (CENTENNIAL, ISC).")
    print("  2. El terremoto de mayor magnitud (Mw 8.35, 1906) ocurrió en la zona")
    print("     de subducción frente a Esmeraldas, donde la Placa de Nazca se")
    print("     subduce bajo la Placa Sudamericana. Este evento generó un tsunami.")
    print("  3. Los 10 eventos de mayor magnitud se concentran en la zona costera")
    print("     norte del Ecuador, confirmando que la interfaz de subducción es")
    print("     la principal fuente de peligro sísmico del país.")
    print("  4. Varios de los eventos mayores ocurrieron en la misma zona (lat ~1°N,")
    print("     lon ~79-80°W), lo que sugiere una recurrencia de grandes terremotos")
    print("     en este segmento de la zona de subducción.")


# ============================================================================
# LITERAL 3: ANÁLISIS DE FRECUENCIAS POR INTERVALOS DE MAGNITUD
# ============================================================================
def literal_3_histograma(df):
    """Elabora histograma de frecuencias por intervalos de magnitud."""
    print("\n" + "=" * 60)
    print("  LITERAL 3: ANÁLISIS DE FRECUENCIAS POR INTERVALOS DE MAGNITUD")
    print("=" * 60)

    # Filtrar Mw >= 4 para los intervalos solicitados
    df_hist = df[df['Mw'] >= 4.0].copy()

    # Definir intervalos según la tarea
    intervalos = [4.0, 4.5, 5.0, 5.5, 6.0, 6.5, 7.0, df_hist['Mw'].max() + 0.1]
    etiquetas = ['4.0 - 4.5', '4.5 - 5.0', '5.0 - 5.5', '5.5 - 6.0',
                 '6.0 - 6.5', '6.5 - 7.0', '> 7.0']

    # Contar eventos por intervalo
    conteos = pd.cut(df_hist['Mw'], bins=intervalos, right=False,
                     labels=etiquetas).value_counts().sort_index()

    print("\n  Frecuencia por intervalo de magnitud:")
    print("  " + "-" * 35)
    for etiqueta, conteo in conteos.items():
        print(f"  {etiqueta:>12s}: {conteo:>5d} eventos")
    print("  " + "-" * 35)
    print(f"  {'TOTAL':>12s}: {conteos.sum():>5d} eventos")

    # Crear histograma
    colores = ['#2196F3', '#03A9F4', '#00BCD4', '#FF9800',
               '#FF5722', '#E91E63', '#9C27B0']

    fig, ax = plt.subplots(figsize=(11, 7))

    barras = ax.bar(range(len(etiquetas)), conteos.values,
                    color=colores, edgecolor='black', linewidth=0.8, width=0.75)

    # Etiquetas de frecuencia sobre cada barra
    for barra, conteo in zip(barras, conteos.values):
        ax.text(barra.get_x() + barra.get_width() / 2, barra.get_height() + 15,
                f'{conteo}', ha='center', va='bottom', fontweight='bold', fontsize=11)

    ax.set_xticks(range(len(etiquetas)))
    ax.set_xticklabels(etiquetas, fontsize=11)
    ax.set_xlabel('Intervalo de Magnitud (Mw)')
    ax.set_ylabel('Número de Eventos Sísmicos')
    ax.set_title('Histograma de Frecuencias de Eventos Sísmicos por Magnitud\n'
                 'Catálogo Homogeneizado del Ecuador (1901-2009)')
    ax.grid(axis='y', linestyle='--', alpha=0.4)

    ruta = os.path.join(OUTPUT_DIR, 'literal3_histograma_magnitudes.png')
    fig.savefig(ruta)
    print(f"\n  Histograma guardado en: {ruta}")
    plt.show()

    # Interpretación
    print("\n  ── INTERPRETACIÓN ──")
    print("  1. Se observa una distribución inversamente proporcional entre la")
    print("     magnitud y la frecuencia de eventos: a mayor magnitud, menor")
    print("     cantidad de sismos. Esto es consistente con la ley de")
    print("     Gutenberg-Richter (log N = a - bM).")
    print("  2. El intervalo 4.0-4.5 concentra la mayor cantidad de eventos,")
    print(f"     representando el {conteos.values[0]/conteos.sum()*100:.1f}% del total de sismos con Mw >= 4.")
    print("  3. Los eventos con Mw > 7 son poco frecuentes pero de alto impacto,")
    print(f"     con apenas {conteos.values[-1]} registros en 109 años de observación.")
    print("  4. La distribución refleja el comportamiento típico de una zona de")
    print("     alta sismicidad asociada a un margen de subducción activo.")


# ============================================================================
# LITERAL 4: ANÁLISIS ESTADÍSTICO DE MAGNITUDES
# ============================================================================
def literal_4_estadisticas_magnitud(df):
    """Calcula estadísticas y curva de distribución normal de magnitudes."""
    print("\n" + "=" * 60)
    print("  LITERAL 4: ANÁLISIS ESTADÍSTICO DE MAGNITUDES")
    print("=" * 60)

    magnitudes = df['Mw'].values

    # Estadísticas descriptivas
    media = np.mean(magnitudes)
    mediana = np.median(magnitudes)
    desv_std = np.std(magnitudes, ddof=1)

    print(f"\n  Estadísticas descriptivas de magnitud (Mw):")
    print(f"  {'─' * 40}")
    print(f"  Número de eventos:     {len(magnitudes)}")
    print(f"  Promedio (media):      {media:.4f}")
    print(f"  Mediana:               {mediana:.4f}")
    print(f"  Desviación estándar:   {desv_std:.4f}")
    print(f"  Mínimo:                {magnitudes.min():.2f}")
    print(f"  Máximo:                {magnitudes.max():.2f}")

    # Ajustar distribución normal
    mu_fit, sigma_fit = stats.norm.fit(magnitudes)
    print(f"\n  Parámetros de la distribución normal ajustada:")
    print(f"  μ (media ajustada):    {mu_fit:.4f}")
    print(f"  σ (desv. ajustada):    {sigma_fit:.4f}")

    # Cuantiles
    p16 = stats.norm.ppf(0.16, mu_fit, sigma_fit)
    p84 = stats.norm.ppf(0.84, mu_fit, sigma_fit)
    print(f"\n  Cuantiles:")
    print(f"  P16 (cuantil 16):      {p16:.4f}")
    print(f"  P84 (cuantil 84):      {p84:.4f}")

    # Gráfico
    fig, ax = plt.subplots(figsize=(11, 7))

    # Histograma normalizado
    n, bins_edges, patches = ax.hist(magnitudes, bins=40, density=True,
                                      color='#4FC3F7', edgecolor='black',
                                      linewidth=0.5, alpha=0.7,
                                      label='Datos observados')

    # Curva de distribución normal ajustada
    x = np.linspace(magnitudes.min() - 0.3, magnitudes.max() + 0.3, 300)
    pdf = stats.norm.pdf(x, mu_fit, sigma_fit)
    ax.plot(x, pdf, 'r-', linewidth=2.5, label=f'Normal ajustada (μ={mu_fit:.2f}, σ={sigma_fit:.2f})')

    # Líneas verticales
    ax.axvline(media, color='#2E7D32', linestyle='-', linewidth=2.5,
               label=f'Promedio = {media:.2f}')
    ax.axvline(mediana, color='#1565C0', linestyle='-.', linewidth=2,
               label=f'Mediana = {mediana:.2f}')
    ax.axvline(p16, color='#E65100', linestyle='--', linewidth=2,
               label=f'P16 = {p16:.2f}')
    ax.axvline(p84, color='#E65100', linestyle='--', linewidth=2,
               label=f'P84 = {p84:.2f}')

    ax.set_xlabel('Magnitud (Mw)')
    ax.set_ylabel('Densidad de Probabilidad')
    ax.set_title('Distribución Normal Ajustada a las Magnitudes Sísmicas\n'
                 'Catálogo Homogeneizado del Ecuador (1901-2009)')
    ax.legend(loc='upper right', fontsize=10, framealpha=0.9)
    ax.grid(axis='y', linestyle='--', alpha=0.3)

    # Cuadro de estadísticos
    textstr = (f'n = {len(magnitudes)}\n'
               f'Media = {media:.3f}\n'
               f'Mediana = {mediana:.3f}\n'
               f'σ = {desv_std:.3f}\n'
               f'P16 = {p16:.3f}\n'
               f'P84 = {p84:.3f}')
    props = dict(boxstyle='round', facecolor='wheat', alpha=0.85)
    ax.text(0.02, 0.97, textstr, transform=ax.transAxes, fontsize=10,
            verticalalignment='top', bbox=props)

    ruta = os.path.join(OUTPUT_DIR, 'literal4_distribucion_magnitudes.png')
    fig.savefig(ruta)
    print(f"\n  Gráfico guardado en: {ruta}")
    plt.show()

    # Interpretación
    print("\n  ── INTERPRETACIÓN ──")
    print(f"  1. La magnitud promedio es {media:.2f} Mw con una desviación estándar")
    print(f"     de {desv_std:.2f}, lo que indica que la mayoría de los eventos se")
    print(f"     concentran entre Mw {p16:.2f} (P16) y Mw {p84:.2f} (P84).")
    print(f"  2. La mediana ({mediana:.2f}) es menor que la media ({media:.2f}),")
    print("     lo que indica una distribución con sesgo positivo: existen")
    print("     eventos de gran magnitud que desplazan la media hacia arriba.")
    print("  3. El intervalo entre P16 y P84 contiene aproximadamente el 68%")
    print("     de los eventos, equivalente a ±1σ en una distribución normal.")
    print("  4. La distribución de magnitudes no es perfectamente normal, ya que")
    print("     los catálogos sísmicos suelen seguir una distribución exponencial")
    print("     truncada (ley de Gutenberg-Richter). El ajuste normal es una")
    print("     aproximación estadística útil para describir la tendencia central.")


# ============================================================================
# LITERAL 5: ANÁLISIS ESTADÍSTICO DE PROFUNDIDADES
# ============================================================================
def literal_5_estadisticas_profundidad(df):
    """Calcula estadísticas y curva de distribución normal de profundidades."""
    print("\n" + "=" * 60)
    print("  LITERAL 5: ANÁLISIS ESTADÍSTICO DE PROFUNDIDADES")
    print("=" * 60)

    profundidades = df['Profundidad'].values

    # Estadísticas descriptivas
    media = np.mean(profundidades)
    mediana = np.median(profundidades)
    desv_std = np.std(profundidades, ddof=1)

    print(f"\n  Estadísticas descriptivas de profundidad (km):")
    print(f"  {'─' * 40}")
    print(f"  Número de eventos:     {len(profundidades)}")
    print(f"  Promedio (media):      {media:.4f} km")
    print(f"  Mediana:               {mediana:.4f} km")
    print(f"  Desviación estándar:   {desv_std:.4f} km")
    print(f"  Mínimo:                {profundidades.min():.2f} km")
    print(f"  Máximo:                {profundidades.max():.2f} km")

    # Ajustar distribución normal
    mu_fit, sigma_fit = stats.norm.fit(profundidades)
    print(f"\n  Parámetros de la distribución normal ajustada:")
    print(f"  μ (media ajustada):    {mu_fit:.4f} km")
    print(f"  σ (desv. ajustada):    {sigma_fit:.4f} km")

    # Cuantiles
    p16_raw = stats.norm.ppf(0.16, mu_fit, sigma_fit)
    p16 = max(0, p16_raw)  # La profundidad no puede ser negativa
    p84 = stats.norm.ppf(0.84, mu_fit, sigma_fit)
    print(f"\n  Cuantiles:")
    print(f"  P16 (cuantil 16):      {p16:.4f} km" +
          (f" (ajustado de {p16_raw:.1f} km, la profundidad no puede ser negativa)"
           if p16_raw < 0 else ""))
    print(f"  P84 (cuantil 84):      {p84:.4f} km")

    # Gráfico
    fig, ax = plt.subplots(figsize=(11, 7))

    # Histograma normalizado
    n, bins_edges, patches = ax.hist(profundidades, bins=50, density=True,
                                      color='#81C784', edgecolor='black',
                                      linewidth=0.5, alpha=0.7,
                                      label='Datos observados')

    # Curva de distribución normal ajustada
    x = np.linspace(0, profundidades.max() + 10, 300)
    pdf = stats.norm.pdf(x, mu_fit, sigma_fit)
    ax.plot(x, pdf, 'r-', linewidth=2.5,
            label=f'Normal ajustada (μ={mu_fit:.1f} km, σ={sigma_fit:.1f} km)')

    # Líneas verticales
    ax.axvline(media, color='#2E7D32', linestyle='-', linewidth=2.5,
               label=f'Promedio = {media:.1f} km')
    ax.axvline(mediana, color='#1565C0', linestyle='-.', linewidth=2,
               label=f'Mediana = {mediana:.1f} km')
    ax.axvline(p16, color='#E65100', linestyle='--', linewidth=2,
               label=f'P16 = {p16:.1f} km')
    ax.axvline(p84, color='#E65100', linestyle='--', linewidth=2,
               label=f'P84 = {p84:.1f} km')

    # Limitar eje X a valores positivos
    ax.set_xlim(left=0)

    ax.set_xlabel('Profundidad (km)')
    ax.set_ylabel('Densidad de Probabilidad')
    ax.set_title('Distribución Normal Ajustada a las Profundidades Sísmicas\n'
                 'Catálogo Homogeneizado del Ecuador (1901-2009)')
    ax.legend(loc='upper right', fontsize=10, framealpha=0.9)
    ax.grid(axis='y', linestyle='--', alpha=0.3)

    # Cuadro de estadísticos
    textstr = (f'n = {len(profundidades)}\n'
               f'Media = {media:.1f} km\n'
               f'Mediana = {mediana:.1f} km\n'
               f'σ = {desv_std:.1f} km\n'
               f'P16 = {p16:.1f} km\n'
               f'P84 = {p84:.1f} km')
    props = dict(boxstyle='round', facecolor='wheat', alpha=0.85)
    ax.text(0.97, 0.97, textstr, transform=ax.transAxes, fontsize=10,
            verticalalignment='top', horizontalalignment='right', bbox=props)

    ruta = os.path.join(OUTPUT_DIR, 'literal5_distribucion_profundidades.png')
    fig.savefig(ruta)
    print(f"\n  Gráfico guardado en: {ruta}")
    plt.show()

    # Interpretación
    print("\n  ── INTERPRETACIÓN ──")
    print(f"  1. La profundidad promedio es {media:.1f} km con una desviación")
    print(f"     estándar de {desv_std:.1f} km, reflejando una alta dispersión")
    print("     en las profundidades de los eventos sísmicos.")
    print(f"  2. La mediana ({mediana:.1f} km) es considerablemente menor que la")
    print(f"     media ({media:.1f} km), lo que indica una distribución fuertemente")
    print("     sesgada hacia profundidades someras: la mayoría de los sismos")
    print("     ocurren a profundidades relativamente superficiales.")
    print("  3. Esto es coherente con el contexto tectónico del Ecuador, donde")
    print("     los sismos corticales (0-30 km) asociados a fallas activas de la")
    print("     Sierra y los sismos de la interfaz de subducción (30-60 km) son")
    print("     los más frecuentes.")
    print("  4. Los sismos profundos (>200 km) corresponden a la zona de Wadati-")
    print("     Benioff, donde la Placa de Nazca se hunde bajo el continente.")


# ============================================================================
# LITERAL 6: CONCLUSIONES TÉCNICAS
# ============================================================================
def literal_6_conclusiones(df):
    """Presenta conclusiones técnicas sobre la sismicidad del Ecuador."""
    print("\n" + "=" * 60)
    print("  LITERAL 6: CONCLUSIONES TÉCNICAS")
    print("=" * 60)

    # Calcular datos para las conclusiones
    total = len(df)
    mayor7 = len(df[df['Mw'] >= 7])
    mayor6 = len(df[df['Mw'] >= 6])
    prof_media = df['Profundidad'].mean()
    mag_media = df['Mw'].mean()

    print(f"""
  ── CONCLUSIONES ──

  1. SISMICIDAD ELEVADA Y SOSTENIDA
     El catálogo homogeneizado registra {total:,} eventos sísmicos con Mw >= 3.0
     en el período 1901-2009, con {mayor7} eventos de magnitud Mw >= 7.0 y {mayor6}
     de Mw >= 6.0. Esto evidencia que el Ecuador se encuentra en una de las
     zonas de mayor actividad sísmica del planeta.

  2. DOMINIO DE LA SUBDUCCIÓN
     Los eventos de mayor magnitud se concentran en la zona costera norte
     (Esmeraldas, Manabí), asociados a la interfaz de subducción entre la
     Placa de Nazca y la Placa Sudamericana. El terremoto de 1906 (Mw 8.35)
     y sus réplicas mayores confirman el potencial destructivo de esta fuente.

  3. DISTRIBUCIÓN DE PROFUNDIDADES
     La profundidad promedio de {prof_media:.1f} km y la predominancia de sismos
     superficiales (<70 km) indican que la mayor parte de la sismicidad se
     genera en la corteza y en la interfaz de subducción, donde los efectos
     en superficie son más severos.

  4. COMPORTAMIENTO ESTADÍSTICO
     La distribución de magnitudes sigue el patrón de Gutenberg-Richter: alta
     frecuencia de eventos pequeños y baja frecuencia de eventos grandes. La
     magnitud promedio de {mag_media:.2f} Mw refleja el umbral de detección del
     catálogo homogeneizado.

  5. RELACIÓN CON EL PELIGRO SÍSMICO
     Los resultados justifican la clasificación del Ecuador como país de alto
     peligro sísmico en la NEC-SE-DS. La recurrencia de grandes terremotos
     en la zona de subducción y la presencia de fallas activas en la Sierra
     (como la falla de Quito) demandan un diseño sismorresistente riguroso
     en todas las edificaciones del territorio nacional.

  6. IMPORTANCIA DEL CATÁLOGO
     El catálogo homogeneizado de Beauval et al. (2013) constituye una
     herramienta fundamental para el análisis de peligro sísmico probabilístico
     (PSHA) en el Ecuador, al unificar múltiples fuentes y estandarizar las
     magnitudes a Mw, permitiendo análisis estadísticos consistentes.
  """)


# ============================================================================
# MENÚ PRINCIPAL
# ============================================================================
def mostrar_menu():
    """Muestra el menú interactivo de opciones."""
    print("\n")
    print("═" * 60)
    print("  TAREA 1 - DISEÑO SISMORRESISTENTE")
    print("  Catálogo Sísmico del Ecuador (1901-2009)")
    print("  Pablo Baez - 8vo Nivel - PUCE")
    print("═" * 60)
    print("  [1] Mapa de calor de eventos sísmicos")
    print("  [2] Identificación de eventos relevantes")
    print("  [3] Histograma de frecuencias por magnitud")
    print("  [4] Análisis estadístico de magnitudes")
    print("  [5] Análisis estadístico de profundidades")
    print("  [6] Conclusiones técnicas")
    print("  [0] Ejecutar TODO")
    print("  [q] Salir")
    print("═" * 60)


def ejecutar_literal(opcion, df):
    """Ejecuta el literal seleccionado."""
    funciones = {
        '1': literal_1_mapa_calor,
        '2': literal_2_eventos_relevantes,
        '3': literal_3_histograma,
        '4': literal_4_estadisticas_magnitud,
        '5': literal_5_estadisticas_profundidad,
        '6': literal_6_conclusiones,
    }

    if opcion == '0':
        for key in ['1', '2', '3', '4', '5', '6']:
            funciones[key](df)
        print("\n" + "=" * 60)
        print("  TODOS LOS LITERALES EJECUTADOS EXITOSAMENTE")
        print(f"  Figuras guardadas en: {OUTPUT_DIR}")
        print("=" * 60)
    elif opcion in funciones:
        funciones[opcion](df)
    else:
        print("  Opción no válida.")


def main():
    """Función principal del programa."""
    # Cargar datos una sola vez
    df = cargar_catalogo()

    while True:
        mostrar_menu()
        opcion = input("  Seleccione una opción: ").strip().lower()

        if opcion == 'q':
            print("\n  Programa finalizado. ¡Éxito con la tarea!")
            break
        else:
            ejecutar_literal(opcion, df)
            input("\n  Presione Enter para continuar...")


if __name__ == '__main__':
    main()
