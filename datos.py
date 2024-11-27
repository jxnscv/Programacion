import requests
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import io
import time

def obtener_datos_paises():
    url = 'https://restcountries.com/v3.1/all'
    intentos = 5  # Número de intentos
    for intento in range(intentos):
        try:
            respuesta = requests.get(url)
            respuesta.raise_for_status()  # Lanza un error si la respuesta no es 200
            return respuesta.json()
        except requests.exceptions.HTTPError as http_err:
            st.error(f"Error HTTP: {http_err}")
            break  # Salir si hay un error HTTP
        except requests.exceptions.ConnectionError as conn_err:
            st.warning(f"Error de conexión: {conn_err}. Intentando de nuevo...")
            time.sleep(2)  # Esperar 2 segundos antes de reintentar
        except requests.exceptions.Timeout:
            st.error("La solicitud ha tardado demasiado tiempo en responder.")
            break
        except requests.exceptions.RequestException as req_err:
            st.error(f"Error inesperado: {req_err}")
            break
    return None  # Devuelve None si hay un error

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

# Obtener datos de países
paises = obtener_datos_paises()
if paises is not None:
    df = convertir_a_dataframe(paises)

    st.title('Análisis de Datos de Países')

    st.sidebar.title("Navegación")
    pagina = st.sidebar.radio("Selecciona una página", ["Descripción", "Interacción con Datos", "Gráficos Interactivos"])

    if pagina == "Descripción":
        st.title("Descripción del Proyecto")
        st.write("""
        Esta aplicación web utiliza datos de la API [REST Countries](https://restcountries.com/v3.1/all).
        Permite explorar información sobre países, incluyendo su población, área, idiomas, fronteras y más.
        La aplicación está dividida en tres secciones principales:
        - **Descripción**: Información sobre el proyecto y la fuente de datos.
        - **Interacción con Datos**: Visualiza y filtra los datos obtenidos.
        - **Gráficos Interactivos**: Crea gráficos dinámicos basados en los datos.
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
        df_filtrado = df[(df["Población
