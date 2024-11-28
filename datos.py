import requests
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import folium
from streamlit_folium import st_folium

# Función para obtener datos de países
def obtener_datos_paises():
    url = 'https://raw.githubusercontent.com/jxnscv/Programacion/main/all.json'
    respuesta = requests.get(url)
    if respuesta.status_code == 200:
        return respuesta.json()
    else:
        st.error(f'Error: {respuesta.status_code}')
        return []

# Función para convertir los datos a DataFrame
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
            'Latitud': pais.get('latlng', [0])[0],
            'Longitud': pais.get('latlng', [0])[1]
        })
    return pd.DataFrame(datos)

# Procesamiento de datos
paises = obtener_datos_paises()
df = convertir_a_dataframe(paises)

# Configuración de Streamlit
if "pagina" not in st.session_state:
    st.session_state.pagina = 1

if st.session_state.pagina == 1:
    # Página 1: Presentación del Proyecto
    st.title('Análisis de Datos de Países')
    st.write('Este proyecto analiza datos globales sobre países.')
    st.write('Aquí se pueden explorar tablas, estadísticas, gráficos y un mapa interactivo.')
    if st.button('Ir a la siguiente página'):
        st.session_state.pagina = 2

elif st.session_state.pagina == 2:
    # Página 2: Tablas de datos
    st.title('Tablas de Datos')
    st.write('### Información General')
    st.write('Tabla con datos recopilados de cada país.')
    st.write(df)

    # Estadísticas de columnas seleccionadas
    st.write('### Estadísticas')
    columna_estadisticas = st.selectbox('Selecciona una columna para estadísticas', df.columns[2:])
    if columna_estadisticas:
        media = df[columna_estadisticas].mean()
        mediana = df[columna_estadisticas].median()
        desviacion_estandar = df[columna_estadisticas].std()
        st.write(f'Media: {media}')
        st.write(f'Mediana: {mediana}')
        st.write(f'Desviación Estándar: {desviacion_estandar}')

    if st.button('Ir a la siguiente página'):
        st.session_state.pagina = 3

elif st.session_state.pagina == 3:
    # Página 3: Gráficos
    st.title('Gráficos y Mapas')
    st.write('### Visualización de Datos')

    # Selección del tipo de gráfico
    tipo_grafico = st.selectbox('Selecciona el tipo de gráfico', ['Barras', 'Líneas', 'Dispersión'])

    # Selección de ejes
    eje_x = st.selectbox('Eje X', df.columns[2:])
    eje_y = st.selectbox('Eje Y', df.columns[2:])

    # Creación del gráfico
    if eje_x and eje_y:
        plt.figure(figsize=(10, 5))
        if tipo_grafico == 'Barras':
            df.groupby(eje_x)[eje_y].mean().plot(kind='bar', color='orange')
        elif tipo_grafico == 'Líneas':
            plt.plot(df[eje_x], df[eje_y], color='green')
        elif tipo_grafico == 'Dispersión':
            plt.scatter(df[eje_x], df[eje_y], color='blue', alpha=0.6)

        plt.title(f'{eje_y} vs {eje_x}')
        plt.xlabel(eje_x)
        plt.ylabel(eje_y)
        st.pyplot(plt)

    # Mapa interactivo
    st.write('### Mapa Interactivo')
    mapa = folium.Map(location=[20, 0], zoom_start=2)
    for _, row in df.iterrows():
        folium.Marker(
            location=[row['Latitud'], row['Longitud']],
            popup=(
                f"{row['Nombre Común']} - {row['Población Total']} hab."
            )
        ).add_to(mapa)
    st_folium(mapa, width=700, height=500)

    if st.button('Volver a la primera página'):
        st.session_state.pagina = 1
