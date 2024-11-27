import requests
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

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
            'Número de Zonas Horarias': len(pais.get('timezones', []))
        })
    return pd.DataFrame(datos)

paises = obtener_datos_paises()
df = convertir_a_dataframe(paises)

st.title('Análisis de Datos de Países')

color_fondo = st.color_picker('Selecciona el color de fondo', '#FFCCFF')
st.markdown(
    f"""
    <style>
    .reportview-container {{
        background: {color_fondo};
    }}
    </style>
    """,
    unsafe_allow_html=True
)

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

mostrar_graficos = st.checkbox('Mostrar gráficos')

if mostrar_graficos:
    plt.figure(figsize=(10, 5))
    df.groupby('Región Geográfica')['Población Total'].sum().plot(kind='bar', color='lightcoral')
    plt.title('Población Total por Región', fontsize=16)
    plt.xlabel('Región Geográfica', fontsize=12)
    plt.ylabel('Población Total', fontsize=12)
    plt.xticks(rotation=45)
    plt.grid(axis='y')
    st.pyplot(plt)
    
    plt.figure(figsize=(10, 5))
    plt.scatter(df['Área en km²'], df['Población Total'], alpha=0.7, c='blue
