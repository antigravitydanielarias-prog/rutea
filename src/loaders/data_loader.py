"""
Módulo de carga de datos para el dashboard de movilidad urbana.

Este módulo maneja la lectura y validación de archivos CSV y otros formatos
tabulares, implementando caché para optimizar el rendimiento.
"""

import pandas as pd
import streamlit as st
from pathlib import Path
from typing import Optional, Dict, Any, List
import hashlib


def generar_hash_archivo(ruta_archivo: str) -> str:
    """
    Genera un hash único para un archivo basado en su contenido.
    
    Args:
        ruta_archivo: Ruta completa al archivo
        
    Returns:
        Hash MD5 del contenido del archivo
    """
    with open(ruta_archivo, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()


@st.cache_data(ttl=3600, show_spinner=True)
def cargar_csv(ruta_archivo: str) -> Optional[pd.DataFrame]:
    """
    Carga un archivo CSV con manejo de errores y validación básica.
    
    Args:
        ruta_archivo: Ruta al archivo CSV
        
    Returns:
        DataFrame con los datos cargados o None si hay error
    """
    try:
        # Verificar existencia del archivo
        if not Path(ruta_archivo).exists():
            st.error(f"❌ El archivo no existe: {ruta_archivo}")
            return None
        
        # Cargar CSV con configuración robusta
        df = pd.read_csv(
            ruta_archivo,
            encoding='utf-8',
            on_bad_lines='skip',
            skipinitialspace=True
        )
        
        # Validar que no esté vacío
        if df.empty:
            st.warning("⚠️ El archivo está vacío")
            return None
        
        return df
        
    except UnicodeDecodeError:
        # Intentar con encoding alternativo
        try:
            df = pd.read_csv(ruta_archivo, encoding='latin-1')
            return df
        except Exception as e:
            st.error(f"❌ Error de codificación: {str(e)}")
            return None
            
    except Exception as e:
        st.error(f"❌ Error al cargar CSV: {str(e)}")
        return None


@st.cache_data(ttl=3600, show_spinner=True)
def cargar_excel(ruta_archivo: str, hoja: Optional[str] = None) -> Optional[pd.DataFrame]:
    """
    Carga un archivo Excel con manejo de errores.
    
    Args:
        ruta_archivo: Ruta al archivo Excel
        hoja: Nombre o índice de la hoja (opcional)
        
    Returns:
        DataFrame con los datos cargados o None si hay error
    """
    try:
        if not Path(ruta_archivo).exists():
            st.error(f"❌ El archivo no existe: {ruta_archivo}")
            return None
        
        df = pd.read_excel(ruta_archivo, sheet_name=hoja if hoja else 0)
        
        if df.empty:
            st.warning("⚠️ El archivo está vacío")
            return None
        
        return df
        
    except Exception as e:
        st.error(f"❌ Error al cargar Excel: {str(e)}")
        return None


def validar_columnas_requeridas(
    df: pd.DataFrame, 
    columnas_requeridas: List[str],
    nombre_dataset: str = "datos"
) -> bool:
    """
    Valida que un DataFrame contenga las columnas requeridas.
    
    Args:
        df: DataFrame a validar
        columnas_requeridas: Lista de nombres de columnas requeridas
        nombre_dataset: Nombre descriptivo del dataset para mensajes
        
    Returns:
        True si todas las columnas están presentes, False en caso contrario
    """
    columnas_faltantes = [col for col in columnas_requeridas if col not in df.columns]
    
    if columnas_faltantes:
        st.error(
            f"❌ El dataset '{nombre_dataset}' falta columnas requeridas: "
            f"{', '.join(columnas_faltantes)}"
        )
        return False
    
    return True


def normalizar_nombres_columnas(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normaliza los nombres de columnas a minúsculas sin espacios.
    
    Args:
        df: DataFrame original
        
    Returns:
        DataFrame con nombres de columnas normalizados
    """
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(' ', '_')
        .str.replace('-', '_')
    )
    return df


def obtener_info_dataset(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Obtiene información resumida de un dataset.
    
    Args:
        df: DataFrame a analizar
        
    Returns:
        Diccionario con información del dataset
    """
    return {
        "filas": len(df),
        "columnas": len(df.columns),
        "nombre_columnas": list(df.columns),
        "tipos_datos": df.dtypes.astype(str).to_dict(),
        "nulos_por_columna": df.isnull().sum().to_dict(),
        "memoria_uso_mb": df.memory_usage(deep=True).sum() / (1024 * 1024)
    }


def cargar_datos_ejemplo_movilidad() -> Dict[str, pd.DataFrame]:
    """
    Genera datasets de ejemplo para movilidad urbana de Medellín.
    
    Esta función crea datos sintéticos que representan dinámicas urbanas
    reales para propósitos de demostración y pruebas.
    
    Returns:
        Diccionario con múltiples DataFrames de ejemplo
    """
    import numpy as np
    from datetime import datetime, timedelta
    
    np.random.seed(42)
    
    # =========================================
    # Dataset 1: Rutas de Transporte
    # =========================================
    n_rutas = 50
    rutas_data = {
        "id_ruta": [f"RUTA-{i:03d}" for i in range(1, n_rutas + 1)],
        "nombre_ruta": [f"Ruta {chr(65 + i % 26)}{i // 26 + 1}" for i in range(n_rutas)],
        "tipo_ruta": np.random.choice(
            ["Principal", "Secundaria", "Local", "Peatonal"], 
            n_rutas, 
            p=[0.3, 0.4, 0.25, 0.05]
        ),
        "comuna_inicio": np.random.choice(
            [f"Comuna {i} - {nombre}" for i, nombre in enumerate([
                "Popular", "Santa Cruz", "Manrique", "Aranjuez", "Castilla",
                "Doce de Octubre", "Robledo", "Villa Hermosa", "Buenos Aires",
                "La Candelaria", "Laureles", "La América", "San Javier",
                "El Poblado", "Guayabal", "Belén"
            ], 1)],
            n_rutas
        ),
        "comuna_fin": np.random.choice(
            [f"Comuna {i} - {nombre}" for i, nombre in enumerate([
                "Popular", "Santa Cruz", "Manrique", "Aranjuez", "Castilla",
                "Doce de Octubre", "Robledo", "Villa Hermosa", "Buenos Aires",
                "La Candelaria", "Laureles", "La América", "San Javier",
                "El Poblado", "Guayabal", "Belén"
            ], 1)],
            n_rutas
        ),
        "lat_inicio": np.random.uniform(6.15, 6.35, n_rutas),
        "lon_inicio": np.random.uniform(-75.70, -75.45, n_rutas),
        "lat_fin": np.random.uniform(6.15, 6.35, n_rutas),
        "lon_fin": np.random.uniform(-75.70, -75.45, n_rutas),
        "frecuencia_minutos": np.random.choice([5, 10, 15, 20, 30], n_rutas),
        "capacidad_pasajeros": np.random.choice([50, 80, 120, 160], n_rutas)
    }
    df_rutas = pd.DataFrame(rutas_data)
    
    # =========================================
    # Dataset 2: Motivos de Viaje
    # =========================================
    n_viajes = 500
    motivos_data = {
        "id_viaje": [f"VIAJE-{i:05d}" for i in range(1, n_viajes + 1)],
        "motivo": np.random.choice(
            ["Trabajo", "Estudio", "Salud", "Compras", "Ocio/Recreación", "Trámites", "Visitas", "Otros"],
            n_viajes,
            p=[0.35, 0.20, 0.08, 0.10, 0.12, 0.05, 0.07, 0.03]
        ),
        "comuna_origen": np.random.choice(
            [f"Comuna {i} - {nombre}" for i, nombre in enumerate([
                "Popular", "Santa Cruz", "Manrique", "Aranjuez", "Castilla",
                "Doce de Octubre", "Robledo", "Villa Hermosa", "Buenos Aires",
                "La Candelaria", "Laureles", "La América", "San Javier",
                "El Poblado", "Guayabal", "Belén"
            ], 1)],
            n_viajes
        ),
        "comuna_destino": np.random.choice(
            [f"Comuna {i} - {nombre}" for i, nombre in enumerate([
                "Popular", "Santa Cruz", "Manrique", "Aranjuez", "Castilla",
                "Doce de Octubre", "Robledo", "Villa Hermosa", "Buenos Aires",
                "La Candelaria", "Laureles", "La América", "San Javier",
                "El Poblado", "Guayabal", "Belén"
            ], 1)],
            n_viajes
        ),
        "hora_salida": np.random.randint(0, 24, n_viajes),
        "dia_semana": np.random.choice(
            ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"],
            n_viajes,
            p=[0.15, 0.15, 0.15, 0.15, 0.15, 0.15, 0.10]
        ),
        "medio_transporte": np.random.choice(
            ["Bus", "Metro", "Metrocable", "Taxi", "Bicicleta", "Caminando", "Carro particular"],
            n_viajes,
            p=[0.30, 0.25, 0.10, 0.10, 0.08, 0.12, 0.05]
        ),
        "duracion_minutos": np.random.randint(5, 90, n_viajes),
        "lat_origen": np.random.uniform(6.15, 6.35, n_viajes),
        "lon_origen": np.random.uniform(-75.70, -75.45, n_viajes),
        "lat_destino": np.random.uniform(6.15, 6.35, n_viajes),
        "lon_destino": np.random.uniform(-75.70, -75.45, n_viajes)
    }
    df_motivos = pd.DataFrame(motivos_data)
    
    # =========================================
    # Dataset 3: Horas de Embotellamiento
    # =========================================
    n_puntos = 100
    embotellamiento_data = {
        "id_punto": [f"PUNTO-{i:03d}" for i in range(1, n_puntos + 1)],
        "ubicacion": [f"Punto crítico {i}" for i in range(1, n_puntos + 1)],
        "vía": np.random.choice(
            ["Av. El Poblado", "Av. La Playa", "Cra. 43A", "Cra. 70", "Av. San Juan",
             "Cra. 45", "Calle 10", "Av. Oriental", "Cra. 48", "Calle 50"],
            n_puntos
        ),
        "comuna": np.random.choice(
            [f"Comuna {i} - {nombre}" for i, nombre in enumerate([
                "Popular", "Santa Cruz", "Manrique", "Aranjuez", "Castilla",
                "Doce de Octubre", "Robledo", "Villa Hermosa", "Buenos Aires",
                "La Candelaria", "Laureles", "La América", "San Javier",
                "El Poblado", "Guayabal", "Belén"
            ], 1)],
            n_puntos
        ),
        "rango_horario": np.random.choice(
            ["Madrugada (00:00 - 05:59)", "Mañana Temprano (06:00 - 08:59)",
             "Mañana (09:00 - 11:59)", "Mediodía (12:00 - 13:59)",
             "Tarde (14:00 - 17:59)", "Hora Pico PM (18:00 - 20:59)",
             "Noche (21:00 - 23:59)"],
            n_puntos,
            p=[0.05, 0.25, 0.10, 0.10, 0.15, 0.25, 0.10]
        ),
        "nivel_congestion": np.random.randint(0, 101, n_puntos),
        "velocidad_promedio_kmh": np.random.uniform(5, 60, n_puntos),
        "longitud_fila_metros": np.random.randint(0, 500, n_puntos),
        "tiempo_espera_minutos": np.random.randint(0, 45, n_puntos),
        "lat": np.random.uniform(6.15, 6.35, n_puntos),
        "lon": np.random.uniform(-75.70, -75.45, n_puntos)
    }
    df_embotellamiento = pd.DataFrame(embotellamiento_data)
    
    # =========================================
    # Dataset 4: Flujos de Tráfico
    # =========================================
    n_flujos = 200
    flujos_data = {
        "id_sensor": [f"SENSOR-{i:03d}" for i in range(1, n_flujos + 1)],
        "ubicacion": [f"Sensor {i}" for i in range(1, n_flujos + 1)],
        "vía_principal": np.random.choice(
            ["Av. El Poblado", "Av. La Playa", "Cra. 43A", "Cra. 70", "Av. San Juan",
             "Cra. 45", "Calle 10", "Av. Oriental", "Cra. 48", "Calle 50"],
            n_flujos
        ),
        "comuna": np.random.choice(
            [f"Comuna {i} - {nombre}" for i, nombre in enumerate([
                "Popular", "Santa Cruz", "Manrique", "Aranjuez", "Castilla",
                "Doce de Octubre", "Robledo", "Villa Hermosa", "Buenos Aires",
                "La Candelaria", "Laureles", "La América", "San Javier",
                "El Poblado", "Guayabal", "Belén"
            ], 1)],
            n_flujos
        ),
        "hora_medicion": np.random.randint(0, 24, n_flujos),
        "flujo_vehiculos_hora": np.random.randint(50, 2000, n_flujos),
        "flujo_peatones_hora": np.random.randint(0, 500, n_flujos),
        "ocupacion_vial_porcentaje": np.random.randint(0, 101, n_flujos),
        "velocidad_promedio_kmh": np.random.uniform(10, 70, n_flujos),
        "direccion_sentido": np.random.choice(["Norte", "Sur", "Oriente", "Occidente"], n_flujos),
        "lat": np.random.uniform(6.15, 6.35, n_flujos),
        "lon": np.random.uniform(-75.70, -75.45, n_flujos)
    }
    df_flujos = pd.DataFrame(flujos_data)
    
    # =========================================
    # Dataset 5: Estratificación por Comuna
    # =========================================
    comunas_data = {
        "id_comuna": list(range(1, 17)),
        "nombre_comuna": [
            "Popular", "Santa Cruz", "Manrique", "Aranjuez", "Castilla",
            "Doce de Octubre", "Robledo", "Villa Hermosa", "Buenos Aires",
            "La Candelaria", "Laureles", "La América", "San Javier",
            "El Poblado", "Guayabal", "Belén"
        ],
        "nombre_completo": [
            f"Comuna {i} - {nombre}" for i, nombre in enumerate([
                "Popular", "Santa Cruz", "Manrique", "Aranjuez", "Castilla",
                "Doce de Octubre", "Robledo", "Villa Hermosa", "Buenos Aires",
                "La Candelaria", "Laureles", "La América", "San Javier",
                "El Poblado", "Guayabal", "Belén"
            ], 1)
        ],
        "estrato_predominante": np.random.choice([1, 2, 3, 4, 5, 6], 16),
        "poblacion_total": np.random.randint(50000, 200000, 16),
        "area_km2": np.random.uniform(2, 15, 16),
        "densidad_hab_km2": np.random.randint(5000, 25000, 16),
        "lat_centro": np.random.uniform(6.15, 6.35, 16),
        "lon_centro": np.random.uniform(-75.70, -75.45, 16),
        "poligono_lat": [[np.random.uniform(6.15, 6.35) for _ in range(5)] for _ in range(16)],
        "poligono_lon": [[np.random.uniform(-75.70, -75.45) for _ in range(5)] for _ in range(16)]
    }
    df_comunas = pd.DataFrame(comunas_data)
    
    return {
        "rutas": df_rutas,
        "motivos": df_motivos,
        "embotellamiento": df_embotellamiento,
        "flujos": df_flujos,
        "comunas": df_comunas
    }


def guardar_datos_ejemplo_csv(ruta_directorio: str = "data") -> None:
    """
    Guarda los datasets de ejemplo como archivos CSV.
    
    Args:
        ruta_directorio: Directorio donde se guardarán los archivos
    """
    datos = cargar_datos_ejemplo_movilidad()
    
    Path(ruta_directorio).mkdir(parents=True, exist_ok=True)
    
    for nombre, df in datos.items():
        ruta_archivo = Path(ruta_directorio) / f"{nombre}.csv"
        df.to_csv(ruta_archivo, index=False, encoding='utf-8')
        print(f"✅ Guardado: {ruta_archivo}")
