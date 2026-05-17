"""
Módulo de procesamiento de datos para el dashboard de movilidad urbana.

Este módulo contiene funciones para filtrar, transformar y preparar
los datos cargados para su visualización y análisis.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime


def aplicar_filtro_comuna(
    df: pd.DataFrame,
    comunas_seleccionadas: Optional[List[str]],
    columnas_comuna: Optional[List[str]] = None
) -> pd.DataFrame:
    """
    Filtra un DataFrame por comunas seleccionadas.
    
    Args:
        df: DataFrame original
        comunas_seleccionadas: Lista de comunas a filtrar
        columnas_comuna: Nombres de columnas que pueden contener información de comuna
        
    Returns:
        DataFrame filtrado
    """
    if not comunas_seleccionadas:
        return df
    
    if columnas_comuna is None:
        columnas_comuna = ['comuna', 'comuna_origen', 'comuna_destino', 'comuna_inicio', 'comuna_fin']
    
    # Buscar columnas existentes
    columnas_existentes = [col for col in columnas_comuna if col in df.columns]
    
    if not columnas_existentes:
        return df
    
    # Filtrar por cualquiera de las columnas de comuna
    mascara = pd.Series([False] * len(df), index=df.index)
    for col in columnas_existentes:
        mascara |= df[col].isin(comunas_seleccionadas)
    
    return df[mascara].copy()


def aplicar_filtro_rango_horario(
    df: pd.DataFrame,
    rango_horario: str,
    columna_hora: str = 'hora_salida'
) -> pd.DataFrame:
    """
    Filtra un DataFrame por rango horario.
    
    Args:
        df: DataFrame original
        rango_horario: Rango horario seleccionado
        columna_hora: Nombre de la columna que contiene la hora
        
    Returns:
        DataFrame filtrado
    """
    if rango_horario == "Todo el día" or columna_hora not in df.columns:
        return df
    
    # Verificar si la columna es de tipo string (formato nombre de rango)
    # o numérica (hora del día)
    if df[columna_hora].dtype == object:
        # Es una columna de texto, filtrar por coincidencia exacta
        return df[df[columna_hora] == rango_horario].copy()
    
    # Mapeo de rangos horarios a horas
    rangos = {
        "Madrugada (00:00 - 05:59)": (0, 5),
        "Mañana Temprano (06:00 - 08:59)": (6, 8),
        "Mañana (09:00 - 11:59)": (9, 11),
        "Mediodía (12:00 - 13:59)": (12, 13),
        "Tarde (14:00 - 17:59)": (14, 17),
        "Hora Pico PM (18:00 - 20:59)": (18, 20),
        "Noche (21:00 - 23:59)": (21, 23)
    }
    
    if rango_horario in rangos:
        hora_inicio, hora_fin = rangos[rango_horario]
        return df[(df[columna_hora] >= hora_inicio) & (df[columna_hora] <= hora_fin)].copy()
    
    return df


def aplicar_filtro_motivo_viaje(
    df: pd.DataFrame,
    motivos_seleccionados: Optional[List[str]],
    columna_motivo: str = 'motivo'
) -> pd.DataFrame:
    """
    Filtra un DataFrame por motivos de viaje.
    
    Args:
        df: DataFrame original
        motivos_seleccionados: Lista de motivos seleccionados
        columna_motivo: Nombre de la columna que contiene el motivo
        
    Returns:
        DataFrame filtrado
    """
    if not motivos_seleccionados or columna_motivo not in df.columns:
        return df
    
    return df[df[columna_motivo].isin(motivos_seleccionados)].copy()


def aplicar_filtro_tipo_ruta(
    df: pd.DataFrame,
    tipo_ruta: str,
    columna_tipo: str = 'tipo_ruta'
) -> pd.DataFrame:
    """
    Filtra un DataFrame por tipo de ruta.
    
    Args:
        df: DataFrame original
        tipo_ruta: Tipo de ruta seleccionado
        columna_tipo: Nombre de la columna que contiene el tipo de ruta
        
    Returns:
        DataFrame filtrado
    """
    if tipo_ruta == "Todas" or columna_tipo not in df.columns:
        return df
    
    return df[df[columna_tipo] == tipo_ruta].copy()


def aplicar_filtro_nivel_congestion(
    df: pd.DataFrame,
    rango_congestion: Tuple[int, int],
    columna_congestion: str = 'nivel_congestion'
) -> pd.DataFrame:
    """
    Filtra un DataFrame por nivel de congestión.
    
    Args:
        df: DataFrame original
        rango_congestion: Tupla con valores mínimo y máximo de congestión
        columna_congestion: Nombre de la columna que contiene el nivel de congestión
        
    Returns:
        DataFrame filtrado
    """
    if columna_congestion not in df.columns:
        return df
    
    min_cong, max_cong = rango_congestion
    return df[(df[columna_congestion] >= min_cong) & (df[columna_congestion] <= max_cong)].copy()


def aplicar_todos_los_filtros(
    datos: Dict[str, pd.DataFrame],
    filtros: Dict[str, Any]
) -> Dict[str, pd.DataFrame]:
    """
    Aplica todos los filtros configurados a los datasets correspondientes.
    
    Args:
        datos: Diccionario con los datasets originales
        filtros: Diccionario con los valores de los filtros aplicados
        
    Returns:
        Diccionario con los datasets filtrados
    """
    datos_filtrados = {}
    
    # =========================================
    # Filtrar dataset de rutas
    # =========================================
    if 'rutas' in datos:
        df = datos['rutas'].copy()
        df = aplicar_filtro_comuna(
            df, 
            filtros.get('comuna'),
            ['comuna_inicio', 'comuna_fin']
        )
        df = aplicar_filtro_tipo_ruta(
            df,
            filtros.get('tipo_ruta', 'Todas')
        )
        datos_filtrados['rutas'] = df
    
    # =========================================
    # Filtrar dataset de motivos de viaje
    # =========================================
    if 'motivos' in datos:
        df = datos['motivos'].copy()
        df = aplicar_filtro_comuna(
            df,
            filtros.get('comuna'),
            ['comuna_origen', 'comuna_destino']
        )
        df = aplicar_filtro_rango_horario(
            df,
            filtros.get('rango_horario', 'Todo el día')
        )
        df = aplicar_filtro_motivo_viaje(
            df,
            filtros.get('motivo_viaje')
        )
        datos_filtrados['motivos'] = df
    
    # =========================================
    # Filtrar dataset de embotellamiento
    # =========================================
    if 'embotellamiento' in datos:
        df = datos['embotellamiento'].copy()
        df = aplicar_filtro_comuna(df, filtros.get('comuna'))
        df = aplicar_filtro_rango_horario(
            df,
            filtros.get('rango_horario', 'Todo el día'),
            columna_hora='rango_horario'
        )
        df = aplicar_filtro_nivel_congestion(
            df,
            filtros.get('nivel_congestion', (0, 100))
        )
        datos_filtrados['embotellamiento'] = df
    
    # =========================================
    # Filtrar dataset de flujos
    # =========================================
    if 'flujos' in datos:
        df = datos['flujos'].copy()
        df = aplicar_filtro_comuna(df, filtros.get('comuna'))
        df = aplicar_filtro_rango_horario(
            df,
            filtros.get('rango_horario', 'Todo el día'),
            columna_hora='hora_medicion'
        )
        df = aplicar_filtro_nivel_congestion(
            df,
            filtros.get('nivel_congestion', (0, 100)),
            columna_congestion='ocupacion_vial_porcentaje'
        )
        datos_filtrados['flujos'] = df
    
    # =========================================
    # Filtrar dataset de comunas
    # =========================================
    if 'comunas' in datos:
        df = datos['comunas'].copy()
        df = aplicar_filtro_comuna(df, filtros.get('comuna'), ['nombre_completo'])
        datos_filtrados['comunas'] = df
    
    return datos_filtrados


def calcular_estadisticas_resumen(
    datos: Dict[str, pd.DataFrame]
) -> Dict[str, Dict[str, Any]]:
    """
    Calcula estadísticas resumen de los datasets filtrados.
    
    Args:
        datos: Diccionario con los datasets filtrados
        
    Returns:
        Diccionario con estadísticas por dataset
    """
    estadisticas = {}
    
    if 'rutas' in datos and not datos['rutas'].empty:
        df = datos['rutas']
        estadisticas['rutas'] = {
            'total_rutas': len(df),
            'rutas_principales': len(df[df['tipo_ruta'] == 'Principal']) if 'tipo_ruta' in df.columns else 0,
            'frecuencia_promedio': df['frecuencia_minutos'].mean() if 'frecuencia_minutos' in df.columns else 0
        }
    
    if 'motivos' in datos and not datos['motivos'].empty:
        df = datos['motivos']
        estadisticas['motivos'] = {
            'total_viajes': len(df),
            'duracion_promedio': df['duracion_minutos'].mean() if 'duracion_minutos' in df.columns else 0,
            'motivo_mas_frecuente': df['motivo'].mode().iloc[0] if 'motivo' in df.columns and not df['motivo'].mode().empty else 'N/A'
        }
    
    if 'embotellamiento' in datos and not datos['embotellamiento'].empty:
        df = datos['embotellamiento']
        estadisticas['embotellamiento'] = {
            'puntos_criticos': len(df),
            'congestion_promedio': df['nivel_congestion'].mean() if 'nivel_congestion' in df.columns else 0,
            'tiempo_espera_promedio': df['tiempo_espera_minutos'].mean() if 'tiempo_espera_minutos' in df.columns else 0
        }
    
    if 'flujos' in datos and not datos['flujos'].empty:
        df = datos['flujos']
        estadisticas['flujos'] = {
            'sensores_activos': len(df),
            'flujo_vehicular_promedio': df['flujo_vehiculos_hora'].mean() if 'flujo_vehiculos_hora' in df.columns else 0,
            'velocidad_promedio': df['velocidad_promedio_kmh'].mean() if 'velocidad_promedio_kmh' in df.columns else 0
        }
    
    return estadisticas


def detectar_valores_atipicos(
    df: pd.DataFrame,
    columna: str,
    umbral_desviaciones: float = 2.0
) -> pd.DataFrame:
    """
    Detecta valores atípicos en una columna usando el método de desviaciones estándar.
    
    Args:
        df: DataFrame a analizar
        columna: Nombre de la columna a analizar
        umbral_desviaciones: Número de desviaciones estándar para considerar atípico
        
    Returns:
        DataFrame con columna booleana indicando si es atípico
    """
    if columna not in df.columns:
        df['es_atipico'] = False
        return df
    
    media = df[columna].mean()
    desviacion = df[columna].std()
    
    limite_inferior = media - (umbral_desviaciones * desviacion)
    limite_superior = media + (umbral_desviaciones * desviacion)
    
    df['es_atipico'] = (df[columna] < limite_inferior) | (df[columna] > limite_superior)
    
    return df


def agregar_columnas_derivadas(datos: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
    """
    Agrega columnas derivadas útiles para análisis y visualización.
    
    Args:
        datos: Diccionario con los datasets originales
        
    Returns:
        Diccionario con datasets enriquecidos
    """
    datos_enriquecidos = {}
    
    # =========================================
    # Enriquecer dataset de embotellamiento
    # =========================================
    if 'embotellamiento' in datos:
        df = datos['embotellamiento'].copy()
        
        # Clasificar nivel de congestión
        def clasificar_congestion(nivel):
            if nivel >= 75:
                return 'Alta'
            elif nivel >= 50:
                return 'Media'
            elif nivel >= 25:
                return 'Baja'
            else:
                return 'Mínima'
        
        if 'nivel_congestion' in df.columns:
            df['categoria_congestion'] = df['nivel_congestion'].apply(clasificar_congestion)
        
        # Detectar puntos críticos atípicos
        df = detectar_valores_atipicos(df, 'nivel_congestion')
        
        datos_enriquecidos['embotellamiento'] = df
    
    # =========================================
    # Enriquecer dataset de flujos
    # =========================================
    if 'flujos' in datos:
        df = datos['flujos'].copy()
        
        # Clasificar intensidad de flujo
        def clasificar_flujo(flujo):
            if flujo >= 1500:
                return 'Muy Alto'
            elif flujo >= 1000:
                return 'Alto'
            elif flujo >= 500:
                return 'Medio'
            else:
                return 'Bajo'
        
        if 'flujo_vehiculos_hora' in df.columns:
            df['categoria_flujo'] = df['flujo_vehiculos_hora'].apply(clasificar_flujo)
        
        datos_enriquecidos['flujos'] = df
    
    # =========================================
    # Enriquecer dataset de motivos
    # =========================================
    if 'motivos' in datos:
        df = datos['motivos'].copy()
        
        # Determinar si es hora pico
        def es_hora_pico(hora):
            return (6 <= hora <= 9) or (17 <= hora <= 20)
        
        if 'hora_salida' in df.columns:
            df['es_hora_pico'] = df['hora_salida'].apply(es_hora_pico)
        
        datos_enriquecidos['motivos'] = df
    
    # Copiar datasets sin enriquecimiento
    for key, df in datos.items():
        if key not in datos_enriquecidos:
            datos_enriquecidos[key] = df.copy()
    
    return datos_enriquecidos


def preparar_datos_para_mapa(
    datos: Dict[str, pd.DataFrame],
    capas_activas: Dict[str, bool]
) -> Dict[str, pd.DataFrame]:
    """
    Prepara los datos específicos para visualización en mapa.
    
    Args:
        datos: Diccionario con los datasets filtrados
        capas_activas: Diccionario indicando qué capas están activas
        
    Returns:
        Diccionario con datos listos para renderizar en mapa
    """
    datos_mapa = {}
    
    if capas_activas.get('rutas_transporte', False) and 'rutas' in datos:
        datos_mapa['rutas'] = datos['rutas'][
            ['lat_inicio', 'lon_inicio', 'lat_fin', 'lon_fin', 'nombre_ruta', 'tipo_ruta']
        ].dropna()
    
    if capas_activas.get('motivos_viaje', False) and 'motivos' in datos:
        datos_mapa['motivos'] = datos['motivos'][
            ['lat_origen', 'lon_origen', 'lat_destino', 'lon_destino', 'motivo', 'medio_transporte']
        ].dropna()
    
    if capas_activas.get('horas_embotellamiento', False) and 'embotellamiento' in datos:
        datos_mapa['embotellamiento'] = datos['embotellamiento'][
            ['lat', 'lon', 'nivel_congestion', 'ubicacion', 'vía', 'categoria_congestion']
        ].dropna()
    
    if capas_activas.get('flujos_trafico', False) and 'flujos' in datos:
        datos_mapa['flujos'] = datos['flujos'][
            ['lat', 'lon', 'flujo_vehiculos_hora', 'ocupacion_vial_porcentaje', 'direccion_sentido']
        ].dropna()
    
    if capas_activas.get('estratificacion_comuna', False) and 'comunas' in datos:
        datos_mapa['comunas'] = datos['comunas'][
            ['nombre_completo', 'estrato_predominante', 'poblacion_total', 'lat_centro', 'lon_centro']
        ].dropna()
    
    return datos_mapa
