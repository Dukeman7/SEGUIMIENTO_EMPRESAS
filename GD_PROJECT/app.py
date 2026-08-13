import streamlit as st
import pandas as pd

# Configuración de la página
st.set_page_config(
    page_title="Seguimiento Modificación Habilitación - Gold Data",
    page_icon="🎼",
    layout="wide"
)

SHEET_ID = "1YDV8UIyNldR9bLl71tgoI21cXvq4CIrkCSpMAmpOLvU"

@st.cache_data(ttl=30)
def cargar_datos_sheet(sheet_name):
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
    try:
        return pd.read_csv(url)
    except Exception as e:
        return pd.DataFrame()

# Cargar pestañas
df_legal = cargar_datos_sheet("LEGAL")
df_econ = cargar_datos_sheet("ECONOMICO")
df_tec = cargar_datos_sheet("TECNICO")
df_diag = cargar_datos_sheet("DIAGRAMACION")

# Valores iniciales en 0.00%
rec_tec, av_tec = 0.0, 0.0
rec_leg, av_leg = 0.0, 0.0
rec_eco, av_eco = 0.0, 0.0
av_diag = 0.0

# Ponderación por Tomo (Técnico 55%, Legal 20%, Económico 20%, Diagramación 5%)
# Recaudos = 40% del Tomo | Ejecución = 60% del Tomo
total_tec = (rec_tec * 0.40) + (av_tec * 0.60)
pnet_tec = total_tec * 0.55

total_leg = (rec_leg * 0.40) + (av_leg * 0.60)
pnet_leg = total_leg * 0.20

total_eco = (rec_eco * 0.40) + (av_eco * 0.60)
pnet_eco = total_eco * 0.20

pnet_diag = av_diag * 0.05

# Avance Global Ponderado del Proyecto
avance_global = pnet_tec + pnet_leg + pnet_eco + pnet_diag

# ==========================================
# BARRA LATERAL (SIDEBAR)
# ==========================================
st.sidebar.title("🎼 Panel de Control")
st.sidebar.markdown("---")
st.sidebar.subheader("🎯 Avance Global")
st.sidebar.metric(label="Proyecto Total", value=f"{avance_global:.2f}%")
st.sidebar.progress(avance_global / 100.0)
st.sidebar.markdown("---")

vista = st.sidebar.radio(
    "Seleccione la vista:",
    ["📊 Resumen Ejecutivo", "🛠️ Tomo Técnico (55%)", "⚖️ Tomo Legal (20%)", "💰 Tomo Económico (20%)", "📦 Diagramación y Entrega (5%)"]
)

# ==========================================
# VISTAS DE LA APLICACIÓN
# ==========================================
if vista == "📊 Resumen Ejecutivo":
    st.title("🎼 Centro de Mando: Modificación de Habilitación")
    st.markdown("### Avance Ponderado Global del Proyecto")
    st.metric(label="Estado Actual", value=f"{avance_global:.2f}%", delta="Sincronizado con Google Sheets")
    st.progress(avance_global / 100.0)
    
    st.markdown("---")
    st.markdown("### 📁 RECAUDOS (Peso: 40% dentro de cada Tomo)")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Recaudos Técnico", f"{rec_tec:.2f}%")
        st.progress(rec_tec / 100.0)
    with col2:
        st.metric("Recaudos Legal", f"{rec_leg:.2f}%")
        st.progress(rec_leg / 100.0)
    with col3:
        st.metric("Recaudos Económico", f"{rec_eco:.2f}%")
        st.progress(rec_eco / 100.0)

    # Fila 2: Avances de Ejecución
    data_sections = st.markdown("---")
    st.markdown("### ⚙️ AVANCES / EJECUCIÓN (Peso: 60% dentro de cada Tomo)")
    col4, col5, col6 = st.columns(3)
    with col4:
        st.metric("Ejecución Técnico", f"{av_tec:.2f}%")
        st.progress(av_tec / 100.0)
    with col5:
        st.metric("Ejecución Legal", f"{av_leg:.2f}%")
        st.progress(av_leg / 100.0)
    with col6:
        st.metric("Ejecución Económico", f"{av_eco:.2f}%")
        st.progress(av_eco / 100.0)

elif vista == "🛠️ Tomo Técnico (55%)":
    st.subheader("🛠️ Detalle: Tomo Técnico (Peso Global: 55%)")
    st.markdown("*Desglose de Recaudos (40%) y Actividades Técnicas (60%)*")
    st.dataframe(df_tec, use_container_width=True)

elif vista == "⚖️ Tomo Legal (20%)":
    st.subheader("⚖️ Detalle: Tomo Legal (Peso Global: 20%)")
    st.markdown("*Desglose de Recaudos (40%) y Actividades Legales (60%)*")
    st.dataframe(df_legal, use_container_width=True)

elif vista == "💰 Tomo Económico (20%)":
    st.subheader("💰 Detalle: Tomo Económico (Peso Global: 20%)")
    st.markdown("*Desglose de Recaudos (40%) y Actividades Económicas (60%)*")
    st.dataframe(df_econ, use_container_width=True)

elif vista == "📦 Diagramación y Entrega (5%)":
    st.subheader("📦 Detalle: Diagramación y Cierre (Peso Global: 5%)")
    st.markdown("*Actividades finales de impresión, encuadernado y entrega ante CONATEL*")
    st.dataframe(df_diag, use_container_width=True)
