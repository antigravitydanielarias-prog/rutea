"""
Configuración global del dashboard de movilidad urbana.

Este módulo centraliza todas las constantes, configuraciones y parámetros
del sistema para facilitar mantenimiento y escalabilidad.
"""

# =============================================================================
# CONFIGURACIÓN DE LA APLICACIÓN
# =============================================================================

APP_TITLE = "Dashboard de Movilidad Urbana - Medellín"
APP_SUBTITLE = "Análisis inteligente de dinámicas urbanas y patrones de movilidad"
APP_ICON = "🏙️"

# Configuración de página Streamlit
PAGE_CONFIG = {
    "page_title": APP_TITLE,
    "page_icon": APP_ICON,
    "layout": "wide",
    "initial_sidebar_state": "expanded"
}

# =============================================================================
# CONFIGURACIÓN GEOGRÁFICA (MEDELLÍN)
# =============================================================================

# Coordenadas centrales de Medellín
MEDELLIN_CENTER = {
    "lat": 6.2442,
    "lon": -75.5812
}

ZOOM_DEFAULT = 12
ZOOM_MIN = 10
ZOOM_MAX = 18

# Límites aproximados de Medellín
MEDELLIN_BOUNDS = {
    "north": 6.3500,
    "south": 6.1500,
    "east": -75.4500,
    "west": -75.7000
}

# =============================================================================
# VARIABLES URBANAS PRINCIPALES
# =============================================================================

VARIABLES_PRINCIPALES = {
    "rutas_transporte": {
        "nombre": "Rutas de Transporte",
        "descripcion": "Red de rutas de transporte público y vías principales",
        "icono": "🚌",
        "capa_default": True
    },
    "motivos_viaje": {
        "nombre": "Motivos de Viaje",
        "descripcion": "Propósito principal de los desplazamientos urbanos",
        "icono": "🎯",
        "capa_default": False
    },
    "horas_embotellamiento": {
        "nombre": "Horas de Congestión",
        "descripcion": "Puntos críticos de congestión por rango horario",
        "icono": "🚦",
        "capa_default": False
    },
    "flujos_trafico": {
        "nombre": "Flujos de Tráfico",
        "descripcion": "Intensidad vehicular en vías principales",
        "icono": "🚗",
        "capa_default": True
    },
    "estratificacion_comuna": {
        "nombre": "Estratificación por Comuna",
        "descripcion": "División administrativa y estratificación socioeconómica",
        "icono": "🏘️",
        "capa_default": False
    }
}

# =============================================================================
# FILTROS DISPONIBLES
# =============================================================================

FILTROS_DISPONIBLES = {
    "comuna": {
        "nombre": "Comuna",
        "tipo": "multiselect",
        "opciones": [
            "Comuna 1 - Popular",
            "Comuna 2 - Santa Cruz",
            "Comuna 3 - Manrique",
            "Comuna 4 - Aranjuez",
            "Comuna 5 - Castilla",
            "Comuna 6 - Doce de Octubre",
            "Comuna 7 - Robledo",
            "Comuna 8 - Villa Hermosa",
            "Comuna 9 - Buenos Aires",
            "Comuna 10 - La Candelaria",
            "Comuna 11 - Laureles",
            "Comuna 12 - La América",
            "Comuna 13 - San Javier",
            "Comuna 14 - El Poblado",
            "Comuna 15 - Guayabal",
            "Comuna 16 - Belén"
        ],
        "default": None,
        "descripcion": "Seleccione una o más comunas para analizar"
    },
    "rango_horario": {
        "nombre": "Rango Horario",
        "tipo": "selectbox",
        "opciones": [
            "Todo el día",
            "Madrugada (00:00 - 05:59)",
            "Mañana Temprano (06:00 - 08:59)",
            "Mañana (09:00 - 11:59)",
            "Mediodía (12:00 - 13:59)",
            "Tarde (14:00 - 17:59)",
            "Hora Pico PM (18:00 - 20:59)",
            "Noche (21:00 - 23:59)"
        ],
        "default": "Todo el día",
        "descripcion": "Filtrar por período del día"
    },
    "motivo_viaje": {
        "nombre": "Motivo de Viaje",
        "tipo": "multiselect",
        "opciones": [
            "Trabajo",
            "Estudio",
            "Salud",
            "Compras",
            "Ocio/Recreación",
            "Trámites",
            "Visitas",
            "Otros"
        ],
        "default": None,
        "descripcion": "Propósito principal del desplazamiento"
    },
    "tipo_ruta": {
        "nombre": "Tipo de Ruta",
        "tipo": "selectbox",
        "opciones": [
            "Todas",
            "Principal",
            "Secundaria",
            "Local",
            "Peatonal"
        ],
        "default": "Todas",
        "descripcion": "Clasificación vial de la ruta"
    },
    "nivel_congestion": {
        "nombre": "Nivel de Congestión",
        "tipo": "slider",
        "min": 0,
        "max": 100,
        "default": [0, 100],
        "descripcion": "Filtrar por porcentaje de congestión"
    }
}

# =============================================================================
# UMBRALES PARA MOTOR DE REGLAS
# =============================================================================

UMBRALES = {
    "congestion_alta": 75,
    "congestion_media": 50,
    "congestion_baja": 25,
    "flujo_alto": 80,
    "flujo_medio": 50,
    "desviacion_tipica": 1.5,  # Desviaciones estándar para detectar atípicos
    "hora_pico_manana": {"inicio": 6, "fin": 9},
    "hora_pico_tarde": {"inicio": 17, "fin": 20}
}

# =============================================================================
# ESTADOS DE CONCLUSIÓN
# =============================================================================

ESTADOS_CONCLUSION = {
    "normal": {
        "icono": "✅",
        "color": "#28a745",
        "etiqueta": "Normal"
    },
    "alerta": {
        "icono": "⚠️",
        "color": "#ffc107",
        "etiqueta": "Alerta"
    },
    "critico": {
        "icono": "🔴",
        "color": "#dc3545",
        "etiqueta": "Crítico"
    },
    "atipico": {
        "icono": "📊",
        "color": "#17a2b8",
        "etiqueta": "Comportamiento Atípico"
    },
    "tendencia": {
        "icono": "📈",
        "color": "#6f42c1",
        "etiqueta": "Tendencia Detectada"
    },
    "recomendacion": {
        "icono": "💡",
        "color": "#20c997",
        "etiqueta": "Recomendación"
    }
}

# =============================================================================
# PALETA DE COLORES
# =============================================================================

PALETA_COLORES = {
    "primario": "#2E86AB",
    "secundario": "#A23B72",
    "terciario": "#F18F01",
    "fondo": "#F8F9FA",
    "borde": "#DEE2E6",
    "texto": "#212529",
    "texto_suave": "#6C757D",
    "exito": "#28a745",
    "advertencia": "#ffc107",
    "peligro": "#dc3545",
    "informacion": "#17a2b8"
}

# =============================================================================
# RUTAS DE ARCHIVOS
# =============================================================================

RUTA_DATOS = "data"
RUTA_CACHE = ".cache"
ARCHIVOS_SOPORTADOS = [".csv", ".geojson", ".json", ".xlsx"]

# =============================================================================
# CONFIGURACIÓN DE RENDIMIENTO
# =============================================================================

CACHE_TTL = 3600  # Tiempo de vida del caché en segundos
MAX_REGISTROS_VISTA = 10000  # Límite de registros para visualización
HABILITAR_CACHE = True

# =============================================================================
# MENSAJES DEL SISTEMA
# =============================================================================

MENSAJES = {
    "bienvenida": """
    ### 👋 Bienvenido al Dashboard de Movilidad Urbana
    
    Esta herramienta le permite analizar patrones de movilidad en Medellín,
    detectar comportamientos atípicos y generar conclusiones accionables.
    
    **Instrucciones rápidas:**
    1. Active/desactive capas en el mapa
    2. Aplique filtros según su análisis
    3. Presione **Ejecutar análisis** para obtener conclusiones
    """,
    "sin_datos": """
    ### 📭 No hay datos disponibles
    
    No se encontraron datos que coincidan con los filtros seleccionados.
    
    **Sugerencias:**
    - Amplíe los rangos de filtrado
    - Verifique que haya datos cargados
    - Revise la configuración de capas
    """,
    "analisis_completado": """
    ### ✅ Análisis Completado
    
    Se han generado {n} conclusiones basadas en los filtros aplicados.
    Revise las recomendaciones y alertas detectadas.
    """,
    "error_carga": """
    ### ❌ Error al cargar datos
    
    No fue posible cargar el archivo seleccionado.
    
    **Verifique:**
    - El formato del archivo es compatible
    - El archivo no está corrupto
    - Las columnas requeridas están presentes
    """,
    "cargando": "⏳ Procesando análisis...",
    "esperando_filtros": "👈 Seleccione filtros y presione 'Ejecutar análisis'"
}

# =============================================================================
# CONFIGURACIÓN DE TOOLTIPS
# =============================================================================

TOOLTIPS = {
    "ejecutar_analisis": "Ejecuta el motor de reglas sobre los filtros seleccionados para generar conclusiones",
    "resetear_filtros": "Limpia todos los filtros aplicados y restablece valores por defecto",
    "activar_capa": "Mostrar/ocultar esta capa en el mapa",
    "info_variable": "Ver información detallada sobre esta variable urbana"
}
