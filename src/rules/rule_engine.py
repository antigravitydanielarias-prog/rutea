"""
Motor de reglas para generación de conclusiones dinámicas.

Este módulo implementa un sistema de reglas desacoplado que evalúa
condiciones sobre los datos filtrados y genera conclusiones accionables
en lenguaje natural.

Arquitectura diseñada para ser fácilmente extensible hacia inferencia
automática o modelos predictivos en el futuro.
"""

from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
import pandas as pd
import numpy as np


class TipoConclusion(Enum):
    """Tipos de conclusión que puede generar el motor."""
    NORMAL = "normal"
    ALERTA = "alerta"
    CRITICO = "critico"
    ATIPICO = "atipico"
    TENDENCIA = "tendencia"
    RECOMENDACION = "recomendacion"


@dataclass
class Conclusion:
    """
    Representa una conclusión generada por el motor de reglas.
    
    Attributes:
        tipo: Tipo de conclusión según la clasificación
        titulo: Título corto y descriptivo
        mensaje: Mensaje detallado en lenguaje natural
        severidad: Nivel de severidad (1-5, donde 5 es más severo)
        contexto: Información contextual adicional
        recomendacion: Acción recomendada basada en la conclusión
        datos_soporte: Datos que respaldan la conclusión
    """
    tipo: TipoConclusion
    titulo: str
    mensaje: str
    severidad: int = 3
    contexto: Optional[str] = None
    recomendacion: Optional[str] = None
    datos_soporte: Optional[Dict[str, Any]] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte la conclusión a diccionario para serialización."""
        return {
            "tipo": self.tipo.value,
            "titulo": self.titulo,
            "mensaje": self.mensaje,
            "severidad": self.severidad,
            "contexto": self.contexto,
            "recomendacion": self.recomendacion,
            "datos_soporte": self.datos_soporte
        }


class Regla:
    """
    Representa una regla individual del motor.
    
    Una regla consiste en:
    - Una función de evaluación que retorna True/False
    - Una función de generación de conclusión si la regla se activa
    
    Attributes:
        nombre: Identificador único de la regla
        descripcion: Descripción de lo que evalúa la regla
        evaluar: Función que evalúa la condición
        generar_conclusion: Función que genera la conclusión si se activa
        activa: Indica si la regla está habilitada
    """
    
    def __init__(
        self,
        nombre: str,
        descripcion: str,
        evaluar: Callable[[Dict[str, pd.DataFrame], Dict[str, Any]], bool],
        generar_conclusion: Callable[[Dict[str, pd.DataFrame], Dict[str, Any]], Conclusion]
    ):
        self.nombre = nombre
        self.descripcion = descripcion
        self.evaluar = evaluar
        self.generar_conclusion = generar_conclusion
        self.activa = True
    
    def ejecutar(
        self, 
        datos: Dict[str, pd.DataFrame], 
        filtros: Dict[str, Any]
    ) -> Optional[Conclusion]:
        """
        Ejecuta la regla y retorna una conclusión si se activa.
        
        Args:
            datos: Diccionario con los datasets filtrados
            filtros: Filtros aplicados por el usuario
            
        Returns:
            Conclusión si la regla se activa, None en caso contrario
        """
        if not self.activa:
            return None
        
        try:
            if self.evaluar(datos, filtros):
                return self.generar_conclusion(datos, filtros)
        except Exception as e:
            # Si hay error en la evaluación, retornar None silenciosamente
            # pero registrar para debugging en producción
            pass
        
        return None


class MotorReglas:
    """
    Motor principal de reglas para generación de conclusiones.
    
    Este motor:
    1. Mantiene un registro de reglas configuradas
    2. Evalúa todas las reglas contra los datos filtrados
    3. Genera conclusiones consolidadas
    4. Prioriza conclusiones por severidad y relevancia
    
    La arquitectura permite:
    - Agregar reglas dinámicamente
    - Habilitar/deshabilitar reglas específicas
    - Extender hacia inferencia automática
    """
    
    def __init__(self):
        self.reglas: List[Regla] = []
        self.inicializar_reglas_base()
    
    def agregar_regla(self, regla: Regla) -> None:
        """Agrega una nueva regla al motor."""
        self.reglas.append(regla)
    
    def remover_regla(self, nombre: str) -> bool:
        """Remueve una regla por su nombre."""
        for i, regla in enumerate(self.reglas):
            if regla.nombre == nombre:
                self.reglas.pop(i)
                return True
        return False
    
    def habilitar_regla(self, nombre: str) -> bool:
        """Habilita una regla específica."""
        for regla in self.reglas:
            if regla.nombre == nombre:
                regla.activa = True
                return True
        return False
    
    def deshabilitar_regla(self, nombre: str) -> bool:
        """Deshabilita una regla específica."""
        for regla in self.reglas:
            if regla.nombre == nombre:
                regla.activa = False
                return True
        return False
    
    def obtener_reglas_disponibles(self) -> List[Dict[str, Any]]:
        """Retorna lista de reglas disponibles con su estado."""
        return [
            {
                "nombre": r.nombre,
                "descripcion": r.descripcion,
                "activa": r.activa
            }
            for r in self.reglas
        ]
    
    def inicializar_reglas_base(self) -> None:
        """Inicializa el conjunto base de reglas predefinidas."""
        
        # =========================================
        # REGLA 1: Congestión alta en hora pico
        # =========================================
        def evaluar_congestion_hora_pico(datos, filtros):
            if 'embotellamiento' not in datos or datos['embotellamiento'].empty:
                return False
            
            rango = filtros.get('rango_horario', '')
            es_hora_pico = 'Mañana Temprano' in rango or 'Hora Pico PM' in rango
            
            if not es_hora_pico:
                return False
            
            congestion_alta = datos['embotellamiento']['nivel_congestion'] >= 75
            return congestion_alta.any()
        
        def generar_conclusion_congestion_hora_pico(datos, filtros):
            df = datos['embotellamiento']
            puntos_criticos = df[df['nivel_congestion'] >= 75]
            n_puntos = len(puntos_criticos)
            congestion_max = df['nivel_congestion'].max()
            
            return Conclusion(
                tipo=TipoConclusion.ALERTA,
                titulo="Congestión Crítica en Hora Pico",
                mensaje=f"Se detectaron {n_puntos} puntos con congestión superior al 75% durante hora pico. "
                       f"El nivel máximo alcanza {congestion_max:.0f}%. "
                       f"Los motivos de viaje laborales incrementan significativamente la presión vial.",
                severidad=4,
                contexto=f"Rango horario: {filtros.get('rango_horario', 'No especificado')}",
                recomendacion="Considere ajustar horarios de salida o usar rutas alternativas. "
                             "El transporte público puede ser más eficiente en este período.",
                datos_soporte={
                    "puntos_criticos": n_puntos,
                    "congestion_maxima": congestion_max,
                    "congestion_promedio": df['nivel_congestion'].mean()
                }
            )
        
        self.agregar_regla(Regla(
            nombre="congestion_hora_pico",
            descripcion="Detecta congestión alta durante horas pico",
            evaluar=evaluar_congestion_hora_pico,
            generar_conclusion=generar_conclusion_congestion_hora_pico
        ))
        
        # =========================================
        # REGLA 2: Flujo vehicular atípico
        # =========================================
        def evaluar_flujo_atipico(datos, filtros):
            if 'flujos' not in datos or datos['flujos'].empty:
                return False
            
            df = datos['flujos']
            if 'flujo_vehiculos_hora' not in df.columns:
                return False
            
            media = df['flujo_vehiculos_hora'].mean()
            desviacion = df['flujo_vehiculos_hora'].std()
            limite_superior = media + (2 * desviacion)
            
            return (df['flujo_vehiculos_hora'] > limite_superior).any()
        
        def generar_conclusion_flujo_atipico(datos, filtros):
            df = datos['flujos']
            media = df['flujo_vehiculos_hora'].mean()
            desviacion = df['flujo_vehiculos_hora'].std()
            limite = media + (2 * desviacion)
            puntos_atipicos = df[df['flujo_vehiculos_hora'] > limite]
            
            return Conclusion(
                tipo=TipoConclusion.ATIPICO,
                titulo="Flujo Vehicular Atípico Detectado",
                mensaje=f"Se identificaron {len(puntos_atipicos)} sensores con flujo vehicular "
                       f"significativamente superior al promedio ({media:.0f} vehículos/hora). "
                       f"Estos puntos superan {limite:.0f} vehículos/hora.",
                severidad=3,
                contexto=f"Comunas analizadas: {', '.join(filtros.get('comuna', ['Todas'])) if filtros.get('comuna') else 'Todas'}",
                recomendacion="Investigue eventos especiales o cambios patrones de movilidad en estas zonas. "
                             "Puede indicar construcción, eventos masivos o desvíos de tráfico.",
                datos_soporte={
                    "puntos_atipicos": len(puntos_atipicos),
                    "flujo_promedio": media,
                    "flujo_limite": limite,
                    "flujo_maximo": df['flujo_vehiculos_hora'].max()
                }
            )
        
        self.agregar_regla(Regla(
            nombre="flujo_atipico",
            descripcion="Detecta flujos vehiculares anormalmente altos",
            evaluar=evaluar_flujo_atipico,
            generar_conclusion=generar_conclusion_flujo_atipico
        ))
        
        # =========================================
        # REGLA 3: Concentración de viajes por motivo
        # =========================================
        def evaluar_concentracion_motivo(datos, filtros):
            if 'motivos' not in datos or datos['motivos'].empty:
                return False
            
            df = datos['motivos']
            if 'motivo' not in df.columns:
                return False
            
            total_viajes = len(df)
            if total_viajes < 10:
                return False
            
            conteo_motivos = df['motivo'].value_counts()
            motivo_dominante = conteo_motivos.iloc[0]
            porcentaje = (motivo_dominante / total_viajes) * 100
            
            return porcentaje > 50  # Más del 50% es concentración significativa
        
        def generar_conclusion_concentracion_motivo(datos, filtros):
            df = datos['motivos']
            conteo_motivos = df['motivo'].value_counts()
            motivo_principal = conteo_motivos.index[0]
            cantidad = conteo_motivos.iloc[0]
            porcentaje = (cantidad / len(df)) * 100
            
            return Conclusion(
                tipo=TipoConclusion.TENDENCIA,
                titulo=f"Dominancia de Viajes por {motivo_principal}",
                mensaje=f"El {porcentaje:.1f}% de los viajes filtrados tienen como motivo '{motivo_principal}'. "
                       f"Esto representa {cantidad} viajes del total analizado.",
                severidad=2,
                contexto=f"Total de viajes analizados: {len(df)}",
                recomendacion=f"La infraestructura y servicios deberían priorizar desplazamientos por {motivo_principal.lower()}. "
                             f"Considere refuerzo de transporte en horarios asociados a este motivo.",
                datos_soporte={
                    "motivo_principal": motivo_principal,
                    "cantidad": cantidad,
                    "porcentaje": porcentaje,
                    "top_3_motivos": conteo_motivos.head(3).to_dict()
                }
            )
        
        self.agregar_regla(Regla(
            nombre="concentracion_motivo",
            descripcion="Detecta dominancia significativa de un motivo de viaje",
            evaluar=evaluar_concentracion_motivo,
            generar_conclusion=generar_conclusion_concentracion_motivo
        ))
        
        # =========================================
        # REGLA 4: Comportamiento atípico por comuna
        # =========================================
        def evaluar_comuna_atipica(datos, filtros):
            if 'comuna' not in filtros or not filtros['comuna']:
                return False
            
            if 'embotellamiento' not in datos or datos['embotellamiento'].empty:
                return False
            
            # Comparar congestión promedio de comunas seleccionadas vs global
            df = datos['embotellamiento']
            if 'comuna' not in df.columns:
                return False
            
            comunas_seleccionadas = filtros['comuna']
            comunas_en_datos = df['comuna'].unique()
            comunas_interseccion = [c for c in comunas_seleccionadas if c in comunas_en_datos]
            
            if not comunas_interseccion:
                return False
            
            congestion_global = df['nivel_congestion'].mean()
            congestion_comunas = df[df['comuna'].isin(comunas_interseccion)]['nivel_congestion'].mean()
            
            # Desviación mayor al 30% respecto al promedio global
            return abs(congestion_comunas - congestion_global) > (0.3 * congestion_global)
        
        def generar_conclusion_comuna_atipica(datos, filtros):
            df = datos['embotellamiento']
            comunas_seleccionadas = filtros['comuna']
            
            congestion_global = df['nivel_congestion'].mean()
            congestion_comunas = df[df['comuna'].isin(comunas_seleccionadas)]['nivel_congestion'].mean()
            
            diferencia = congestion_comunas - congestion_global
            direccion = "superior" if diferencia > 0 else "inferior"
            
            return Conclusion(
                tipo=TipoConclusion.ATIPICO,
                titulo="Comportamiento Atípico por Comuna",
                mensaje=f"Las comunas seleccionadas presentan congestión {direccion} al promedio ciudad. "
                       f"Diferencia: {abs(diferencia):.1f} puntos porcentuales "
                       f"(Promedio seleccionado: {congestion_comunas:.1f}%, Global: {congestion_global:.1f}%)",
                severidad=3,
                contexto=f"Comunas: {', '.join(comunas_seleccionadas)}",
                recomendacion="Analice factores específicos de estas comunas: densidad poblacional, "
                             "infraestructura vial, oferta de transporte público.",
                datos_soporte={
                    "congestion_comunas": congestion_comunas,
                    "congestion_global": congestion_global,
                    "diferencia": diferencia
                }
            )
        
        self.agregar_regla(Regla(
            nombre="comuna_atipica",
            descripcion="Detecta comportamiento atípico de congestión por comuna",
            evaluar=evaluar_comuna_atipica,
            generar_conclusion=generar_conclusion_comuna_atipica
        ))
        
        # =========================================
        # REGLA 5: Recomendación de transporte alternativo
        # =========================================
        def evaluar_transporte_alternativo(datos, filtros):
            if 'motivos' not in datos or datos['motivos'].empty:
                return False
            
            df = datos['motivos']
            if 'medio_transporte' not in df.columns:
                return False
            
            # Si más del 60% usa carro particular, recomendar alternativas
            total = len(df)
            carro_particular = len(df[df['medio_transporte'] == 'Carro particular'])
            
            return total > 20 and (carro_particular / total) > 0.6
        
        def generar_conclusion_transporte_alternativo(datos, filtros):
            df = datos['motivos']
            total = len(df)
            carro = len(df[df['medio_transporte'] == 'Carro particular'])
            porcentaje_carro = (carro / total) * 100
            
            transporte_publico = len(df[df['medio_transporte'].isin(['Bus', 'Metro', 'Metrocable'])])
            porcentaje_tp = (transporte_publico / total) * 100
            
            return Conclusion(
                tipo=TipoConclusion.RECOMENDACION,
                titulo="Alta Dependencia del Automóvil Particular",
                mensaje=f"El {porcentaje_carro:.1f}% de viajeros usa carro particular. "
                       f"Solo el {porcentaje_tp:.1f}% utiliza transporte público.",
                severidad=2,
                contexto="Análisis de modos de transporte en el área filtrada",
                recomendacion="Promueva el uso de transporte público, bicicleta o viajes compartidos. "
                             "Considere programas de incentivos para reducción del uso del automóvil.",
                datos_soporte={
                    "porcentaje_carro": porcentaje_carro,
                    "porcentaje_transporte_publico": porcentaje_tp,
                    "total_viajeros": total
                }
            )
        
        self.agregar_regla(Regla(
            nombre="transporte_alternativo",
            descripcion="Recomienda alternativas cuando hay alta dependencia del automóvil",
            evaluar=evaluar_transporte_alternativo,
            generar_conclusion=generar_conclusion_transporte_alternativo
        ))
        
        # =========================================
        # REGLA 6: Velocidad promedio crítica
        # =========================================
        def evaluar_velocidad_critica(datos, filtros):
            if 'embotellamiento' not in datos or datos['embotellamiento'].empty:
                return False
            
            df = datos['embotellamiento']
            if 'velocidad_promedio_kmh' not in df.columns:
                return False
            
            velocidad_media = df['velocidad_promedio_kmh'].mean()
            return velocidad_media < 15  # Menos de 15 km/h es crítico
        
        def generar_conclusion_velocidad_critica(datos, filtros):
            df = datos['embotellamiento']
            velocidad_media = df['velocidad_promedio_kmh'].mean()
            velocidad_min = df['velocidad_promedio_kmh'].min()
            
            return Conclusion(
                tipo=TipoConclusion.CRITICO,
                titulo="Velocidad Promedio Crítica",
                mensaje=f"La velocidad promedio en puntos de congestión es de solo {velocidad_media:.1f} km/h. "
                       f"El punto más lento registra {velocidad_min:.1f} km/h. "
                       f"Esto indica colapso parcial de la movilidad.",
                severidad=5,
                contexto="Análisis de velocidades en puntos críticos",
                recomendacion="Urgente: Implementar medidas de gestión de tráfico. "
                             "Considere desvíos, control semafórico adaptativo o restricción vehicular temporal.",
                datos_soporte={
                    "velocidad_promedio": velocidad_media,
                    "velocidad_minima": velocidad_min,
                    "velocidad_maxima": df['velocidad_promedio_kmh'].max()
                }
            )
        
        self.agregar_regla(Regla(
            nombre="velocidad_critica",
            descripcion="Detecta velocidades promedio críticamente bajas",
            evaluar=evaluar_velocidad_critica,
            generar_conclusion=generar_conclusion_velocidad_critica
        ))
        
        # =========================================
        # REGLA 7: Sin datos suficientes (fallback)
        # =========================================
        def evaluar_sin_datos(datos, filtros):
            total_registros = sum(len(df) for df in datos.values())
            return total_registros == 0
        
        def generar_conclusion_sin_datos(datos, filtros):
            return Conclusion(
                tipo=TipoConclusion.NORMAL,
                titulo="Sin Datos para Analizar",
                mensaje="No hay datos suficientes en los filtros seleccionados para generar conclusiones.",
                severidad=1,
                contexto=f"Filtros aplicados: {filtros}",
                recomendacion="Amplíe los rangos de filtrado o seleccione diferentes parámetros.",
                datos_soporte={"filtros_aplicados": filtros}
            )
        
        self.agregar_regla(Regla(
            nombre="sin_datos",
            descripcion="Maneja el caso cuando no hay datos suficientes",
            evaluar=evaluar_sin_datos,
            generar_conclusion=generar_conclusion_sin_datos
        ))
    
    def ejecutar_analisis(
        self, 
        datos: Dict[str, pd.DataFrame], 
        filtros: Dict[str, Any]
    ) -> List[Conclusion]:
        """
        Ejecuta todas las reglas activas y retorna conclusiones ordenadas.
        
        Args:
            datos: Diccionario con los datasets filtrados
            filtros: Filtros aplicados por el usuario
            
        Returns:
            Lista de conclusiones ordenadas por severidad (descendente)
        """
        conclusiones = []
        
        for regla in self.reglas:
            conclusion = regla.ejecutar(datos, filtros)
            if conclusion:
                conclusiones.append(conclusion)
        
        # Ordenar por severidad (mayor primero)
        conclusiones.sort(key=lambda c: c.severidad, reverse=True)
        
        # Eliminar duplicados por tipo (mantener la más severa)
        tipos_vistos = set()
        conclusiones_unicas = []
        for conclusion in conclusiones:
            if conclusion.tipo not in tipos_vistos:
                tipos_vistos.add(conclusion.tipo)
                conclusiones_unicas.append(conclusion)
        
        return conclusiones_unicas


# Instancia global del motor para reutilización
motor_reglas_global = MotorReglas()


def obtener_motor_reglas() -> MotorReglas:
    """Retorna la instancia global del motor de reglas."""
    return motor_reglas_global
