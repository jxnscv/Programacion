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
st.title('Análisis de Datos de Países')
st.write('Este proyecto analiza diversos datos sobre países, incluyendo población, área, fronteras, idiomas y zonas horarias.')

# Mostrar datos originales
if st.checkbox('Mostrar datos originales'):
    st.write(df)

# Estadísticas de columnas seleccionadas
columna_estadisticas = st.selectbox('Selecciona una columna para calcular estadísticas', df.columns[2:])
if columna_estadisticas:
    media = df[columna_estadisticas].mean()
    mediana = df[columna_estadisticas].median()
    desviacion_estandar = df[columna_estadisticas].std()
    st.write(f'Media: {media}')
    st.write(f'Mediana: {mediana}')
    st.write(f'Desviación Estándar: {desviacion_estandar}')

# Ordenar por columna
columna_ordenar = st.selectbox('Selecciona una columna para ordenar', df.columns)
orden = st.radio('Selecciona el orden', ('Ascendente', 'Descendente'))
if columna_ordenar:
    df_ordenado = df.sort_values(by=columna_ordenar, ascending=(orden == 'Ascendente'))
    st.write(df_ordenado)

# Filtrar por población total
valor_filtro = st.slider('Selecciona un valor para filtrar la población total', 0, int(df['Población Total'].max()), 100000)
df_filtrado = df[df['Población Total'] >= valor_filtro]
st.write('Datos filtrados:')
st.write(df_filtrado)

# Botón para descargar datos filtrados
if st.button('Descargar datos filtrados'):
    csv = df_filtrado.to_csv(index=False)
    st.download_button('Descargar CSV', csv, 'datos_filtrados.csv', 'text/csv')

# Gráficos de análisis
st.subheader('Gráficos de Análisis')
mostrar_graficos = st.checkbox('Mostrar Gráficos')
if mostrar_graficos:
    # Gráfico 1: Población Total por Región
    st.subheader('Gráfico 1: Población Total por Región')
    plt.figure(figsize=(10, 5))
    df.groupby('Región Geográfica')['Población Total'].sum().plot(kind='bar', color='lightcoral')
    plt.title('Población Total por Región', fontsize=16)
    plt.xlabel('Región Geográfica', fontsize=12)
    plt.ylabel('Población Total', fontsize=12)
    plt.xticks(rotation=45)
    st.pyplot(plt)
    plt.close()

    # Gráfico 2: Relación entre Área y Población
    st.subheader('Gráfico 2: Relación entre Área y Población')
    plt.figure(figsize=(10, 5))
    plt.scatter(df['Área en km²'], df['Población Total'], color='blue', alpha=0.5)
    plt.title('Relación entre Área y Población', fontsize=16)
    plt.xlabel('Área en km²', fontsize=12)
    plt.ylabel('Población Total', fontsize=12)
    st.pyplot(plt)
    plt.close()

    # Mapa interactivo
    st.subheader('Mapa Interactivo')
    mapa = folium.Map(location=[20, 0], zoom_start=2)
    for _, row in df.iterrows():
        popup_info = (
            f"<strong>Nombre Común:</strong> {row['Nombre Común']}<br>"
            f"<strong>Región Geográfica:</strong> {row['Región Geográfica']}<br>"
            f"<strong>Población Total:</strong> {row['Población Total']}<br>"
            f"<strong>Área en km²:</strong> {row['Área en km²']}<br>"
        )
        folium.Marker(
            location=[row['Latitud'], row['Longitud']],
            popup=popup_info,
            icon=folium.Icon(color='blue')
        ).add_to(mapa)
    st_folium(mapa, width=700, height=500)
