import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Configuración de la App
st.set_page_config(page_title="Dashboard Dólar BCV", layout="wide")
st.title("📊 Histórico de Tasas BCV")

# Función para cargar datos desde Google Sheets
@st.cache_data(ttl=3600)
def load_data():
    sheet_id = "1_z2yK2pYwYVVhc0DzvgDfap6YEE28A2PP9MwikCRDlE"
    # Añadimos sheet=CONSOLIDADO_HISTORICO (o el nombre exacto de tu pestaña en el Google Sheet)
    # Si quieres una pestaña específica, se usa &sheet=NombreDeLaHoja
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet=CONSOLIDADO_HISTORICO"
    
    df = pd.read_csv(url)
    
    # Por si acaso las columnas vienen con espacios o nombres raros, 
    # nos aseguramos mapeando por posición si las dos primeras columnas son Fecha y Tasa:
    df.columns = [str(col).strip() for col in df.columns]
    
    if 'Vigencia' not in df.columns:
        # Si por alguna razón la columna 0 es la fecha, la renombramos por seguridad
        df = df.rename(columns={df.columns[0]: 'Vigencia', df.columns[1]: 'Tasa'})

    df['Vigencia'] = pd.to_datetime(df['Vigencia'], errors='coerce')
    df['Tasa'] = pd.to_numeric(df['Tasa'], errors='coerce')
    
    return df.dropna(subset=['Vigencia', 'Tasa'])

df = load_data()

# Filtros laterales
st.sidebar.header("Filtros")
min_date = df['Vigencia'].min().date()
max_date = df['Vigencia'].max().date()
start_date, end_date = st.sidebar.date_input("Rango de fechas", [min_date, max_date])

# Filtrar dataframe
mask = (df['Vigencia'].dt.date >= start_date) & (df['Vigencia'].dt.date <= end_date)
filtered_df = df.loc[mask]

# Acciones
col1, col2, col3 = st.columns(3)

if col1.button("Tasa Primer Día del Mes"):
    primer_dia = filtered_df[filtered_df['Vigencia'].dt.day == 1]
    st.write("Tasa al primer día de cada mes:")
    st.dataframe(primer_dia[['Vigencia', 'Tasa']])

if col2.button("Promedio Mensual"):
    promedios = filtered_df.groupby(filtered_df['Vigencia'].dt.to_period('M'))['Tasa'].mean().reset_index()
    promedios.columns = ['Mes', 'Promedio Tasa']
    st.write("Promedio de tasa mensual:")
    st.dataframe(promedios)

if col3.button("Gráfico Evolución"):
    st.line_chart(filtered_df.set_index('Vigencia')['Tasa'])
