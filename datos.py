import requests
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import io
import folium
from folium.plugins import MarkerCluster

# Función para obtener los datos de países desde la API REST Countries
def obtener_datos_paises():
    url = 'https://restcountries.com/v3.1/all'
    respuesta = requests.get(url)
    if respuesta.status_code == 200:
        return respuesta.json()
    else:
        st.error(f'Error: {respuesta.status_code}')
        return []

# Función para convertir los datos de los países a un dataframe
def convertir_a_dataframe(paises):
    datos = []
    for pais in paises:
        datos.append({
            'Nombre Común': pais.get('name', {}).get('common', 'No disponible'),
            'Región Geográfica': pais.get('region', 'No disponible'),
            'Población Total': pais.get('population', 0),
            'Área en km²': pais.get('area', 0),
            'Número de Fronteras': len(pais.get('borders', [])),
            'Número de Idiomas Oficiales': len(pais.get('languages', {})),
            'Número de Zonas Horarias': len(pais.get('timezones', [])),
            'Latitud': pais.get('latlng', [None, None])[0],  # Latitud
            'Longitud': pais.get('latlng', [None, None])[1]  # Longitud
        })
    return pd.DataFrame(datos)

# Obtener y convertir los datos de los países
paises = obtener_datos_paises()
df = convertir_a_dataframe(paises)

st.title('Análisis de Datos de Países')

# Barra lateral para navegar entre las páginas
st.sidebar.title("Navegación")
pagina = st.sidebar.radio("Selecciona una página", ["Descripción", "Interacción con Datos", "Gráficos Interactivos", "Mapa de Países"])

if pagina == "Descripción":
    st.title("Descripción del Proyecto")
    st.write("""
    Esta aplicación web utiliza datos de la API [REST Countries](https://restcountries.com/v3.1/all).
    Permite explorar información sobre países, incluyendo su población, área, idiomas, fronteras y más.
    La aplicación está dividida en tres secciones principales:
    - **Descripción**: Información sobre el proyecto y la fuente de datos.
    - **Interacción con Datos**: Visualiza y filtra los datos obtenidos.
    - **Gráficos Interactivos**: Crea gráficos dinámicos basados en los datos.
    - **Mapa de Países**: Visualiza los países en un mapa interactivo con sus coordenadas geográficas.
    """)

elif pagina == "Interacción con Datos":
    st.title("Interacción con Datos")
    st.subheader("Datos Originales")
    
    if st.checkbox('Mostrar datos originales'):
        st.dataframe(df)

    st.subheader("Estadísticas")
    columna_estadisticas = st.selectbox("Selecciona una columna numérica para calcular estadísticas", ["Población Total", "Área en km²"])
    if columna_estadisticas:
        st.write(f"**Media**: {df[columna_estadisticas].mean():,.2f}")
        st.write(f"**Mediana**: {df[columna_estadisticas].median():,.2f}")
        st.write(f"**Desviación Estándar**: {df[columna_estadisticas].std():,.2f}")

    st.subheader("Ordenar Datos")
    columna_ordenar = st.selectbox("Selecciona una columna para ordenar", df.columns)
    orden = st.radio("Orden", ["Ascendente", "Descendente"])
    if columna_ordenar:
        df_ordenado = df.sort_values(by=columna_ordenar, ascending=(orden == "Ascendente"))
        st.dataframe(df_ordenado)

    st.subheader("Filtrar por Población")
    rango_min, rango_max = st.slider("Selecciona un rango de población", 
                                     int(df["Población Total"].min()), 
                                     int(df["Población Total"].max()), 
                                     (int(df["Población Total"].min()), int(df["Población Total"].max())))
    df_filtrado = df[(df["Población Total"] >= rango_min) & (df["Población Total"] <= rango_max)]
    st.dataframe(df_filtrado)

    if st.button('Descargar datos filtrados'):
        csv = df_filtrado.to_csv(index=False)
        st.download_button('Descargar CSV', csv, 'datos_filtrados.csv', 'text/csv')

elif pagina == "Gráficos Interactivos":
    st.title("Gráficos Interactivos")
    st.subheader("Configurar Gráfico")
    x_var = st.selectbox("Eje X", ["Población Total", "Área en km²", "Número de Fronteras", "Número de Idiomas Oficiales", "Número de Zonas Horarias"])
    y_var = st.selectbox("Eje Y", ["Población Total", "Área en km²", "Número de Fronteras", "Número de Idiomas Oficiales", "Número de Zonas Horarias"])
    tipo_grafico = st.selectbox("Tipo de Gráfico", ["Dispersión", "Línea", "Barras"])

    fig, ax = plt.subplots()
    if tipo_grafico == "Dispersión":
        ax.scatter(df[x_var], df[y_var], alpha=0.7)
    elif tipo_grafico == "Línea":
        ax.plot(df[x_var], df[y_var], marker='o')
    elif tipo_grafico == "Barras":
        ax.bar(df[x_var], df[y_var])

    ax.set_xlabel(x_var)
    ax.set_ylabel(y_var)
    ax.set_title(f"{tipo_grafico} entre {x_var} y {y_var}")
    st.pyplot(fig)

    buffer = io.BytesIO()
    fig.savefig(buffer, format="png")
    buffer.seek(0)
    st.download_button("Descargar Gráfico", buffer, file_name="grafico.png")

elif pagina == "Mapa de Países":
    st.title("Mapa Interactivo de Países")
    
    # Crear un mapa centrado en el mundo
    m = folium.Map(location=[20, 0], zoom_start=2)

    # Crear un MarkerCluster para agrupar los países en el mapa
    marker_cluster = MarkerCluster().add_to(m)

    # Añadir los marcadores para cada país en el mapa
    for _, row in df.iterrows():
        lat, lon = row['Latitud'], row['Longitud']
        if pd.notnull(lat) and pd.notnull(lon):
            folium.Marker(
                location=[lat, lon],
                popup=row['Nombre Común'],
                icon=folium.Icon(color='blue')
            ).add_to(marker_cluster)

    # Mostrar el mapa en Streamlit
    st.write("Mapa interactivo de países con latitudes y longitudes.")
    st.map(m)
