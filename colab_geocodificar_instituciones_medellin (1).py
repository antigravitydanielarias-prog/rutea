
# ============================================================
# COLAB: GEOCODIFICAR INSTITUCIONES EDUCATIVAS DE MEDELLÍN
# ============================================================

!pip install pandas geopy folium unidecode -q

from google.colab import files
import pandas as pd
import numpy as np
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
import folium
from folium.plugins import MarkerCluster, HeatMap

uploaded = files.upload()
file_name = list(uploaded.keys())[0]

df = pd.read_csv(file_name)

geolocator = Nominatim(user_agent="rutea_instituciones_medellin")
geocode = RateLimiter(
    geolocator.geocode,
    min_delay_seconds=1,
    max_retries=2,
    error_wait_seconds=2
)

latitudes = []
longitudes = []
fuentes = []
precisiones = []

for i, query in enumerate(df["consulta_geocodificacion"].fillna("")):
    query = str(query).strip()

    if query == "" or query.lower() == "nan":
        latitudes.append(np.nan)
        longitudes.append(np.nan)
        fuentes.append("sin_direccion")
        precisiones.append("sin_direccion")
        continue

    try:
        loc = geocode(query)
        if loc:
            latitudes.append(loc.latitude)
            longitudes.append(loc.longitude)
            fuentes.append("Nominatim/OpenStreetMap")
            precisiones.append(loc.raw.get("class", "geocoded"))
        else:
            latitudes.append(np.nan)
            longitudes.append(np.nan)
            fuentes.append("no_encontrado")
            precisiones.append("no_encontrado")
    except Exception as e:
        latitudes.append(np.nan)
        longitudes.append(np.nan)
        fuentes.append("error")
        precisiones.append(str(e)[:80])

    if i % 10 == 0:
        print(f"Procesadas {i} de {len(df)} direcciones")

df["latitud"] = latitudes
df["longitud"] = longitudes
df["fuente_coordenadas"] = fuentes
df["precision_geocodificacion"] = precisiones

df_geo = df.dropna(subset=["latitud", "longitud"]).copy()
df_geo = df_geo[
    (df_geo["latitud"].between(6.0, 6.5)) &
    (df_geo["longitud"].between(-75.8, -75.3))
].copy()

print("Total registros:", len(df))
print("Con coordenadas válidas en Medellín:", len(df_geo))
print("Porcentaje geocodificado:", round(len(df_geo) / len(df) * 100, 2), "%")

df.to_csv("instituciones_educativas_medellin_con_coordenadas.csv", index=False, encoding="utf-8-sig")
df_geo.to_csv("instituciones_educativas_medellin_con_coordenadas_validas.csv", index=False, encoding="utf-8-sig")

centro_medellin = [6.2442, -75.5812]

mapa = folium.Map(location=centro_medellin, zoom_start=12, tiles="OpenStreetMap")
cluster = MarkerCluster().add_to(mapa)

for _, row in df_geo.iterrows():
    popup = f"""
    <b>{row.get('nombre_institucion','')}</b><br>
    Comuna: {row.get('comuna','')} - {row.get('nombre_comuna','')}<br>
    Tipo: {row.get('tipo_organizacion','')}<br>
    Dirección: {row.get('direccion_original','')}<br>
    Latitud: {row.get('latitud','')}<br>
    Longitud: {row.get('longitud','')}
    """

    folium.Marker(
        location=[row["latitud"], row["longitud"]],
        popup=folium.Popup(popup, max_width=350),
        tooltip=row.get("nombre_institucion", "Institución educativa")
    ).add_to(cluster)

mapa.save("mapa_instituciones_educativas_medellin.html")

mapa_calor = folium.Map(location=centro_medellin, zoom_start=12, tiles="OpenStreetMap")
HeatMap(df_geo[["latitud", "longitud"]].values.tolist(), radius=15, blur=20).add_to(mapa_calor)
mapa_calor.save("mapa_calor_instituciones_educativas_medellin.html")

files.download("instituciones_educativas_medellin_con_coordenadas.csv")
files.download("instituciones_educativas_medellin_con_coordenadas_validas.csv")
files.download("mapa_instituciones_educativas_medellin.html")
files.download("mapa_calor_instituciones_educativas_medellin.html")

