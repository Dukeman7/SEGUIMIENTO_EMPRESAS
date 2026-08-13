import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Configuración
st.set_page_config(page_title="Gold Data - Centro de Control", layout="wide")

SHEET_ID = "1YDV8UIyNldR9bLl71tgoI21cXvq4CIrkCSpMAmpOLvU"

@st.cache_data(ttl=30)
def cargar_sheet(sheet_name):
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
    return pd.read_csv(url)

# Cargar datos
df_legal = cargar_sheet("LEGAL")
df_econ = cargar_sheet("ECONOMICO")
df_tec = cargar_sheet("TECNICO")
df_diag = cargar_sheet("DIAGRAMACION")

# Extraer valores de la tabla resumen en DIAGRAMACION (D1:H6)
# Asumiendo que el rango D1:H6 se carga en df_diag
try:
    # Ajusta los índices según la estructura real de tu hoja DIAGRAMACION
    # H4, H5, H6 son las filas 3, 4, 5 y la columna 4 (índice 4)
    rec_total = float(str(df_diag.iloc[3, 4]).replace('%','')) 
    act_total = float(str(df_diag.iloc[4, 4]).replace('%',''))
    avance_global = float(str(df_diag.iloc[5, 4]).replace('%',''))
except:
    rec_total, act_total, avance_global = 0.0, 0.0, 0.0

# Sidebar
st.sidebar.title("🎼 Panel de Control")
vista = st.sidebar.radio("Seleccione la vista:", 
    ["📊 Resumen Ejecutivo", "🛠️ Tomo Técnico", "⚖️ Tomo Legal", "💰 Tomo Económico", "📦 Diagramación"])

# Vistas
if vista == "📊 Resumen Ejecutivo":
    st.title("🎼 Centro de Mando: Modificación de Habilitación")
    
    col1, col2 = st.columns([1, 2])
    with col1:
        # Galga Global
        fig = go.Figure(go.Indicator(mode="gauge+number", value=avance_global, 
                                     gauge={'axis': {'range': [0, 100]}, 'bar': {'color': "#00cc66"}},
                                     title={'text': "Avance Global (%)"}))
        st.plotly_chart(fig, use_container_width=True)
        
    with col2:
        st.subheader("📊 Indicadores de Gestión")
        c1, c2 = st.columns(2)
        c1.metric("Recaudos Totales (40% Peso)", f"{rec_total:.1f}%")
        c2.metric("Actividades Totales (60% Peso)", f"{act_total:.1f}%")
        st.progress(rec_total/100)
        st.progress(act_total/100)

elif vista == "🛠️ Tomo Técnico":
    st.subheader("🛠️ Detalle: Tomo Técnico")
    st.dataframe(df_tec, use_container_width=True)

elif vista == "⚖️ Tomo Legal":
    st.subheader("⚖️ Detalle: Tomo Legal")
    st.dataframe(df_legal, use_container_width=True)

elif vista == "💰 Tomo Económico":
    st.subheader("💰 Detalle: Tomo Económico")
    st.dataframe(df_econ, use_container_width=True)

elif vista == "📦 Diagramación":
    st.subheader("📦 Detalle: Diagramación y Cierre")
    st.dataframe(df_diag, use_container_width=True)
