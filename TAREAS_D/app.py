import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta

# --- CONFIGURACIÓN ---
SHEET_ID = "1GYEizLwSybQ9-ezFD1gPnSytQyaNF2DWiJrwKcR68V4"
SHEET_NAME = "TAREAS_D"

@st.cache_data(ttl=60)
def cargar_tareas():
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={SHEET_NAME}"
    df = pd.read_csv(url)
    
    # Nos quedamos estrictamente con las primeras 4 columnas (A, B, C, D)
    df = df.iloc[:, :4]
    
    # Asignamos los nombres de forma segura
    df.columns = ['Fecha', 'Estado', 'Descripcion', 'Observaciones']
    
    # Limpiamos filas vacías por si acaso
    df = df.dropna(subset=['Fecha'])
    
    # Convertimos Fecha a datetime de forma segura
    df['Fecha'] = pd.to_datetime(df['Fecha'], dayfirst=True, errors='coerce')
    
    # Convertimos Estado a booleano real (True/False)
    df['Estado'] = df['Estado'].astype(bool)
    
    return df

df = cargar_tareas()
hoy = pd.Timestamp(datetime.now().date())

# --- CÁLCULOS ---
def calcular_stats(df_filtro):
    if len(df_filtro) == 0: return 0
    return (df_filtro['Estado'].sum() / len(df_filtro)) * 100

# Filtros
hoy_df = df[df['Fecha'] == hoy]
semana_df = df[(df['Fecha'] >= hoy) & (df['Fecha'] <= hoy + timedelta(days=7))]
quincena_df = df[(df['Fecha'] >= hoy) & (df['Fecha'] <= hoy + timedelta(days=15))]

# --- DASHBOARD ---
st.title("🎛️ Centro de Control de Productividad")

# Galgas (Gauges)
cols = st.columns(3)
stats = [("Hoy", hoy_df), ("Semana", semana_df), ("Quincena", quincena_df)]

for i, (nombre, data) in enumerate(stats):
    pct = calcular_stats(data)
    with cols[i]:
        fig = go.Figure(go.Indicator(
            mode="gauge+number", value=pct,
            title={'text': nombre},
            gauge={'axis': {'range': [0, 100]}, 'bar': {'color': "#00cc66"}}
        ))
        st.plotly_chart(fig, use_container_width=True)

# Radar de Tareas Pendientes
st.subheader("🚨 Radar de Tareas (Pendientes Próximos 7 días)")
pendientes = semana_df[semana_df['Estado'] == False]
if not pendientes.empty:
    st.table(pendientes[['Fecha', 'Descripcion', 'Observaciones']])
else:
    st.success("¡Radar despejado! No hay tareas pendientes esta semana.")

# Lista Completa
with st.expander("📋 Ver todas las tareas"):
    st.dataframe(df, use_container_width=True)
