import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Configuración
st.set_page_config(page_title="Gold Data - Centro de Control", layout="wide")

SHEET_ID = "1YDV8UIyNldR9bLl71tgoI21cXvq4CIrkCSpMAmpOLvU"

@st.cache_data(ttl=30)
def cargar_resumen():
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=DIAGRAMACION"
    return pd.read_csv(url)

def limpiar_valor(val):
    """Convierte de forma segura celdas con %, texto o números a float"""
    if pd.isna(val):
        return 0.0
    if isinstance(val, str):
        val = val.replace('%', '').strip()
        try:
            return float(val)
        except ValueError:
            return 0.0
    try:
        return float(val)
    except:
        return 0.0

# Leer los datos maestros
df_resumen = cargar_resumen()

# --- EXTRACCIÓN SEGURA ---
try:
    # Ajusta los índices según la posición exacta de tus celdas en D1:H6
    raw_rec = df_resumen.iloc[2, 4] if len(df_resumen) > 2 else 0.0
    raw_act = df_resumen.iloc[3, 4] if len(df_resumen) > 3 else 0.0
    raw_glob = df_resumen.iloc[4, 4] if len(df_resumen) > 4 else 0.0
    
    progreso_recaudos_total = limpiar_valor(raw_rec)
    progreso_actividades_total = limpiar_valor(raw_act)
    avance_global = limpiar_valor(raw_glob)
except Exception as e:
    st.error(f"Error leyendo la tabla maestra: {e}")
    progreso_recaudos_total, progreso_actividades_total, avance_global = 0.0, 0.0, 0.0

# --- INTERFAZ ---
st.title("🎼 Centro de Control: Modificación de Habilitación")

col_a, col_b = st.columns([1, 2])

with col_a:
    st.subheader("🎯 Avance Global")
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = avance_global,
        gauge = {'axis': {'range': [0, 100]}, 'bar': {'color': "#00cc66"}},
        title = {'text': "Avance Total (%)"}
    ))
    st.plotly_chart(fig, use_container_width=True)

with col_b:
    st.subheader("📊 Resumen por Nivel")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Recaudos (40%)", f"{progreso_recaudos_total:.2f}%")
        st.progress(min(max(progreso_recaudos_total/100, 0.0), 1.0))
    with col2:
        st.metric("Total Ejecución (60%)", f"{progreso_actividades_total:.2f}%")
        st.progress(min(max(progreso_actividades_total/100, 0.0), 1.0))
