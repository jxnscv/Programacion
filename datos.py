import requests
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import folium
from streamlit_folium import st_folium
from io import BytesIO

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

# Configuración de navegación entre páginas
if "pagina" not in st.session_state:
    st.session_state.pagina = 1

# Página 1: Presentación
if st.session_state.pagina == 1:
    st.title('Análisis de Datos de Países')
    st.write('Este proyecto analiza datos globales sobre países.')
    st.write('Se incluyen tablas, estadísticas descriptivas, gráficos personalizados y un mapa interactivo.')

    col1, col2 = st.columns(2)
    with col1:
        if st.button('Ir a la siguiente página'):
            st.session_state.pagina = 2

# Página 2: Tablas
elif st.session_state.pagina == 2:
    st.title('Tablas y Estadísticas de Datos')
    st.write('### Información General de los Países')
    st.write(df)

    # Filtrar por población total
    valor_filtro = st.slider('Selecciona un valor para filtrar la población total', 0, int(df['Población Total'].max()), 100000)
    df_filtrado = df[df['Población Total'] >= valor_filtro]
    st.write('Datos filtrados:')
    st.write(df_filtrado)

    # Botón para descargar los datos como CSV y Excel
   if st.button('Descargar datos filtrados'):
    # Convertir el DataFrame a CSV
     csv = df_filtrado.to_csv(index=False)
    # Crear el botón para descargar el CSV
     st.download_button(
         label='Descargar CSV',
         data=csv,
         file_name='datos_filtrados.csv',
         mime='text/csv'
     )

    # Estadísticas de columnas seleccionadas
    st.write('### Estadísticas Descriptivas')
    columna_estadisticas = st.selectbox('Selecciona una columna para estadísticas', df.columns[2:])
    if columna_estadisticas:
        media = df[columna_estadisticas].mean()
        mediana = df[columna_estadisticas].median()
        desviacion_estandar = df[columna_estadisticas].std()
        st.write(f'Media: {media}')
        st.write(f'Mediana: {mediana}')
        st.write(f'Desviación Estándar: {desviacion_estandar}')

    col1, col2 = st.columns(2)
    with col1:
        if st.button('Volver a la primera página'):
            st.session_state.pagina = 1
    with col2:
        if st.button('Ir a la siguiente página'):
            st.session_state.pagina = 3

# Página 3: Gráficos y Mapas
elif st.session_state.pagina == 3:
    st.title('Gráficos y Mapas')
    st.write('### Gráfico Personalizado')

    # Selección del tipo de gráfico
    tipo_grafico = st.selectbox('Selecciona el tipo de gráfico', ['Barras', 'Líneas', 'Dispersión'])

    # Selección de ejes
    eje_x = st.selectbox('Selecciona la variable para el eje X', df.columns[2:], key='grafico_x')
    eje_y = st.selectbox('Selecciona la variable para el eje Y', df.columns[2:], key='grafico_y')

    # Rango para los ejes
    if eje_x and eje_y:
        min_x, max_x = st.slider(f'Selecciona el rango para {eje_x}', 
                                 float(df[eje_x].min()), 
                                 float(df[eje_x].max()), 
                                 (float(df[eje_x].min()), float(df[eje_x].max())), key='rango_x')

        min_y, max_y = st.slider(f'Selecciona el rango para {eje_y}', 
                                 float(df[eje_y].min()), 
                                 float(df[eje_y].max()), 
                                 (float(df[eje_y].min()), float(df[eje_y].max())), key='rango_y')

        # Filtrar los datos según el rango seleccionado
        df_filtrado = df[(df[eje_x] >= min_x) & (df[eje_x] <= max_x) &
                         (df[eje_y] >= min_y) & (df[eje_y] <= max_y)]

        # Creación del gráfico
        plt.figure(figsize=(10, 5))
        if tipo_grafico == 'Barras':
            df_filtrado.groupby(eje_x)[eje_y].sum().plot(kind='bar', color='lightcoral')
        elif tipo_grafico == 'Líneas':
            plt.plot(df_filtrado[eje_x], df_filtrado[eje_y], color='blue', alpha=0.7)
        elif tipo_grafico == 'Dispersión':
            plt.scatter(df_filtrado[eje_x], df_filtrado[eje_y], color='green', alpha=0.5)

        # Personalización del gráfico
        plt.title(f'{eje_y} vs {eje_x}', fontsize=16)
        plt.xlabel(eje_x, fontsize=12)
        plt.ylabel(eje_y, fontsize=12)
        plt.xticks(rotation=45)
        st.pyplot(plt)
        plt.close()

    # Mapa interactivo
    st.write('### Mapa Interactivo')
    min_poblacion_mapa, max_poblacion_mapa = st.slider(
        'Selecciona el rango de población para mostrar en el mapa',
        int(df['Población Total'].min()), 
        int(df['Población Total'].max()), 
        (int(df['Población Total'].min()), int(df['Población Total'].max()))
    )

    df_filtrado_mapa = df[(df['Población Total'] >= min_poblacion_mapa) & 
                          (df['Población Total'] <= max_poblacion_mapa)]

    mapa = folium.Map(location=[20, 0], zoom_start=2)
    for _, row in df_filtrado_mapa.iterrows():
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

    col1, col2 = st.columns(2)
    with col1:
        if st.button('Volver a la página anterior'):
            st.session_state.pagina = 2
    with col2:
        if st.button('Volver a la primera página'):
            st.session_state.pagina = 1
