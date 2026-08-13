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

# Leer hojas
df_legal = cargar_sheet("LEGAL")
df_econ = cargar_sheet("ECONOMICO")
df_tec = cargar_sheet("TECNICO")
df_diag = cargar_sheet("DIAGRAMACION")

# --- EXTRACCIÓN DE LOS 6 INDICADORES ---
# Basado en tu estructura donde los valores están en E4:F6 (aprox)
# Vamos a extraer los valores crudos de tu tabla resumen
try:
    # Definimos una función para limpiar y convertir a float
    def get_val(r, c): return float(str(df_diag.iloc[r, c]).replace('%',''))

    # Mapeo: [Tomo][Recaudos, Actividades]
    # Legal (Fila 3), Económico (Fila 4), Técnico (Fila 5) - Ajusta según tu D1:H6
    datos = {
        "⚖️ Legal": [get_val(2, 1), get_val(2, 2)],
        "💰 Económico": [get_val(3, 1), get_val(3, 2)],
        "🛠️ Técnico": [get_val(4, 1), get_val(4, 2)]
    }
    avance_global = get_val(5, 4) # H6
except:
    datos = {"⚖️ Legal": [0,0], "💰 Económico": [0,0], "🛠️ Técnico": [0,0]}
    avance_global = 0.0

# Sidebar
st.sidebar.title("🎼 Panel de Control")
vista = st.sidebar.radio("Seleccione la vista:", ["📊 Resumen Ejecutivo", "⚖️ Tomo Legal", "💰 Tomo Económico", "🛠️ Tomo Técnico", "📦 Diagramación"])

if vista == "📊 Resumen Ejecutivo":
    st.title("🎼 Centro de Mando: Modificación de Habilitación")
    
    col_a, col_b = st.columns([1, 2])
    with col_a:
        fig = go.Figure(go.Indicator(mode="gauge+number", value=avance_global, 
                                     gauge={'axis': {'range': [0, 100]}, 'bar': {'color': "#00cc66"}},
                                     title={'text': "Avance Global (%)"}))
        st.plotly_chart(fig, use_container_width=True)
        
    with col_b:
        st.subheader("📊 Aportes por Tomo al Proyecto")
        
        # Generar las 3 columnas para los tomos
        cols = st.columns(3)
        for i, (nombre, valores) in enumerate(datos.items()):
            with cols[i]:
                st.markdown(f"### {nombre}")
                st.metric("Recaudos", f"{valores[0]:.1f}%")
                st.progress(min(valores[0] / 40.0, 1.0)) # Normalizado
                st.metric("Actividades", f"{valores[1]:.1f}%")
                st.progress(min(valores[1] / 60.0, 1.0)) # Normalizado

elif vista in ["⚖️ Tomo Legal", "💰 Tomo Económico", "🛠️ Tomo Técnico"]:
    st.subheader(f"Detalle: {vista}")
    if "Legal" in vista: st.dataframe(df_legal, use_container_width=True)
    elif "Económico" in vista: st.dataframe(df_econ, use_container_width=True)
    else: st.dataframe(df_tec, use_container_width=True)
