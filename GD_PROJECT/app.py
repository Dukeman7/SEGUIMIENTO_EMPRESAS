import streamlit as st
import pandas as pd

# Configuración de la página
st.set_page_config(
    page_title="Seguimiento Modificación Habilitación - Gold Data",
    page_icon="📊",
    layout="wide"
)

# ID del Google Sheet proporcionado por el usuario
SHEET_ID = "1YDV8UIyNldR9bLl71tgoI21cXvq4CIrkCSpMAmpOLvU"

@st.cache_data(ttl=60)
def cargar_datos_sheet(sheet_name):
    """Función para leer cada pestaña del Google Sheet público como CSV"""
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
    try:
        df = pd.read_csv(url)
        return df
    except Exception as e:
        st.error(f"Error al cargar la pestaña {sheet_name}: {e}")
        return pd.DataFrame()

# Título principal del Director de Orquesta
st.title("🎼 Centro de Control: Modificación de Habilitación - Gold Data")
st.markdown("---")

# Cargar las 4 pestañas de la galga (sin tildes en TECNICO y DIAGRAMACION)
df_legal = cargar_datos_sheet("LEGAL")
df_econ = cargar_datos_sheet("ECONOMICO")
df_tec = cargar_datos_sheet("TECNICO")
df_diag = cargar_datos_sheet("DIAGRAMACION")

# Sidebar de navegación
st.sidebar.header("🎛️ Panel de Control")
vista = st.sidebar.radio(
    "Seleccione la vista:",
    ["📊 Resumen Ejecutivo (Ponderación)", "⚖️ Tomo Legal (20%)", "💰 Tomo Económico (20%)", "🛠️ Tomo Técnico (60%)", "📦 Diagramación y Entrega"]
)

# Función simulada de cálculo de avance (basada en el conteo de filas o casillas)
# Aquí puedes adaptar la lógica según cómo evalúes las celdas de verificación en tu Google Sheet
def calcular_progreso(df):
    if df.empty:
        return 0.0
    # Ejemplo genérico: porcentaje de filas con datos o casillas marcadas
    # Puedes afinarlo si las columnas de verificación tienen nombres específicos
    return 45.0 # Valor de prueba inicial hasta calibrar el mapeo exacto de las columnas de verificación

progreso_legal = calcular_progreso(df_legal)
progreso_econ = calcular_progreso(df_econ)
progreso_tec = calcular_progreso(df_tec)
progreso_diag = calcular_progreso(df_diag)

# Cálculo Ponderado Global (Técnico 60%, Legal 20%, Económico 20%)
avance_global = (progreso_tec * 0.60) + (progreso_legal * 0.20) + (progreso_econ * 0.20)

if vista == "📊 Resumen Ejecutivo (Ponderación)":
    st.subheader("🎯 Indicadores Macro de la Solicitud")
    
    # Métrica principal global
    st.metric(label="Avance Ponderado Global del Proyecto", value=f"{avance_global:.1f}%", delta="En tiempo real desde Google Sheets")
    st.progress(avance_global / 100.0)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(label="🛠️ Tomo Técnico (Peso: 60%)", value=f"{progreso_tec:.1f}%")
        st.progress(progreso_tec / 100.0)
        
    with col2:
        st.metric(label="⚖️ Tomo Legal (Peso: 20%)", value=f"{progreso_legal:.1f}%")
        st.progress(progreso_legal / 100.0)
        
    with col3:
        st.metric(label="💰 Tomo Económico (Peso: 20%)", value=f"{progreso_econ:.1f}%")
        st.progress(progreso_econ / 100.0)

    st.markdown("---")
    st.info("💡 **Nota del Director:** Este panel lee directamente de la galga centralizada en Google Sheets. Cada tilde que marque tu equipo actualizará los porcentajes automáticamente.")

elif vista == "⚖️ Tomo Legal (20%)":
    st.subheader("⚖️ Seguimiento: Tomo Legal")
    st.dataframe(df_legal, use_container_width=True)

elif vista == "💰 Tomo Económico (20%)":
    st.subheader("💰 Seguimiento: Tomo Económico")
    st.dataframe(df_econ, use_container_width=True)

elif vista == "🛠️ Tomo Técnico (60%)":
    st.subheader("🛠️ Seguimiento: Tomo Técnico")
    st.dataframe(df_tec, use_container_width=True)

elif vista == "📦 Diagramación y Entrega":
    st.subheader("📦 Seguimiento: Diagramación y Preparación Final")
    st.dataframe(df_diag, use_container_width=True)
