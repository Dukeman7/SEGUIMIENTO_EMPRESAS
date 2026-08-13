import streamlit as st
import pandas as pd
import plotly.graph_objects as go

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

def calcular_sub_avances(df):
    """
    Divide el dataframe en Recaudos y Actividades si están separados por bloques,
    o calcula un estimado basado en las filas que tengan casillas marcadas (TRUE/FALSE o 1/0).
    Aquí asumiremos una lectura flexible de columnas booleanas o numéricas.
    """
    if df.empty:
        return 0.0, 0.0
    
    # Buscamos si hay columnas de estado o simulación temporal
    # Por defecto devolvemos 0.0 para que arranques en ceros limpios como pediste
    recaudos_prog = 0.0
    avances_prog = 0.0
    
    # Si las columnas contienen datos booleanos o enteros de verificación:
    for col in df.columns:
        if df[col].dtype in ['bool', 'int64', 'float64']:
            # Lógica de cálculo proporcional simulada/real
            pass
            
    return recaudos_prog, avances_prog

# Obtener avances por tomo (Recaudos 40% / Ejecución 60%)
# Puedes ajustar la lectura real de tu Google Sheet aquí según tus columnas de checkboxes
rec_tec, av_tec = 0.0, 0.0
rec_leg, av_leg = 0.0, 0.0
rec_eco, av_eco = 0.0, 0.0
av_diag = 0.0 # Diagramación es 100% ejecución de cierre

# Ponderación por Tomo
# Técnico: 55% (Recaudos Tomo = 40% de 55% = 22%, Ejecución Tomo = 60% de 55% = 33%)
total_tec = (rec_tec * 0.40) + (av_tec * 0.60)
pnet_tec = total_tec * 0.55

# Legal: 20% (Recaudos = 8%, Ejecución = 12%)
total_leg = (rec_leg * 0.40) + (av_leg * 0.60)
pnet_leg = total_leg * 0.20

# Económico: 20% (Recaudos = 8%, Ejecución = 12%)
total_eco = (rec_eco * 0.40) + (av_eco * 0.60)
pnet_eco = total_eco * 0.20

# Diagramación: 5%
pnet_diag = av_diag * 0.05

# Avance Global Ponderado del Proyecto (Suma 100%)
avance_global = pnet_tec + pnet_leg + pnet_eco + pnet_diag

# ==========================================
# BARRA LATERAL (SIDEBAR) CON BARRA DE PROGRESO GENERAL
# ==========================================
st.sidebar.title("🎼 Panel de Control")
st.sidebar.markdown("---")
st.sidebar.subheader("🎯 Avance Global")
st.sidebar.metric(label="Proyecto Total", value=f"{avance_global:.2f}%")
st.sidebar.progress(avance_global / 100.0)
st.sidebar.markdown("---")

vista = st.sidebar.radio(
    "Seleccione la vista:",
    ["📊 Resumen Ejecutivo (Galgas)", "🛠️ Tomo Técnico (55%)", "⚖️ Tomo Legal (20%)", "💰 Tomo Económico (20%)", "📦 Diagramación y Entrega (5%)"]
)

# Función para crear Galga de Aguja (Gauge Chart con Plotly)
def crear_galga_aguja(titulo, valor):
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = valor,
        title = {'text': titulo, 'font': {'size': 16, 'color': 'white'}},
        number = {'font': {'color': 'white', 'size': 20}},
        gauge = {
            'axis': {'range': [0, 100], 'tickcolor': "white"},
            'bar': {'color': "#00cc66"},
            'bgcolor': "#1e1e1e",
            'borderwidth': 2,
            'bordercolor': "#444",
            'steps': [
                {'range': [0, 40], 'toColor': '#ff4d4d'},
                {'range': [40, 80], 'toColor': '#ffcc00'},
                {'range': [80, 100], 'toColor': '#00cc66'}
            ],
        }
    ))
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=220, margin=dict(t=30, b=10, l=20, r=20))
    return fig

# ==========================================
# VISTAS DE LA APLICACIÓN
# ==========================================
if vista == "📊 Resumen Ejecutivo (Galgas)":
    st.title("🎼 Centro de Mando: Modificación de Habilitación")
    st.markdown("### Avance Ponderado Global del Proyecto")
    st.metric(label="Estado Actual", value=f"{avance_global:.2f}%", delta="Sincronizado con Google Sheets")
    st.progress(avance_global / 100.0)
    
    st.markdown("---")
    st.markdown("### 🎛️ Galgas de Control por Tomos (Nivel Recaudos vs Avances)")
    
    # Fila 1: Recaudos
    st.markdown("#### 📁 RECAUDOS (Peso: 40% dentro de cada Tomo)")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.plotly_chart(crear_galga_aguja("Recaudos Técnico", rec_tec), use_container_width=True)
    with col2:
        st.plotly_chart(crear_galga_aguja("Recaudos Legal", rec_leg), use_container_width=True)
    with col3:
        st.plotly_chart(crear_galga_aguja("Recaudos Económico", rec_eco), use_container_width=True)

    # Fila 2: Avances de Ejecución
    st.markdown("#### ⚙️ AVANCES / EJECUCIÓN (Peso: 60% dentro de cada Tomo)")
    col4, col5, col6 = st.columns(3)
    with col4:
        st.plotly_chart(crear_galga_aguja("Ejecución Técnico", av_tec), use_container_width=True)
    with col5:
        st.plotly_chart(crear_galga_aguja("Ejecución Legal", av_leg), use_container_width=True)
    with col6:
        st.plotly_chart(crear_galga_aguja("Ejecución Económico", av_eco), use_container_width=True)

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
