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

# --- CÁLCULOS MEJORADOS ---
# Convertimos todo a formato fecha sin hora para comparar solo días
df['Fecha_Solo'] = df['Fecha'].dt.normalize()
hoy = pd.Timestamp(datetime.now().date())

# Aseguramos que el estado sea realmente booleano
# Si en tu sheet escribes "TRUE", pandas a veces lo lee como texto. 
# Esto fuerza la conversión:
df['Estado'] = df['Estado'].apply(lambda x: str(x).lower() == 'true')

# Filtros ajustados
hoy_df = df[df['Fecha_Solo'] == hoy]
# Incluimos desde el pasado hasta 7 días en el futuro para que nada se pierda
semana_df = df[(df['Fecha_Solo'] <= hoy + timedelta(days=7))]
quincena_df = df[(df['Fecha_Solo'] <= hoy + timedelta(days=15))]

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

# Radar de Tareas Pendientes (AHORA SI TE LAS MOSTRARÁ)
st.subheader("🚨 Radar de Tareas (Pendientes)")
# Filtramos todas las que sean False y tengan fecha
pendientes = df[(df['Estado'] == False) & (df['Fecha_Solo'] >= hoy - timedelta(days=2))].sort_values('Fecha')
if not pendientes.empty:
    st.table(pendientes[['Fecha', 'Descripcion', 'Observaciones']])
else:
    st.success("¡Radar despejado!")

# Lista Completa
with st.expander("📋 Ver todas las tareas"):
    st.dataframe(df, use_container_width=True)
