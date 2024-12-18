import requests
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import folium
from streamlit_folium import st_folium
import io

# Función para obtener datos de países
def obtener_datos_paises():
    url = 'https://raw.githubusercontent.com/jxnscv/Programacion/main/all.json' #aquí deberia ir "https://restcountries.com/v3.1/all" si no diera error.
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
            'Latitud': pais.get('latlng', [None, None])[0],
            'Longitud': pais.get('latlng', [None, None])[1]
        })
    return pd.DataFrame(datos)

# Obtener los datos
paises = obtener_datos_paises()
df = convertir_a_dataframe(paises)

# Configuración de la interfaz de Streamlit
st.title('Análisis de Datos de Países')

st.sidebar.title("Navegación")
pagina = st.sidebar.radio("Selecciona una página", ["Descripción", "Interacción con Datos", "Gráficos Interactivos", "Mapa Interactivo"])

if pagina == "Descripción":
    st.title("Descripción del Proyecto")
    st.write("""
    Esta aplicación web utiliza datos de la API [REST Countries](https://restcountries.com/v3.1/all).
    Permite explorar información sobre países, incluyendo su población, área, idiomas, fronteras y más.
    La aplicación está dividida en cuatro secciones principales:
    - **Descripción**: Información sobre el proyecto y la fuente de datos.
    - **Interacción con Datos**: Visualiza y filtra los datos obtenidos.
    - **Gráficos Interactivos**: Crea gráficos dinámicos basados en los datos.
    - **Mapa Interactivo**: Visualiza los países en un mapa interactivo.
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
    valor_filtro = st.slider("Selecciona un valor para filtrar la población total", 0, int(df["Población Total"].max()), 100000)
    rango_min, rango_max = st.slider("Selecciona un rango de población", int(df["Población Total"].min()), int(df["Población Total"].max()), (0, int(df["Población Total"].max())))
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

elif pagina == "Mapa Interactivo":
    st.title("Mapa Interactivo de Países")
    
    st.write("Aquí puedes ver la ubicación de los países en el mapa según su población.")
    
    min_poblacion, max_poblacion = st.slider(
        "Selecciona un rango de población para mostrar en el mapa",
        int(df['Población Total'].min()), 
        int(df['Población Total'].max()), 
        (int(df['Población Total'].min()), int(df['Población Total'].max()))
    )

    df_filtrado_mapa = df[(df['Población Total'] >= min_poblacion) & 
                          (df['Población Total'] <= max_poblacion)]

    mapa = folium.Map(location=[20, 0], zoom_start=2)
    for _, row in df_filtrado_mapa.iterrows():
        latlng = row.get('Latitud'), row.get('Longitud')
        if latlng and None not in latlng:  # Solo agregar si existen las coordenadas
            popup_info = (
                f"<strong>Nombre Común:</strong> {row['Nombre Común']}<br>"
                f"<strong>Región Geográfica:</strong> {row['Región Geográfica']}<br>"
                f"<strong>Población Total:</strong> {row['Población Total']}<br>"
                f"<strong>Área en km²:</strong> {row['Área en km²']}<br>"
            )
            folium.Marker(
                location=latlng,
                popup=popup_info,
                icon=folium.Icon(color='blue')
            ).add_to(mapa)
    
    st_folium(mapa, width=700, height=500)
