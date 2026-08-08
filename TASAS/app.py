import streamlit as st
import pandas as pd
from datetime import date

# Configuración de la App
st.set_page_config(page_title="Dashboard Dólar BCV", layout="wide")
st.title("📊 Histórico de Tasas BCV")

# Función para cargar datos desde Google Sheets con blindaje contra NaT
@st.cache_data(ttl=3600)
def load_data():
    sheet_id = "1_z2yK2pYwYVVhc0DzvgDfap6YEE28A2PP9MwikCRDlE"
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet=CONSOLIDADO_HISTORICO"
    
    df = pd.read_csv(url)
    
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
    st.error("No se pudieron cargar los datos correctamente desde Google Sheets. Revisa la hoja.")
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

    # Manejar si el usuario selecciona una sola fecha o un rango
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
        # Agrupación por mes para calcular el promedio
        promedios = filtered_df.copy()
        promedios['Mes'] = promedios['Vigencia'].dt.to_period('M').astype(str)
        prom_mensual = promedios.groupby('Mes')['Tasa'].mean().reset_index()
        prom_mensual.columns = ['Mes', 'Promedio Tasa']
        st.subheader("Promedio de tasa mensual")
        st.dataframe(prom_mensual, use_container_width=True)

    if col3.button("Gráfico Evolución"):
        st.subheader("Evolución de la Tasa")
        st.line_chart(filtered_df.set_index('Vigencia')['Tasa'])
