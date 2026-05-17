# Dashboard de Movilidad Urbana - Medellín

Prototipo funcional de dashboard de movilidad urbana para análisis de dinámicas urbanas y patrones de comportamiento en la ciudad de Medellín, Antioquia, Colombia.

## 📋 Descripción

Esta aplicación Streamlit permite:

- **Visualizar información geográfica urbana** sobre OpenStreetMap
- **Activar/desactivar capas** de información (rutas, flujos, congestión, etc.)
- **Aplicar filtros independientes** por comuna, horario, motivo de viaje, etc.
- **Cruzar variables urbanas** para detectar patrones
- **Ejecutar análisis** mediante un motor de reglas
- **Generar conclusiones dinámicas** fáciles de entender

## 🎯 Objetivos

1. Claridad del mensaje
2. Facilidad de uso para usuarios no técnicos
3. Soporte para toma de decisiones
4. Experiencia visual intuitiva

## 🏗️ Arquitectura del Proyecto

```
/workspace
├── app.py                          # Aplicación principal Streamlit
├── data/                           # Directorio para archivos CSV
├── src/
│   ├── __init__.py
│   ├── config.py                   # Configuración global y constantes
│   ├── loaders/
│   │   ├── __init__.py
│   │   └── data_loader.py          # Carga de datos CSV/Excel
│   ├── processors/
│   │   ├── __init__.py
│   │   └── data_processor.py       # Procesamiento y filtrado de datos
│   ├── filters/
│   │   └── __init__.py             # Lógica de filtros (futuro)
│   ├── rules/
│   │   ├── __init__.py
│   │   └── rule_engine.py          # Motor de reglas para conclusiones
│   ├── inference/
│   │   └── __init__.py             # Futuros modelos predictivos
│   ├── renderers/
│   │   ├── __init__.py
│   │   └── map_renderer.py         # Renderizado de mapas Folium
│   ├── components/
│   │   ├── __init__.py
│   │   └── ui_components.py        # Componentes UI reutilizables
│   └── utils/
│       └── __init__.py             # Utilidades varias
└── assets/                         # Recursos estáticos (imágenes, etc.)
```

## 🚀 Instalación

### Requisitos previos

- Python 3.8 o superior
- pip (gestor de paquetes de Python)

### Pasos de instalación

1. **Clonar el repositorio** (si aplica):
```bash
cd /workspace
```

2. **Instalar dependencias**:
```bash
pip install streamlit pandas numpy folium streamlit-folium openpyxl
```

3. **Ejecutar la aplicación**:
```bash
streamlit run app.py
```

La aplicación se abrirá automáticamente en su navegador web en `http://localhost:8501`.

## 📊 Variables Principales

El sistema trabaja con las siguientes variables urbanas:

| Variable | Descripción | Icono |
|----------|-------------|-------|
| Rutas de Transporte | Red de rutas de transporte público y vías principales | 🚌 |
| Motivos de Viaje | Propósito principal de los desplazamientos | 🎯 |
| Horas de Congestión | Puntos críticos por rango horario | 🚦 |
| Flujos de Tráfico | Intensidad vehicular en vías principales | 🚗 |
| Estratificación por Comuna | División administrativa y estratificación | 🏘️ |

## 🔍 Filtros Disponibles

- **Comuna**: Filter por una o más comunas de Medellín
- **Rango Horario**: Madrugada, mañana, tarde, hora pico, noche
- **Motivo de Viaje**: Trabajo, estudio, salud, compras, ocio, etc.
- **Tipo de Ruta**: Principal, secundaria, local, peatonal
- **Nivel de Congestión**: Slider de 0-100%

## 🧠 Motor de Reglas

El sistema incluye un motor de reglas que genera conclusiones automáticas basadas en:

1. **Congestión en hora pico** - Detecta puntos críticos durante horas de mayor tráfico
2. **Flujo vehicular atípico** - Identifica sensores con flujo anormalmente alto
3. **Concentración por motivo** - Detecta dominancia de un tipo de viaje
4. **Comportamiento por comuna** - Compara congestión vs promedio ciudad
5. **Transporte alternativo** - Recomienda alternativas cuando hay alta dependencia del automóvil
6. **Velocidad crítica** - Alerta cuando velocidades son críticamente bajas

### Tipos de Conclusión

| Tipo | Icono | Color | Descripción |
|------|-------|-------|-------------|
| Normal | ✅ | Verde | Información estándar |
| Alerta | ⚠️ | Amarillo | Situación requiere atención |
| Crítico | 🔴 | Rojo | Situación urgente |
| Atípico | 📊 | Azul | Comportamiento fuera de lo normal |
| Tendencia | 📈 | Morado | Patrón detectado |
| Recomendación | 💡 | Turquesa | Sugerencia de acción |

## 💻 Uso de la Aplicación

### Paso 1: Configurar Capas
En el panel lateral izquierdo, active/desactive las capas que desea visualizar en el mapa.

### Paso 2: Aplicar Filtros
Configure los filtros según el análisis que desea realizar:
- Seleccione comunas específicas
- Elija un rango horario
- Filtre por motivos de viaje
- Ajuste el nivel de congestión

### Paso 3: Ejecutar Análisis
Presione el botón **"🔍 Ejecutar Análisis"** para que el motor de reglas genere conclusiones.

### Paso 4: Revisar Conclusiones
Las conclusiones aparecerán en el panel derecho, organizadas por severidad e incluyendo:
- Título descriptivo
- Mensaje explicativo
- Contexto del análisis
- Recomendaciones accionables

### Paso 5: Descargar Reporte (Opcional)
Use el botón "📥 Descargar reporte" para guardar las conclusiones en formato TXT.

## 📁 Formato de Datos

El sistema soporta archivos CSV con las siguientes columnas según el tipo de dato:

### Rutas de Transporte
```csv
id_ruta,nombre_ruta,tipo_ruta,comuna_inicio,comuna_fin,lat_inicio,lon_inicio,lat_fin,lon_fin,frecuencia_minutos,capacidad_pasajeros
```

### Motivos de Viaje
```csv
id_viaje,motivo,comuna_origen,comuna_destino,hora_salida,dia_semana,medio_transporte,duracion_minutos,lat_origen,lon_origen,lat_destino,lon_destino
```

### Embotellamiento
```csv
id_punto,ubicacion,vía,comuna,rango_horario,nivel_congestion,velocidad_promedio_kmh,longitud_fila_metros,tiempo_espera_minutos,lat,lon
```

### Flujos de Tráfico
```csv
id_sensor,ubicacion,vía_principal,comuna,hora_medicion,flujo_vehiculos_hora,flujo_peatones_hora,ocupacion_vial_porcentaje,velocidad_promedio_kmh,direccion_sentido,lat,lon
```

### Comunas
```csv
id_comuna,nombre_comuna,nombre_completo,estrato_predominante,poblacion_total,area_km2,densidad_hab_km2,lat_centro,lon_centro
```

## 🔄 Flujo de Datos

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   Carga     │────▶│ Procesamiento │────▶│  Filtrado   │
│   de Datos  │     │   de Datos    │     │   Filtros   │
└─────────────┘     └──────────────┘     └─────────────┘
                                                │
                                                ▼
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│ Conclusiones│◀────│   Motor de   │◀────│   Mapa      │
│   Push      │     │   Reglas     │     │ Interactivo │
└─────────────┘     └──────────────┘     └─────────────┘
```

## 🛠️ Desarrollo Futuro

La arquitectura está diseñada para escalar hacia:

- [ ] Modelos predictivos de machine learning
- [ ] Inferencia automática de patrones
- [ ] Actualización automática de datos desde APIs
- [ ] Soporte para múltiples ciudades
- [ ] Sistema de autenticación de usuarios
- [ ] Dashboards adicionales especializados
- [ ] Exportación a múltiples formatos (PDF, Excel, JSON)
- [ ] Alertas en tiempo real

## 📝 Notas Técnicas

### Caché
El sistema implementa caché de Streamlit para optimizar:
- Carga de datos (TTL: 3600 segundos)
- Procesamiento de filtros
- Renderizado de mapas

### Rendimiento
- Límite de registros para visualización: 10,000
- Muestreo automático para datasets grandes
- Renderizado condicional de capas

### Manejo de Errores
- Validación de columnas requeridas
- Manejo de archivos corruptos
- Gestión de datos faltantes
- Mensajes de error amigables

## 👥 Público Objetivo

Este dashboard está diseñado para:

- **Funcionarios públicos** de planeación urbana
- **Analistas** de movilidad y transporte
- **Ciudadanos** interesados en dinámicas urbanas
- **Investigadores** de comportamiento urbano
- **Tomadores de decisión** en infraestructura

## 📄 Licencia

Prototipo desarrollado con fines demostrativos y educativos.

## 🤝 Contribuciones

Para contribuir al desarrollo:

1. Fork del proyecto
2. Crear rama de feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit de cambios (`git commit -m 'Añadir nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abrir Pull Request

## 📞 Soporte

Para preguntas o problemas técnicos, consulte la documentación de cada módulo o revise los comentarios en el código fuente.

---

**Dashboard de Movilidad Urbana - Medellín** © 2024
