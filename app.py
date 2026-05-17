"""
Dashboard de Movilidad Urbana - Medellín

Aplicación principal en Streamlit para análisis de dinámicas urbanas
y patrones de movilidad.

Autor: Equipo de Desarrollo
Fecha: 2024
"""

import streamlit as st
import pandas as pd
from typing import Dict, Any, List

# Importar módulos del sistema
from src.config import (
    PAGE_CONFIG, APP_TITLE, APP_SUBTITLE, APP_ICON,
    VARIABLES_PRINCIPALES, FILTROS_DISPONIBLES, MENSAJES, TOOLTIPS,
    MEDELLIN_CENTER
)
from src.loaders.data_loader import cargar_datos_ejemplo_movilidad
from src.processors.data_processor import (
    aplicar_todos_los_filtros,
    calcular_estadisticas_resumen,
    agregar_columnas_derivadas,
    preparar_datos_para_mapa
)
from src.rules.rule_engine import obtener_motor_reglas
from src.components.ui_components import (
    render_panel_conclusiones,
    render_metrica_kpi,
    render_interruptor_capa,
    render_boton_analisis,
    render_estado_vacio,
    render_separador
)
from src.renderers.map_renderer import (
    renderizar_mapa_interactivo,
    mostrar_mapa_streamlit
)


# =============================================================================
# CONFIGURACIÓN DE PÁGINA
# =============================================================================

st.set_page_config(**PAGE_CONFIG)

# CSS personalizado para styling moderno y limpio
st.markdown("""
<style>
    /* Estilo general */
    .main > div {
        padding-top: 2rem;
    }
    
    /* Títulos */
    h1, h2, h3 {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        color: #2E86AB;
    }
    
    /* Sidebar */
    .sidebar-content {
        background-color: #F8F9FA;
    }
    
    /* Botones */
    .stButton > button {
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    
    /* Tarjetas de métricas */
    .metric-card {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        border-radius: 10px;
        padding: 15px;
        text-align: center;
    }
    
    /* Contenedores */
    .stContainer {
        border-radius: 10px;
        border: 1px solid #DEE2E6;
    }
    
    /* Ocultar menú default de Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Header personalizado */
    .header-custom {
        background: linear-gradient(135deg, #2E86AB 0%, #A23B72 100%);
        color: white;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)


# =============================================================================
# GESTIÓN DE ESTADO DE SESIÓN
# =============================================================================

def inicializar_estado_sesion():
    """Inicializa variables de estado de sesión."""
    if 'datos_cargados' not in st.session_state:
        st.session_state.datos_cargados = None
    
    if 'datos_filtrados' not in st.session_state:
        st.session_state.datos_filtrados = None
    
    if 'conclusiones' not in st.session_state:
        st.session_state.conclusiones = []
    
    if 'analisis_ejecutado' not in st.session_state:
        st.session_state.analisis_ejecutado = False
    
    if 'capas_activas' not in st.session_state:
        st.session_state.capas_activas = {
            'rutas_transporte': True,
            'motivos_viaje': False,
            'horas_embotellamiento': False,
            'flujos_trafico': True,
            'estratificacion_comuna': False
        }
    
    if 'filtros_aplicados' not in st.session_state:
        st.session_state.filtros_aplicados = {}


# =============================================================================
# HEADER PRINCIPAL
# =============================================================================

def render_header():
    """Renderiza el header principal de la aplicación."""
    st.markdown(f"""
    <div class='header-custom'>
        <h1 style='margin: 0; color: white;'>{APP_ICON} {APP_TITLE}</h1>
        <p style='margin: 10px 0 0 0; opacity: 0.9;'>{APP_SUBTITLE}</p>
    </div>
    """, unsafe_allow_html=True)


# =============================================================================
# PANEL LATERAL - CONTROLES Y FILTROS
# =============================================================================

def render_panel_lateral():
    """Renderiza el panel lateral con filtros y controles."""
    with st.sidebar:
        st.markdown("### ⚙️ Configuración")
        render_separador()
        
        # =====================================
        # CONTROL DE CAPAS
        # =====================================
        st.markdown("### 🗺️ Capas del Mapa")
        st.caption("Active/desactive capas de información")
        
        for variable_key, variable_info in VARIABLES_PRINCIPALES.items():
            st.session_state.capas_activas[variable_key] = render_interruptor_capa(
                key=f"capa_{variable_key}",
                nombre=variable_info['nombre'],
                icono=variable_info['icono'],
                descripcion=variable_info['descripcion'],
                valor_default=variable_info.get('capa_default', False)
            )
        
        render_separador()
        
        # =====================================
        # FILTROS
        # =====================================
        st.markdown("### 🔍 Filtros de Análisis")
        st.caption("Configure los parámetros de filtrado")
        
        filtros = {}
        
        # Filtro de Comuna
        comuna_config = FILTROS_DISPONIBLES['comuna']
        filtros['comuna'] = st.multiselect(
            f"{comuna_config['icono']} {comuna_config['nombre']}",
            comuna_config['opciones'],
            default=comuna_config['default'],
            help=comuna_config['descripcion'],
            key="filtro_comuna"
        )
        
        # Filtro de Rango Horario
        rango_config = FILTROS_DISPONIBLES['rango_horario']
        filtros['rango_horario'] = st.selectbox(
            f"🕐 {rango_config['nombre']}",
            rango_config['opciones'],
            index=rango_config['opciones'].index(rango_config['default']),
            help=rango_config['descripcion'],
            key="filtro_rango_horario"
        )
        
        # Filtro de Motivo de Viaje
        motivo_config = FILTROS_DISPONIBLES['motivo_viaje']
        filtros['motivo_viaje'] = st.multiselect(
            f"🎯 {motivo_config['nombre']}",
            motivo_config['opciones'],
            default=motivo_config['default'],
            help=motivo_config['descripcion'],
            key="filtro_motivo_viaje"
        )
        
        # Filtro de Tipo de Ruta
        ruta_config = FILTROS_DISPONIBLES['tipo_ruta']
        filtros['tipo_ruta'] = st.selectbox(
            f"🛣️ {ruta_config['nombre']}",
            ruta_config['opciones'],
            index=ruta_config['opciones'].index(ruta_config['default']),
            help=ruta_config['descripcion'],
            key="filtro_tipo_ruta"
        )
        
        # Filtro de Nivel de Congestión
        congestion_config = FILTROS_DISPONIBLES['nivel_congestion']
        filtros['nivel_congestion'] = st.slider(
            f"🚦 {congestion_config['nombre']}",
            min_value=congestion_config['min'],
            max_value=congestion_config['max'],
            value=congestion_config['default'],
            help=congestion_config['descripcion'],
            key="filtro_nivel_congestion"
        )
        
        render_separador()
        
        # =====================================
        # BOTÓN DE EJECUCIÓN
        # =====================================
        st.markdown("### ▶️ Ejecutar Análisis")
        
        boton_presionado = render_boton_analisis(
            key="btn_ejecutar_analisis",
            label="🔍 Ejecutar Análisis",
            disabled=False,
            tipo="primary"
        )
        
        # Guardar filtros en estado de sesión
        st.session_state.filtros_aplicados = filtros
        
        return boton_presionado, filtros


# =============================================================================
# PANEL DE ESTADÍSTICAS RESUMEN
# =============================================================================

def render_panel_estadisticas(estadisticas: Dict[str, Dict[str, Any]]):
    """Renderiza panel de estadísticas resumen."""
    st.markdown("### 📊 Estadísticas Resumen")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if 'rutas' in estadisticas:
            stats = estadisticas['rutas']
            render_metrica_kpi(
                label="Total Rutas",
                value=stats.get('total_rutas', 0),
                icono="🚌",
                color="#3498DB"
            )
        else:
            render_metrica_kpi(label="Rutas", value="-", icono="🚌")
    
    with col2:
        if 'motivos' in estadisticas:
            stats = estadisticas['motivos']
            render_metrica_kpi(
                label="Viajes Analizados",
                value=stats.get('total_viajes', 0),
                icono="🎯",
                color="#E74C3C"
            )
        else:
            render_metrica_kpi(label="Viajes", value="-", icono="🎯")
    
    with col3:
        if 'embotellamiento' in estadisticas:
            stats = estadisticas['embotellamiento']
            render_metrica_kpi(
                label="Puntos Críticos",
                value=stats.get('puntos_criticos', 0),
                icono="🚦",
                color="#F39C12"
            )
        else:
            render_metrica_kpi(label="Críticos", value="-", icono="🚦")
    
    with col4:
        if 'flujos' in estadisticas:
            stats = estadisticas['flujos']
            render_metrica_kpi(
                label="Sensores Activos",
                value=stats.get('sensores_activos', 0),
                icono="📡",
                color="#9B59B6"
            )
        else:
            render_metrica_kpi(label="Sensores", value="-", icono="📡")


# =============================================================================
# APLICACIÓN PRINCIPAL
# =============================================================================

def main():
    """Función principal de la aplicación."""
    
    # Inicializar estado de sesión
    inicializar_estado_sesion()
    
    # Renderizar header
    render_header()
    
    # =====================================
    # CARGAR DATOS DE EJEMPLO
    # =====================================
    if st.session_state.datos_cargados is None:
        with st.spinner("⏳ Cargando datos de ejemplo..."):
            st.session_state.datos_cargados = cargar_datos_ejemplo_movilidad()
            
            # Enriquecer datos con columnas derivadas
            st.session_state.datos_cargados = agregar_columnas_derivadas(
                st.session_state.datos_cargados
            )
    
    if st.session_state.datos_cargados is None:
        render_estado_vacio(
            titulo="Error al cargar datos",
            mensaje="No fue posible cargar los datos de ejemplo.",
            sugerencias=[
                "Verifique que los archivos CSV estén en la carpeta data/",
                "Reinicie la aplicación",
                "Contacte al administrador del sistema"
            ],
            icono="❌"
        )
        return
    
    # =====================================
    # RENDERIZAR PANEL LATERAL
    # =====================================
    boton_analisis_presionado, filtros_actuales = render_panel_lateral()
    
    # =====================================
    # APLICAR FILTROS
    # =====================================
    datos_filtrados = aplicar_todos_los_filtros(
        st.session_state.datos_cargados,
        filtros_actuales
    )
    
    st.session_state.datos_filtrados = datos_filtrados
    
    # =====================================
    # PREPARAR DATOS PARA MAPA
    # =====================================
    datos_mapa = preparar_datos_para_mapa(
        datos_filtrados,
        st.session_state.capas_activas
    )
    
    # =====================================
    # ÁREA PRINCIPAL - DOS COLUMNAS
    # =====================================
    
    # Columna izquierda: Mapa
    col_mapa, col_resultados = st.columns([2, 1])
    
    with col_mapa:
        st.markdown("### 🗺️ Mapa Interactivo de Medellín")
        
        # Verificar si hay datos para mostrar
        tiene_datos_mapa = any(not df.empty for df in datos_mapa.values())
        
        if tiene_datos_mapa:
            # Renderizar mapa
            mapa = renderizar_mapa_interactivo(
                datos_mapa,
                st.session_state.capas_activas,
                altura="600px"
            )
            
            # Mostrar mapa en Streamlit
            mostrar_mapa_streamlit(mapa)
            
            # Leyenda del mapa
            with st.expander("📖 Ver leyenda del mapa"):
                st.markdown("""
                **Rutas de Transporte:**
                - 🔴 Línea roja: Ruta Principal
                - 🔵 Línea azul: Ruta Secundaria
                - 🟢 Línea verde: Ruta Local
                
                **Niveles de Congestión:**
                - 🔴 Círculo rojo: Congestión Alta (≥75%)
                - 🟠 Círculo naranja: Congestión Media (50-74%)
                - 🟡 Círculo amarillo: Congestión Baja (25-49%)
                - 🟢 Círculo verde: Congestión Mínima (<25%)
                
                **Flujos de Tráfico:**
                - 🟣 Cuadrado morado: Flujo Muy Alto (≥1500 veh/h)
                - 🔴 Cuadrado rojo: Flujo Alto (1000-1499 veh/h)
                - 🔵 Cuadrado azul: Flujo Medio (500-999 veh/h)
                - 🟢 Cuadrado verde: Flujo Bajo (<500 veh/h)
                """)
        else:
            render_estado_vacio(
                titulo="Sin datos en el mapa",
                mensaje="Los filtros aplicados no muestran datos en el mapa.",
                sugerencias=[
                    "Amplíe los rangos de filtrado",
                    "Active más capas de información",
                    "Seleccione diferentes comunas"
                ],
                icono="🗺️"
            )
    
    with col_resultados:
        # =====================================
        # PANEL DE RESULTADOS Y CONCLUSIONES
        # =====================================
        st.markdown("### 📈 Resultados del Análisis")
        
        # Calcular estadísticas resumen
        estadisticas = calcular_estadisticas_resumen(datos_filtrados)
        
        # Mostrar estadísticas compactas
        with st.expander("📊 Ver estadísticas", expanded=False):
            render_panel_estadisticas(estadisticas)
        
        render_separador()
        
        # =====================================
        # MANEJO DEL BOTÓN DE ANÁLISIS
        # =====================================
        if boton_analisis_presionado:
            with st.spinner("⏳ Ejecutando motor de reglas..."):
                # Obtener motor de reglas
                motor = obtener_motor_reglas()
                
                # Ejecutar análisis
                conclusiones = motor.ejecutar_analisis(
                    datos_filtrados,
                    filtros_actuales
                )
                
                # Convertir conclusiones a diccionarios
                st.session_state.conclusiones = [c.to_dict() for c in conclusiones]
                st.session_state.analisis_ejecutado = True
        
        # =====================================
        # MOSTRAR CONCLUSIONES
        # =====================================
        if st.session_state.analisis_ejecutado and st.session_state.conclusiones:
            n_conclusiones = len(st.session_state.conclusiones)
            st.success(f"✅ Se generaron {n_conclusiones} conclusiones")
            
            render_panel_conclusiones(
                st.session_state.conclusiones,
                titulo="Conclusiones"
            )
            
            # Botón para descargar reporte
            if st.button("📥 Descargar reporte", use_container_width=True):
                # Crear texto del reporte
                reporte = "DASHBOARD DE MOVILIDAD URBANA - MEDELLÍN\n"
                reporte += "=" * 60 + "\n\n"
                reporte += "CONCLUSIONES DEL ANÁLISIS\n\n"
                
                for i, conc in enumerate(st.session_state.conclusiones, 1):
                    reporte += f"{i}. {conc['titulo']}\n"
                    reporte += f"   Tipo: {conc['tipo']}\n"
                    reporte += f"   {conc['mensaje']}\n"
                    if conc.get('recomendacion'):
                        reporte += f"   Recomendación: {conc['recomendacion']}\n"
                    reporte += "\n"
                
                st.download_button(
                    label="💾 Descargar TXT",
                    data=reporte,
                    file_name="reporte_movilidad.txt",
                    mime="text/plain",
                    use_container_width=True
                )
        
        elif st.session_state.analisis_ejecutado:
            st.info("ℹ️ No se generaron conclusiones específicas con los filtros actuales.")
        
        else:
            st.info(MENSAJES["esperando_filtros"])
    
    # =====================================
    # INFORMACIÓN ADICIONAL
    # =====================================
    render_separador()
    
    with st.expander("ℹ️ Acerca de este dashboard"):
        st.markdown("""
        ### Dashboard de Movilidad Urbana - Medellín
        
        Esta herramienta permite analizar patrones de movilidad y dinámicas urbanas
        en la ciudad de Medellín, Antioquia.
        
        **Características principales:**
        - 🗺️ Visualización geoespacial interactiva
        - 🔍 Filtros independientes por múltiples variables
        - 🧠 Motor de reglas para generación de conclusiones
        - 📊 Estadísticas resumen en tiempo real
        - 💡 Recomendaciones accionables
        
        **Variables analizadas:**
        - Rutas de transporte público
        - Motivos de viaje
        - Horas de congestión
        - Flujos de tráfico
        - Estratificación por comuna
        
        **Instrucciones de uso:**
        1. Active/desactive las capas deseadas en el mapa
        2. Configure los filtros según su análisis
        3. Presione "Ejecutar Análisis" para obtener conclusiones
        4. Revise las recomendaciones generadas
        
        ---
        
        *Prototipo desarrollado para demostración de capacidades de análisis urbano.*
        """)


# =============================================================================
# PUNTO DE ENTRADA
# =============================================================================

if __name__ == "__main__":
    main()
