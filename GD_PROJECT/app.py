import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Configuración
st.set_page_config(page_title="Gold Data - Centro de Control", layout="wide")

SHEET_ID = "1YDV8UIyNldR9bLl71tgoI21cXvq4CIrkCSpMAmpOLvU"

@st.cache_data(ttl=30)
def cargar_resumen():
    # Leemos solo la pestaña DIAGRAMACION
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=DIAGRAMACION"
    return pd.read_csv(url)

# Leer los datos maestros
df_resumen = cargar_resumen()

# --- EXTRACCIÓN DE VALORES ---
# Basado en tu estructura D1:H6. 
# Nota: Ajusta los índices según cómo cargue el dataframe (fila 3 es fila 4, etc.)
try:
    # Estos valores vienen de las celdas H4, H5 y H6 de tu sheet
    progreso_recaudos_total = df_resumen.iloc[3, 4]  # H4
    progreso_actividades_total = df_resumen.iloc[4, 4] # H5
    avance_global = df_resumen.iloc[5, 4] # H6
except:
    progreso_recaudos_total, progreso_actividades_total, avance_global = 0.0, 0.0, 0.0

# --- INTERFAZ ---
st.title("🎼 Centro de Control: Modificación de Habilitación")

col_a, col_b = st.columns([1, 2])

with col_a:
    st.subheader("🎯 Avance Global")
    # Galga de aguja con Plotly (ahora sí lo incluiremos, recuerda tenerlo en requirements.txt)
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
        st.progress(progreso_recaudos_total/100)
    with col2:
        st.metric("Total Ejecución (60%)", f"{progreso_actividades_total:.2f}%")
        st.progress(progreso_actividades_total/100)

st.markdown("---")
# Aquí puedes mostrar los detalles de los tomos que ya tenías
