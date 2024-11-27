import requests
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import folium
from streamlit_folium import st_folium

def obtener_datos_paises():
    url = 'https://raw.githubusercontent.com/jxnscv/Programacion/main/all.json'
    respuesta = requests.get(url)
    if respuesta.status_code == 200:
        return respuesta.json()
    else:
        st.error(f'Error: {respuesta.status_code}')
        return []

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

paises = obtener_datos_paises()
df = convertir_a_dataframe(paises)

st.title('Análisis de Datos de Países')
st.write('Este proyecto analiza diversos datos sobre países, incluyendo población, área, fronteras, idiomas y zonas horarias.')

if st.checkbox('Mostrar datos originales'):
    st.write(df)

columna_estadisticas = st.selectbox('Selecciona una columna para calcular estadísticas', df.columns[2:])
if columna_estadisticas:
    media = df[columna_estadisticas].mean()
    mediana = df[columna_estadisticas].median()
    desviacion_estandar = df[columna_estadisticas].std()
    st.write(f'Media: {media}')
    st.write(f'Mediana: {mediana}')
    st.write(f'Desviación Estándar: {desviacion_estandar}')

columna_ordenar = st.selectbox('Selecciona una columna para ordenar', df.columns)
orden = st.radio('Selecciona el orden', ('Ascendente', 'Descendente'))

if columna_ordenar:
    df_ordenado = df.sort_values(by=columna_ordenar, ascending=(orden == 'Ascendente'))
    st.write(df_ordenado)

valor_filtro = st.slider('Selecciona un valor para filtrar la población total', 0, int(df['Población Total'].max()), 100000)
df_filtrado = df[df['Población Total'] >= valor_filtro]
st.write('Datos filtrados:')
st.write(df_filtrado)

if st.button('Descargar datos filtrados'):
    csv = df_filtrado.to_csv(index=False)
    st.download_button('Descargar CSV', csv, 'datos_filtrados.csv', 'text/csv')
    excel = df_filtrado.to_excel(index=False, engine='openpyxl')
    st.download_button('Descargar Excel', excel, 'datos_filtrados.xlsx', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

st.subheader('Gráficos de Análisis')

mostrar_graficos = st.checkbox('Mostrar Gráficos')
if mostrar_graficos:
# Gráfico 1: Población Total por Región
    st.subheader('Gráfico 1: Población Total por Región')

    min_area_1, max_area_1 = st.slider('Selecciona el rango de área en km² para el gráfico 1',
                                     min_value=int(df['Área en km²'].min()),
                                     max_value=int(df['Área en km²'].max()),
                                     value=(0, int(df['Área en km²'].max())))

    min_poblacion_1, max_poblacion_1 = st.slider('Selecciona el rango de población total para el gráfico 1',
                                               min_value=int(df['Población Total'].min()),
                                               max_value=int(df['Población Total'].max()),
                                               value=(0, int(df['Población Total'].max())))

    df_filtrado_grafico_1 = df[(df['Área en km²'] >= min_area_1) & (df['Área en km²'] <= max_area_1) &
                            (df['Población Total'] >= min_poblacion_1) & (df['Población Total'] <= max_poblacion_1)]

    eje_x_grafico_1 = st.selectbox('Selecciona la variable para el eje X del gráfico 1', df.columns[2:])
    eje_y_grafico_1 = 'Población Total'

    with st.expander('Mostrar Gráfico 1'):
        plt.figure(figsize=(10, 5))
        df_filtrado_grafico_1.groupby('Región Geográfica')[eje_y_grafico_1].sum().plot(kind='bar', color='lightcoral')
        plt.title('Población Total por Región', fontsize=16)
        plt.xlabel('Región Geográfica', fontsize=12)
        plt.ylabel(eje_y_grafico_1, fontsize=12)
        plt.xticks(rotation=45)
        plt.grid(axis='y')
        st.pyplot(plt)
        plt.close()

# Gráfico 2: Relación entre Área y Población
    st.subheader('Gráfico 2: Relación entre Área y Población')

    min_area_2, max_area_2 = st.slider('Selecciona el rango de área en km² para el gráfico 2',
                                     min_value=int(df['Área en km²'].min()),
                                     max_value=int(df['Área en km²'].max()),
                                     value=(0, int(df['Área en km²'].max())))

    min_poblacion_2, max_poblacion_2 = st.slider('Selecciona el rango de población total para el gráfico 2',
                                               min_value=int(df['Población Total'].min()),
                                               max_value=int(df['Población Total'].max()),
                                               value=(0, int(df['Población Total'].max())))

    df_filtrado_grafico_2 = df[(df['Área en km²'] >= min_area_2) & (df['Área en km²'] <= max_area_2) &
                            (df['Población Total'] >= min_poblacion_2) & (df['Población Total'] <= max_poblacion_2)]

    eje_x_grafico_2 = st.selectbox('Selecciona la variable para el eje X del gráfico 2', df.columns[2:])
    eje_y_grafico_2 = 'Población Total'

    with st.expander('Mostrar Gráfico 2'):
        plt.figure(figsize=(10, 5))
        plt.scatter(df_filtrado_grafico_2[eje_x_grafico_2], df_filtrado_grafico_2[eje_y_grafico_2], color='blue', alpha=0.5)
        plt.title('Relación entre Área y Población', fontsize=16)
        plt.xlabel(eje_x_grafico_2, fontsize=12)
        plt.ylabel(eje_y_grafico_2, fontsize=12)
        st.pyplot(plt)
        plt.close() de Países')
        mapa = folium.Map(location=[20, 0], zoom_start=2)
        for i in range(len(df_filtrado_graficos)):
            popup_info = (
                f"<strong>Nombre Común:</strong> {df_filtrado_graficos.iloc[i]['Nombre Común']}<br>"
                f"<strong>Región Geográfica:</strong> {df_filtrado_graficos.iloc[i]['Región Geográfica']}<br>"
                f"<strong>Población Total:</strong> {df_filtrado_graficos.iloc[i]['Población Total']}<br>"
                f"<strong>Área en km²:</strong> {df_filtrado_graficos.iloc[i]['Área en km²']}<br>"
                f"<strong>Número de Fronteras:</strong> {df_filtrado_graficos.iloc[i]['Número de Fronteras']}<br>"
                f"<strong>Número de Idiomas Oficiales:</strong> {df_filtrado_graficos.iloc[i]['Número de Idiomas Oficiales']}<br>"
                f"<strong>Número de Zonas Horarias:</strong> {df_filtrado_graficos.iloc[i]['Número de Zonas Horarias']}<br>"
            )
        
            folium.Marker(
                location=[df_filtrado_graficos.iloc[i]['Latitud'], df_filtrado_graficos.iloc[i]['Longitud']],
                popup=popup_info,
                icon=folium.Icon(color='blue')
            ).add_to(mapa)

        st_folium(mapa, width=700, height=500)
        


