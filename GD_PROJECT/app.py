import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Configuración de la página
st.set_page_config(page_title="Gold Data - Centro de Control", layout="wide")

SHEET_ID = "1YDV8UIyNldR9bLl71tgoI21cXvq4CIrkCSpMAmpOLvU"

@st.cache_data(ttl=30)
def cargar_sheet(sheet_name):
    # Usamos headers=0 para que lea las filas desde el inicio (A1)
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={sheet_name}&headers=0"
    return pd.read_csv(url, header=None)

# Cargar hojas
df_legal = cargar_sheet("LEGAL")
df_econ = cargar_sheet("ECONOMICO")
df_tec = cargar_sheet("TECNICO")
df_ctrl = cargar_sheet("CONTROL")

# --- EXTRACCIÓN DE DATOS DESDE LA PESTAÑA CONTROL ---
def get_val(r, c):
    """Extrae el valor de df_ctrl, limpia comas y convierte a float."""
    try:
        val = df_ctrl.iloc[r, c]
        if pd.isnull(val):
            return 0.0
        val_str = str(val).replace(',', '.').strip()
        return float(val_str)
    except:
        return 0.0

try:
    # Coordenadas exactas según tu imagen de la pestaña CONTROL:
    # Filas: Fila 2 (índice 1) = Recaudos, Fila 3 (índice 2) = Actividades
    # Columnas: B (Legal) = 1, C (Económico) = 2, D (Técnico) = 3
    # Avance Global: E6 -> Fila 6 (índice 5), Columna E (índice 4)
    
    datos = {
        "⚖️ Legal": [get_val(1, 1), get_val(2, 1)],         # B2, B3
        "💰 Económico": [get_val(1, 2), get_val(2, 2)],     # C2, C3
        "🛠️ Técnico": [get_val(1, 3), get_val(2, 3)]       # D2, D3
    }
    
    avance_global = get_val(5, 4) # E6
    
except Exception as e:
    datos = {"⚖️ Legal": [0.0, 0.0], "💰 Económico": [0.0, 0.0], "🛠️ Técnico": [0.0, 0.0]}
    avance_global = 0.0

# --- INTERFAZ ---
st.sidebar.title("🎼 Panel de Control")
vista = st.sidebar.radio("Seleccione la vista:", 
    ["📊 Resumen Ejecutivo", "⚖️ Tomo Legal", "💰 Tomo Económico", "🛠️ Tomo Técnico", "🎛️ Control (Tabla)"])

if vista == "📊 Resumen Ejecutivo":
    st.title("🎼 Centro de Mando: Modificación de Habilitación")
    
    col_a, col_b = st.columns([1, 2])
    
    with col_a:
        st.subheader("🎯 Avance Global")
        fig = go.Figure(go.Indicator(
            mode="gauge+number", 
            value=avance_global,
            number={'suffix': "%"},
            gauge={'axis': {'range': [0, 100]}, 'bar': {'color': "#00cc66"}},
            title={'text': "Proyecto Total"}
        ))
        st.plotly_chart(fig, use_container_width=True)
        
    with col_b:
        st.subheader("📊 Indicadores por Tomo")
        cols = st.columns(3)
        for i, (nombre, valores) in enumerate(datos.items()):
            with cols[i]:
                st.markdown(f"### {nombre}")
                st.metric("Recaudos", f"{valores[0]:.2f}%")
                st.progress(min(valores[0] / 100.0, 1.0))
                st.metric("Actividades", f"{valores[1]:.2f}%")
                st.progress(min(valores[1] / 100.0, 1.0))

elif vista == "⚖️ Tomo Legal":
    st.subheader("⚖️ Detalle: Tomo Legal")
    st.dataframe(df_legal, use_container_width=True)
elif vista == "💰 Tomo Económico":
    st.subheader("💰 Detalle: Tomo Económico")
    st.dataframe(df_econ, use_container_width=True)
elif vista == "🛠️ Tomo Técnico":
    st.subheader("🛠️ Detalle: Tomo Técnico")
    st.dataframe(df_tec, use_container_width=True)
elif vista == "🎛️ Control (Tabla)":
    st.subheader("🎛️ Detalle: Pestaña CONTROL")
    st.dataframe(df_ctrl, use_container_width=True)
