import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Configuración de la página
st.set_page_config(page_title="Gold Data - Centro de Control", layout="wide")

SHEET_ID = "1YDV8UIyNldR9bLl71tgoI21cXvq4CIrkCSpMAmpOLvU"

@st.cache_data(ttl=30)
def cargar_sheet(sheet_name):
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
    return pd.read_csv(url)

# Cargar hojas
df_legal = cargar_sheet("LEGAL")
df_econ = cargar_sheet("ECONOMICO")
df_tec = cargar_sheet("TECNICO")
df_diag = cargar_sheet("DIAGRAMACION")

# --- EXTRACCIÓN DE DATOS ---
def get_val(r, c):
    """Extrae el valor, reemplaza comas por puntos y convierte a float."""
    try:
        val = df_diag.iloc[r, c]
        if pd.isnull(val):
            return 0.0
        # Convertir a string, reemplazar coma por punto, limpiar espacios
        val_str = str(val).replace(',', '.').strip()
        return float(val_str)
    except:
        return 0.0

try:
    # Mapeo según tus coordenadas:
    # Legal: E2(1,4), E3(2,4) | Económico: F2(1,5), F3(2,5) | Técnico: G2(1,6), G3(2,6)
    # Global: H6 (Fila 6 -> índice 5, Columna H -> índice 7)
    datos = {
        "⚖️ Legal": [get_val(1, 4), get_val(2, 4)],
        "💰 Económico": [get_val(1, 5), get_val(2, 5)],
        "🛠️ Técnico": [get_val(1, 6), get_val(2, 6)]
    }
    avance_global = get_val(5, 7) 
except Exception as e:
    # Si algo falla aquí, los valores se quedan en 0 para no romper la app
    datos = {"⚖️ Legal": [0.0, 0.0], "💰 Económico": [0.0, 0.0], "🛠️ Técnico": [0.0, 0.0]}
    avance_global = 0.0

# --- INTERFAZ ---
st.sidebar.title("🎼 Panel de Control")
vista = st.sidebar.radio("Seleccione la vista:", 
    ["📊 Resumen Ejecutivo", "⚖️ Tomo Legal", "💰 Tomo Económico", "🛠️ Tomo Técnico", "📦 Diagramación"])

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
        st.subheader("📊 Aportes por Tomo")
        cols = st.columns(3)
        for i, (nombre, valores) in enumerate(datos.items()):
            with cols[i]:
                st.markdown(f"### {nombre}")
                # Recaudos
                st.metric("Recaudos", f"{valores[0]:.1f}%")
                st.progress(min(valores[0] / 100.0, 1.0))
                # Actividades
                st.metric("Actividades", f"{valores[1]:.1f}%")
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
elif vista == "📦 Diagramación":
    st.subheader("📦 Detalle: Resumen (D1:H6)")
    st.dataframe(df_diag, use_container_width=True)
