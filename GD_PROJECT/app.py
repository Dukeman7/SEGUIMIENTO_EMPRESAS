import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="Gold Data - Centro de Control", layout="wide")
SHEET_ID = "1YDV8UIyNldR9bLl71tgoI21cXvq4CIrkCSpMAmpOLvU"

@st.cache_data(ttl=30)
def cargar_sheet(sheet_name):
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
    return pd.read_csv(url)

df_legal = cargar_sheet("LEGAL")
df_econ = cargar_sheet("ECONOMICO")
df_tec = cargar_sheet("TECNICO")
df_diag = cargar_sheet("DIAGRAMACION")

# --- LECTURA DE LOS TOTALES EN H4, H5, H6 ---
try:
    # Supongamos que H4, H5 y H6 están en la columna H (índice 4 o 7 dependiendo de cómo se cargue el DF)
    # Limpiamos el símbolo % y convertimos
    aporte_recaudos_global = float(str(df_diag.iloc[3, 4]).replace('%','')) # H4 (Ej: 8%)
    aporte_actividades_global = float(str(df_diag.iloc[4, 4]).replace('%','')) # H5 (Ej: 12%)
    avance_global = float(str(df_diag.iloc[5, 4]).replace('%','')) # H6 (Ej: 20%)
except:
    aporte_recaudos_global, aporte_actividades_global, avance_global = 0.0, 0.0, 0.0

# Sidebar
st.sidebar.title("🎼 Panel de Control")
vista = st.sidebar.radio("Seleccione la vista:", ["📊 Resumen Ejecutivo", "🛠️ Tomo Técnico", "⚖️ Tomo Legal", "💰 Tomo Económico", "📦 Diagramación"])

if vista == "📊 Resumen Ejecutivo":
    st.title("🎼 Centro de Mando: Modificación de Habilitación")
    
    col1, col2 = st.columns([1, 2])
    with col1:
        # Galga Global (Se moverá al 20% si Legal está 100% listo)
        fig = go.Figure(go.Indicator(mode="gauge+number", value=avance_global, 
                                     gauge={'axis': {'range': [0, 100]}, 'bar': {'color': "#00cc66"}},
                                     title={'text': "Avance Global (%)"}))
        st.plotly_chart(fig, use_container_width=True)
        
    with col2:
        st.subheader("📊 Aportes al Proyecto Total")
        c1, c2 = st.columns(2)
        
        # Mostramos el valor real (8% y 12%)
        c1.metric("Aporte Recaudos (Max 40%)", f"{aporte_recaudos_global:.1f}%")
        # Como el aporte máximo de recaudos global es 40%, normalizamos la barra dividiendo entre 40
        st.progress(min(aporte_recaudos_global / 40.0, 1.0))
        
        c2.metric("Aporte Ejecución (Max 60%)", f"{aporte_actividades_global:.1f}%")
        # Como el aporte máximo de ejecución global es 60%, normalizamos la barra dividiendo entre 60
        st.progress(min(aporte_actividades_global / 60.0, 1.0))

elif vista == "⚖️ Tomo Legal":
    st.subheader("⚖️ Detalle: Tomo Legal")
    st.dataframe(df_legal, use_container_width=True)
