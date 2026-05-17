"""
Renderizador de mapa interactivo para el dashboard de movilidad urbana.

Este módulo maneja la visualización geoespacial usando OpenStreetMap
a través de la librería folium, integrada con Streamlit.
"""

import folium
import pandas as pd
from typing import Dict, Any, List, Optional, Tuple
from streamlit_folium import st_folium
from src.config import MEDELLIN_CENTER, ZOOM_DEFAULT, PALETA_COLORES


def crear_mapa_base(
    centro: Tuple[float, float] = None,
    zoom: int = None,
    width: str = "100%",
    height: str = "600px"
) -> folium.Map:
    """
    Crea un mapa base de OpenStreetMap centrado en Medellín.
    
    Args:
        centro: Tupla (latitud, longitud) del centro del mapa
        zoom: Nivel de zoom inicial
        width: Ancho del mapa
        height: Alto del mapa
        
    Returns:
        Objeto folium.Map configurado
    """
    centro = centro or (MEDELLIN_CENTER["lat"], MEDELLIN_CENTER["lon"])
    zoom = zoom or ZOOM_DEFAULT
    
    mapa = folium.Map(
        location=centro,
        zoom_start=zoom,
        tiles="OpenStreetMap",
        width=width,
        height=height,
        prefer_canvas=True
    )
    
    return mapa


def agregar_capa_rutas(
    mapa: folium.Map,
    datos_rutas: pd.DataFrame,
    color_por_tipo: Optional[Dict[str, str]] = None
) -> folium.Map:
    """
    Agrega capa de rutas de transporte al mapa.
    
    Args:
        mapa: Mapa folium base
        datos_rutas: DataFrame con información de rutas
        color_por_tipo: Diccionario mapeando tipo de ruta a color
        
    Returns:
        Mapa con las rutas agregadas
    """
    if datos_rutas.empty:
        return mapa
    
    # Colores por tipo de ruta
    colores_default = {
        "Principal": "#E74C3C",
        "Secundaria": "#3498DB",
        "Local": "#2ECC71",
        "Peatonal": "#9B59B6"
    }
    colores = color_por_tipo or colores_default
    
    for _, row in datos_rutas.iterrows():
        # Coordenadas inicio y fin
        lat_inicio = row.get('lat_inicio')
        lon_inicio = row.get('lon_inicio')
        lat_fin = row.get('lat_fin')
        lon_fin = row.get('lon_fin')
        
        if pd.isna(lat_inicio) or pd.isna(lon_inicio) or pd.isna(lat_fin) or pd.isna(lon_fin):
            continue
        
        # Determinar color según tipo
        tipo_ruta = row.get('tipo_ruta', 'Local')
        color = colores.get(tipo_ruta, '#95A5A6')
        
        # Dibujar línea de ruta
        folium.PolyLine(
            locations=[[lat_inicio, lon_inicio], [lat_fin, lon_fin]],
            color=color,
            weight=4,
            opacity=0.7,
            popup=f"{row.get('nombre_ruta', 'Ruta')} - {tipo_ruta}",
            tooltip=row.get('nombre_ruta', 'Ruta')
        ).add_to(mapa)
        
        # Agregar marcador de inicio
        folium.CircleMarker(
            location=[lat_inicio, lon_inicio],
            radius=5,
            color=color,
            fill=True,
            fillColor=color,
            fillOpacity=0.8,
            popup=f"Inicio: {row.get('nombre_ruta', 'Ruta')}"
        ).add_to(mapa)
        
        # Agregar marcador de fin (diferente estilo)
        folium.CircleMarker(
            location=[lat_fin, lon_fin],
            radius=5,
            color=color,
            fill=True,
            fillColor=color,
            fillOpacity=0.8,
            popup=f"Fin: {row.get('nombre_ruta', 'Ruta')}"
        ).add_to(mapa)
    
    return mapa


def agregar_capa_motivos_viaje(
    mapa: folium.Map,
    datos_motivos: pd.DataFrame,
    max_puntos: int = 100
) -> folium.Map:
    """
    Agrega capa de motivos de viaje al mapa como puntos OD (Origen-Destino).
    
    Args:
        mapa: Mapa folium base
        datos_motivos: DataFrame con información de viajes
        max_puntos: Número máximo de puntos a mostrar
        
    Returns:
        Mapa con los puntos de viaje agregados
    """
    if datos_motivos.empty:
        return mapa
    
    # Limitar número de puntos para rendimiento
    df_sample = datos_motivos.head(max_puntos) if len(datos_motivos) > max_puntos else datos_motivos
    
    # Colores por motivo
    colores_motivo = {
        "Trabajo": "#E74C3C",
        "Estudio": "#3498DB",
        "Salud": "#2ECC71",
        "Compras": "#F39C12",
        "Ocio/Recreación": "#9B59B6",
        "Trámites": "#1ABC9C",
        "Visitas": "#E67E22",
        "Otros": "#95A5A6"
    }
    
    for _, row in df_sample.iterrows():
        lat_origen = row.get('lat_origen')
        lon_origen = row.get('lon_origen')
        lat_destino = row.get('lat_destino')
        lon_destino = row.get('lon_destino')
        motivo = row.get('motivo', 'Otros')
        
        if pd.isna(lat_origen) or pd.isna(lon_origen):
            continue
        
        color = colores_motivo.get(motivo, '#95A5A6')
        
        # Marcador de origen
        folium.Marker(
            location=[lat_origen, lon_origen],
            icon=folium.Icon(color='green', icon='play', prefix='fa'),
            popup=f"Origen: {motivo}",
            tooltip=f"Origen - {motivo}"
        ).add_to(mapa)
        
        # Si hay destino, dibujar línea
        if not pd.isna(lat_destino) and not pd.isna(lon_destino):
            folium.Marker(
                location=[lat_destino, lon_destino],
                icon=folium.Icon(color='red', icon='stop', prefix='fa'),
                popup=f"Destino: {motivo}",
                tooltip=f"Destino - {motivo}"
            ).add_to(mapa)
            
            # Línea punteada OD
            folium.PolyLine(
                locations=[[lat_origen, lon_origen], [lat_destino, lon_destino]],
                color=color,
                weight=2,
                opacity=0.4,
                dash_array='5, 5'
            ).add_to(mapa)
    
    return mapa


def agregar_capa_embotellamiento(
    mapa: folium.Map,
    datos_embotellamiento: pd.DataFrame
) -> folium.Map:
    """
    Agrega capa de puntos de congestión al mapa.
    
    Args:
        mapa: Mapa folium base
        datos_embotellamiento: DataFrame con información de congestión
        
    Returns:
        Mapa con los puntos de congestión agregados
    """
    if datos_embotellamiento.empty:
        return mapa
    
    for _, row in datos_embotellamiento.iterrows():
        lat = row.get('lat')
        lon = row.get('lon')
        nivel = row.get('nivel_congestion', 0)
        
        if pd.isna(lat) or pd.isna(lon):
            continue
        
        # Determinar color y radio según nivel de congestión
        if nivel >= 75:
            color = '#E74C3C'  # Rojo - Crítico
            radio = 15
        elif nivel >= 50:
            color = '#F39C12'  # Naranja - Alto
            radio = 12
        elif nivel >= 25:
            color = '#F1C40F'  # Amarillo - Medio
            radio = 10
        else:
            color = '#2ECC71'  # Verde - Bajo
            radio = 8
        
        # Círculo proporcional al nivel de congestión
        folium.Circle(
            location=[lat, lon],
            radius=radio * 10,
            color=color,
            fill=True,
            fillColor=color,
            fillOpacity=0.6,
            popup=f"""
                <b>{row.get('ubicacion', 'Punto crítico')}</b><br>
                Vía: {row.get('vía', 'N/A')}<br>
                Congestión: {nivel:.0f}%<br>
                Velocidad: {row.get('velocidad_promedio_kmh', 0):.1f} km/h<br>
                Tiempo espera: {row.get('tiempo_espera_minutos', 0):.0f} min
            """,
            tooltip=f"Congestión: {nivel:.0f}%"
        ).add_to(mapa)
    
    return mapa


def agregar_capa_flujos(
    mapa: folium.Map,
    datos_flujos: pd.DataFrame
) -> folium.Map:
    """
    Agrega capa de flujos de tráfico al mapa.
    
    Args:
        mapa: Mapa folium base
        datos_flujos: DataFrame con información de flujos
        
    Returns:
        Mapa con los flujos agregados
    """
    if datos_flujos.empty:
        return mapa
    
    for _, row in datos_flujos.iterrows():
        lat = row.get('lat')
        lon = row.get('lon')
        flujo = row.get('flujo_vehiculos_hora', 0)
        direccion = row.get('direccion_sentido', '')
        
        if pd.isna(lat) or pd.isna(lon):
            continue
        
        # Determinar color según intensidad de flujo
        if flujo >= 1500:
            color = '#8E44AD'  # Morado - Muy alto
            radio = 18
        elif flujo >= 1000:
            color = '#E74C3C'  # Rojo - Alto
            radio = 15
        elif flujo >= 500:
            color = '#3498DB'  # Azul - Medio
            radio = 12
        else:
            color = '#2ECC71'  # Verde - Bajo
            radio = 10
        
        # Marcador cuadrado para sensores de flujo
        folium.RegularPolygonMarker(
            location=[lat, lon],
            number_of_sides=4,
            radius=radio,
            rotation=direccion,
            color=color,
            fill=True,
            fillColor=color,
            fillOpacity=0.7,
            popup=f"""
                <b>{row.get('ubicacion', 'Sensor')}</b><br>
                Vía: {row.get('vía_principal', 'N/A')}<br>
                Flujo: {flujo:.0f} veh/h<br>
                Ocupación: {row.get('ocupacion_vial_porcentaje', 0):.0f}%<br>
                Dirección: {direccion}
            """,
            tooltip=f"Flujo: {flujo:.0f} veh/h"
        ).add_to(mapa)
    
    return mapa


def agregar_capa_comunas(
    mapa: folium.Map,
    datos_comunas: pd.DataFrame
) -> folium.Map:
    """
    Agrega capa de comunas con polígonos simplificados.
    
    Args:
        mapa: Mapa folium base
        datos_comunas: DataFrame con información de comunas
        
    Returns:
        Mapa con las comunas agregadas
    """
    if datos_comunas.empty:
        return mapa
    
    # Colores por estrato
    colores_estrato = {
        1: '#27AE60',
        2: '#2ECC71',
        3: '#F1C40F',
        4: '#F39C12',
        5: '#E67E22',
        6: '#E74C3C'
    }
    
    for _, row in datos_comunas.iterrows():
        nombre = row.get('nombre_completo', 'Comuna')
        estrato = row.get('estrato_predominante', 3)
        poblacion = row.get('poblacion_total', 0)
        lat_centro = row.get('lat_centro')
        lon_centro = row.get('lon_centro')
        
        if pd.isna(lat_centro) or pd.isna(lon_centro):
            continue
        
        color = colores_estrato.get(estrato, '#95A5A6')
        
        # Si hay polígono, dibujarlo
        poligono_lat = row.get('poligono_lat')
        poligono_lon = row.get('poligono_lon')
        
        if poligono_lat and poligono_lon and len(poligono_lat) == len(poligono_lon):
            coordenadas = list(zip(poligono_lat, poligono_lon))
            folium.Polygon(
                locations=coordenadas,
                color=color,
                fill=True,
                fillColor=color,
                fillOpacity=0.3,
                weight=2,
                popup=f"""
                    <b>{nombre}</b><br>
                    Estrato: {estrato}<br>
                    Población: {poblacion:,}
                """
            ).add_to(mapa)
        else:
            # Usar círculo si no hay polígono
            folium.Circle(
                location=[lat_centro, lon_centro],
                radius=1500,
                color=color,
                fill=True,
                fillColor=color,
                fillOpacity=0.3,
                popup=f"""
                    <b>{nombre}</b><br>
                    Estrato: {estrato}<br>
                    Población: {poblacion:,}
                """,
                tooltip=nombre
            ).add_to(mapa)
    
    return mapa


def renderizar_mapa_interactivo(
    datos_mapa: Dict[str, pd.DataFrame],
    capas_activas: Dict[str, bool],
    altura: str = "600px"
) -> folium.Map:
    """
    Renderiza el mapa completo con todas las capas activas.
    
    Args:
        datos_mapa: Diccionario con datos preparados para cada capa
        capas_activas: Diccionario indicando qué capas están activas
        altura: Altura del mapa en pixels
        
    Returns:
        Mapa folium completo
    """
    # Crear mapa base
    mapa = crear_mapa_base(height=altura)
    
    # Agregar capas según estén activas
    if capas_activas.get('rutas_transporte', False) and 'rutas' in datos_mapa:
        mapa = agregar_capa_rutas(mapa, datos_mapa['rutas'])
    
    if capas_activas.get('motivos_viaje', False) and 'motivos' in datos_mapa:
        mapa = agregar_capa_motivos_viaje(mapa, datos_mapa['motivos'])
    
    if capas_activas.get('horas_embotellamiento', False) and 'embotellamiento' in datos_mapa:
        mapa = agregar_capa_embotellamiento(mapa, datos_mapa['embotellamiento'])
    
    if capas_activas.get('flujos_trafico', False) and 'flujos' in datos_mapa:
        mapa = agregar_capa_flujos(mapa, datos_mapa['flujos'])
    
    if capas_activas.get('estratificacion_comuna', False) and 'comunas' in datos_mapa:
        mapa = agregar_capa_comunas(mapa, datos_mapa['comunas'])
    
    return mapa


def mostrar_mapa_streamlit(
    mapa: folium.Map,
    key: str = "mapa_principal",
    width: int = None,
    height: int = None
) -> Dict[str, Any]:
    """
    Muestra el mapa en Streamlit usando st_folium.
    
    Args:
        mapa: Mapa folium a mostrar
        key: Key único para el componente
        width: Ancho del mapa
        height: Alto del mapa
        
    Returns:
        Datos de interacción del mapa (clicks, zoom, etc.)
    """
    return st_folium(
        mapa,
        key=key,
        width=width or "100%",
        height=height or 600,
        returned_objects=["last_clicked", "zoom", "bounds"]
    )


def generar_leyenda_mapa() -> str:
    """
    Genera HTML para leyenda del mapa.
    
    Returns:
        String HTML con la leyenda
    """
    leyenda_html = """
    <div style='
        position: fixed;
        bottom: 50px;
        left: 50px;
        z-index: 1000;
        background-color: rgba(255, 255, 255, 0.9);
        padding: 15px;
        border-radius: 10px;
        border: 2px solid #ddd;
        font-family: Arial, sans-serif;
        font-size: 12px;
    '>
        <h4 style='margin: 0 0 10px 0;'>Leyenda</h4>
        
        <div style='margin-bottom: 10px;'>
            <strong>Rutas:</strong><br>
            <span style='color: #E74C3C;'>●</span> Principal<br>
            <span style='color: #3498DB;'>●</span> Secundaria<br>
            <span style='color: #2ECC71;'>●</span> Local
        </div>
        
        <div style='margin-bottom: 10px;'>
            <strong>Congestión:</strong><br>
            <span style='color: #E74C3C;'>●</span> Alta (≥75%)<br>
            <span style='color: #F39C12;'>●</span> Media (50-74%)<br>
            <span style='color: #2ECC71;'>●</span> Baja (<50%)
        </div>
        
        <div>
            <strong>Flujo:</strong><br>
            <span style='color: #8E44AD;'>■</span> Muy Alto<br>
            <span style='color: #E74C3C;'>■</span> Alto<br>
            <span style='color: #3498DB;'>■</span> Medio
        </div>
    </div>
    """
    return leyenda_html
