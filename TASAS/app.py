import streamlit as st
import pandas as pd
import requests
import io
from datetime import date

# Configuración de la App
st.set_page_config(page_title="Dashboard Dólar BCV (2025-2026)", layout="wide")
st.title("📊 Histórico de Tasas BCV (2025-2026)")

# Función para cargar datos de forma segura usando requests
@st.cache_data(ttl=3600)
def load_data():
    url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQUsGQIAmQ695PmJqoPcBcA78T3TIX-QUEn52lF9jkaY2WFWw8UjWYEZw6mUaJtu2MmxG6q_2vDMG51/pub?gid=0&single=true&output=csv"
    
    # Descargamos el contenido mediante requests para evitar que pandas confunda la URL con un archivo local
    response = requests.get(url)
    response.raise_for_status() # Lanza error si falla la conexión
    
    df = pd.read_csv(io.StringIO(response.text))
    
    # Limpieza de nombres de columnas
    df.columns = [str(col).strip() for col in df.columns]
    if 'Vigencia' not in df.columns:
        df = df.rename(columns={df.columns[0]: 'Vigencia', df.columns[1]: 'Tasa'})

    # Conversión forzosa eliminando nulos
    df['Vigencia'] = pd.to_datetime(df['Vigencia'], errors='coerce')
    df['Tasa'] = pd.to_numeric(df['Tasa'], errors='coerce')
    
    df = df.dropna(subset=['Vigencia', 'Tasa'])
    
    # Ordenar por fecha
    df = df.sort_values('Vigencia').reset_index(drop=True)
    return df

df = load_data()

# Validar que el dataframe no esté vacío
if df.empty:
    st.error("No se pudieron cargar los datos correctamente. Revisa el formato de las columnas en la hoja.")
else:
    # Filtros laterales con fechas seguras por defecto
    st.sidebar.header("Filtros")
    min_date = df['Vigencia'].min().date()
    max_date = df['Vigencia'].max().date()
    
    date_range = st.sidebar.date_input(
        "Rango de fechas",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )

    if isinstance(date_range, tuple) and len(date_range) == 2:
        start_date, end_date = date_range
    else:
        start_date, end_date = min_date, max_date

    # Filtrar dataframe
    mask = (df['Vigencia'].dt.date >= start_date) & (df['Vigencia'].dt.date <= end_date)
    filtered_df = df.loc[mask]

    # Acciones con botones
    col1, col2, col3 = st.columns(3)

    if col1.button("Tasa Primer Día del Mes"):
        primer_dia = filtered_df[filtered_df['Vigencia'].dt.day == 1]
        st.subheader("Tasa al primer día de cada mes")
        st.dataframe(primer_dia[['Vigencia', 'Tasa']], use_container_width=True)

    if col2.button("Promedio Mensual"):
        promedios = filtered_df.copy()
        promedios['Mes'] = promedios['Vigencia'].dt.to_period('M').astype(str)
        prom_mensual = promedios.groupby('Mes')['Tasa'].mean().reset_index()
        prom_mensual.columns = ['Mes', 'Promedio Tasa']
        st.subheader("Promedio de tasa mensual")
        st.dataframe(prom_mensual, use_container_width=True)

    if col3.button("Gráfico Evolución"):
        st.subheader("Evolución de la Tasa")
        st.line_chart(filtered_df.set_index('Vigencia')['Tasa'])
