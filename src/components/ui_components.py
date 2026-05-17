"""
Componentes UI reutilizables para el dashboard de movilidad urbana.

Este módulo contiene componentes visuales que pueden ser reutilizados
en diferentes partes de la aplicación, manteniendo consistencia visual.
"""

import streamlit as st
from typing import Dict, Any, List, Optional
from src.config import ESTADOS_CONCLUSION, PALETA_COLORES


def render_tarjeta_conclusion(conclusion: Dict[str, Any], index: int = 0) -> None:
    """
    Renderiza una tarjeta de conclusión con estilo visual jerárquico.
    
    Args:
        conclusion: Diccionario con datos de la conclusión
        index: Índice para generar keys únicos
    """
    tipo = conclusion.get("tipo", "normal")
    estado = ESTADOS_CONCLUSION.get(tipo, ESTADOS_CONCLUSION["normal"])
    
    # Crear contenedor con borde coloreado según el tipo
    color = estado.get("color", "#6C757D")
    icono = estado.get("icono", "📄")
    etiqueta = estado.get("etiqueta", "Información")
    
    # Usar columns para layout
    col_icono, col_contenido = st.columns([0.1, 0.9])
    
    with col_icono:
        st.markdown(f"<div style='font-size: 2em;'>{icono}</div>", unsafe_allow_html=True)
    
    with col_contenido:
        # Título con badge de tipo
        st.markdown(
            f"""
            <div style='
                background-color: {color}20;
                border-left: 4px solid {color};
                padding: 10px 15px;
                border-radius: 5px;
                margin: 10px 0;
            '>
                <span style='
                    background-color: {color};
                    color: white;
                    padding: 3px 8px;
                    border-radius: 3px;
                    font-size: 0.8em;
                    font-weight: bold;
                '>{etiqueta}</span>
                <h3 style='margin: 10px 0 5px 0; color: {color};'>
                    {conclusion.get("titulo", "Conclusión")}
                </h3>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    # Mensaje principal
    st.markdown(f"**{conclusion.get('mensaje', '')}**")
    
    # Contexto si está disponible
    if conclusion.get("contexto"):
        st.info(f"📍 **Contexto:** {conclusion['contexto']}")
    
    # Recomendación si está disponible
    if conclusion.get("recomendacion"):
        st.success(f"💡 **Recomendación:** {conclusion['recomendacion']}")
    
    # Separador
    st.markdown("---")


def render_panel_conclusiones(
    conclusiones: List[Dict[str, Any]], 
    titulo: str = "Conclusiones del Análisis"
) -> None:
    """
    Renderiza un panel completo de conclusiones.
    
    Args:
        conclusiones: Lista de conclusiones a mostrar
        titulo: Título del panel
    """
    if not conclusiones:
        st.info("👈 Ejecute un análisis para ver las conclusiones")
        return
    
    st.subheader(titulo)
    
    # Mostrar número de conclusiones
    n_conclusiones = len(conclusiones)
    st.caption(f"{n_conclusiones} {'conclusión' if n_conclusiones == 1 else 'conclusiones'} generada{'s' if n_conclusiones > 1 else ''}")
    
    # Renderizar cada conclusión
    for i, conclusion in enumerate(conclusiones):
        render_tarjeta_conclusion(conclusion, i)


def render_metrica_kpi(
    label: str,
    value: Any,
    delta: Optional[str] = None,
    icono: str = "📊",
    color: str = "#2E86AB"
) -> None:
    """
    Renderiza una métrica KPI estilizada.
    
    Args:
        label: Etiqueta descriptiva
        value: Valor de la métrica
        delta: Cambio o variación (opcional)
        icono: Emoji o ícono
        color: Color principal
    """
    st.markdown(
        f"""
        <div style='
            background: linear-gradient(135deg, {color}15, {color}05);
            border: 1px solid {color}40;
            border-radius: 10px;
            padding: 15px;
            text-align: center;
        '>
            <div style='font-size: 1.5em; margin-bottom: 5px;'>{icono}</div>
            <div style='color: {PALETA_COLORES["texto_suave"]}; font-size: 0.9em;'>{label}</div>
            <div style='color: {color}; font-size: 1.8em; font-weight: bold; margin: 5px 0;'>
                {value}
            </div>
            {f"<div style='color: {'#28a745' if '+' in delta else '#dc3545'}; font-size: 0.9em;'>{delta}</div>" if delta else ""}
        </div>
        """,
        unsafe_allow_html=True
    )


def render_filtro_selectbox(
    key: str,
    nombre: str,
    opciones: List[str],
    valor_default: Any = None,
    descripcion: str = "",
    ayuda: str = ""
) -> Any:
    """
    Renderiza un filtro tipo selectbox con styling consistente.
    
    Args:
        key: Key único para Streamlit
        nombre: Nombre visible del filtro
        opciones: Lista de opciones disponibles
        valor_default: Valor por defecto
        descripcion: Descripción corta
        ayuda: Texto de ayuda tooltip
        
    Returns:
        Valor seleccionado
    """
    st.markdown(f"**{nombre}**")
    if descripcion:
        st.caption(descripcion)
    
    valor = st.selectbox(
        f"Seleccione {nombre.lower()}",
        opciones,
        index=opciones.index(valor_default) if valor_default in opciones else 0,
        key=key,
        help=ayuda
    )
    
    return valor


def render_filtro_multiselect(
    key: str,
    nombre: str,
    opciones: List[str],
    valor_default: Optional[List[str]] = None,
    descripcion: str = "",
    ayuda: str = ""
) -> Any:
    """
    Renderiza un filtro tipo multiselect con styling consistente.
    
    Args:
        key: Key único para Streamlit
        nombre: Nombre visible del filtro
        opciones: Lista de opciones disponibles
        valor_default: Valores por defecto
        descripcion: Descripción corta
        ayuda: Texto de ayuda tooltip
        
    Returns:
        Lista de valores seleccionados
    """
    st.markdown(f"**{nombre}**")
    if descripcion:
        st.caption(descripcion)
    
    valor = st.multiselect(
        f"Seleccione {nombre.lower()} (opcional)",
        opciones,
        default=valor_default if valor_default else [],
        key=key,
        help=ayuda
    )
    
    return valor


def render_filtro_slider(
    key: str,
    nombre: str,
    min_val: int,
    max_val: int,
    valor_default: tuple = None,
    descripcion: str = "",
    ayuda: str = ""
) -> Any:
    """
    Renderiza un filtro tipo slider range con styling consistente.
    
    Args:
        key: Key único para Streamlit
        nombre: Nombre visible del filtro
        min_val: Valor mínimo del rango
        max_val: Valor máximo del rango
        valor_default: Tupla con valores inicial y final
        descripcion: Descripción corta
        ayuda: Texto de ayuda tooltip
        
    Returns:
        Tupla con valores del rango seleccionado
    """
    st.markdown(f"**{nombre}**")
    if descripcion:
        st.caption(descripcion)
    
    valor = st.slider(
        f"Rango de {nombre.lower()}",
        min_value=min_val,
        max_value=max_val,
        value=valor_default if valor_default else (min_val, max_val),
        key=key,
        help=ayuda
    )
    
    return valor


def render_interruptor_capa(
    key: str,
    nombre: str,
    icono: str,
    descripcion: str,
    valor_default: bool = True
) -> bool:
    """
    Renderiza un interruptor para activar/desactivar capas del mapa.
    
    Args:
        key: Key único para Streamlit
        nombre: Nombre de la capa
        icono: Emoji o ícono representativo
        descripcion: Descripción de la capa
        valor_default: Estado inicial
        
    Returns:
        True si la capa está activa, False en caso contrario
    """
    return st.toggle(
        f"{icono} {nombre}",
        value=valor_default,
        key=key,
        help=descripcion
    )


def render_boton_analisis(
    key: str = "ejecutar_analisis",
    label: str = "🔍 Ejecutar Análisis",
    disabled: bool = False,
    tipo: str = "primary"
) -> bool:
    """
    Renderiza el botón principal de ejecución de análisis.
    
    Args:
        key: Key único para Streamlit
        label: Texto del botón
        disabled: Si el botón está deshabilitado
        tipo: Tipo de botón (primary, secondary, etc.)
        
    Returns:
        True si el botón fue presionado
    """
    return st.button(
        label,
        key=key,
        disabled=disabled,
        type=tipo,
        use_container_width=True,
        help="Ejecuta el motor de reglas sobre los filtros seleccionados para generar conclusiones"
    )


def render_estado_vacio(
    titulo: str = "Sin datos disponibles",
    mensaje: str = "",
    sugerencias: Optional[List[str]] = None,
    icono: str = "📭"
) -> None:
    """
    Renderiza un estado vacío informativo.
    
    Args:
        titulo: Título del estado
        mensaje: Mensaje explicativo
        sugerencias: Lista de sugerencias para el usuario
        icono: Emoji o ícono
    """
    st.markdown(
        f"""
        <div style='
            text-align: center;
            padding: 40px 20px;
            color: {PALETA_COLORES["texto_suave"]};
        '>
            <div style='font-size: 3em; margin-bottom: 20px;'>{icono}</div>
            <h3 style='color: {PALETA_COLORES["texto"]};'>{titulo}</h3>
            {f"<p>{mensaje}</p>" if mensaje else ""}
        </div>
        """,
        unsafe_allow_html=True
    )
    
    if sugerencias:
        st.markdown("**Sugerencias:**")
        for sugerencia in sugerencias:
            st.markdown(f"- {sugerencia}")


def render_loader(mensaje: str = "Cargando...") -> None:
    """
    Renderiza un indicador de carga.
    
    Args:
        mensaje: Mensaje a mostrar durante la carga
    """
    with st.spinner(mensaje):
        pass


def render_tooltip(texto: str, icono: str = "ℹ️") -> None:
    """
    Renderiza un tooltip informativo.
    
    Args:
        texto: Texto del tooltip
        icono: Ícono del tooltip
    """
    st.caption(f"{icono} {texto}")


def render_separador(color: str = "#DEE2E6") -> None:
    """
    Renderiza un separador visual estilizado.
    
    Args:
        color: Color del separador
    """
    st.markdown(f"<hr style='border: 1px solid {color};'>", unsafe_allow_html=True)
