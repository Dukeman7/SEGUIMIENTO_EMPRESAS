import streamlit as st
import pandas as pd
from datetime import datetime

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Control de Productividad", page_icon="🎛️", layout="wide")

SHEET_ID = "1GYEizLwSybQ9-ezFD1gPnSytQyaNF2DWiJrwKcR68V4"
SHEET_NAME = "TAREAS_D"

@st.cache_data(ttl=30)  # Bajamos el tiempo de caché a 30 seg para mayor dinamismo
def cargar_tareas():
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={SHEET_NAME}"
    df = pd.read_csv(url)
    
    # Nos quedamos con las primeras 4 columnas (A, B, C, D)
    df = df.iloc[:, :4]
    df.columns = ['Fecha', 'Estado', 'Descripcion', 'Observaciones']
    
    # Limpieza
    df = df.dropna(subset=['Fecha'])
    df['Fecha'] = pd.to_datetime(df['Fecha'], dayfirst=True, errors='coerce')
    
    # Estado Booleano Robusto
    df['Estado'] = df['Estado'].apply(lambda x: str(x).strip().lower() in ['true', '1', 't', 'yes', 'si', 'verdadero'])
    
    return df

df = cargar_tareas()

# --- DATES Y TIMESTAMPS ---
df['Fecha_Solo'] = df['Fecha'].dt.normalize()
hoy = pd.Timestamp(datetime.now().date())
inicio_mes = hoy.replace(day=1)

# --- CÁLCULO DE LAS 5 CIFRAS CLAVE ---
# 1. Cumplidas Hoy
cumplidas_hoy = len(df[(df['Fecha_Solo'] == hoy) & (df['Estado'] == True)])

# 2. Acumuladas Cumplidas en el Mes
cumplidas_mes = len(df[(df['Fecha_Solo'] >= inicio_mes) & (df['Fecha_Solo'] <= hoy) & (df['Estado'] == True)])

# 3. Acumuladas Cumplidas Histórico (Total)
cumplidas_historico = len(df[df['Estado'] == True])

# 4. Atrasadas (Programadas para antes de hoy y NO cumplidas) -> Alerta Roja
atrasadas = len(df[(df['Fecha_Solo'] < hoy) & (df['Estado'] == False)])

# 5. Pendientes Futuras (Programadas para HOY o DÍAS FUTUROS y NO cumplidas)
pendientes_futuras = len(df[(df['Fecha_Solo'] >= hoy) & (df['Estado'] == False)])

# --- INTERFAZ DEL DASHBOARD ---
st.title("🎛️ Centro de Control de Productividad - Búnker")
st.caption(f"Última sincronización: {datetime.now().strftime('%H:%M:%S')} | Hoja: TAREAS_D")

st.write("---")

# DASHBOARD DE 5 CIFRAS CLAVE
c1, c2, c3, c4, c5 = st.columns(5)

with c1:
    st.metric(label="✅ Cumplidas Hoy", value=cumplidas_hoy)

with c2:
    st.metric(label="📅 Cumplidas este Mes", value=cumplidas_mes)

with c3:
    st.metric(label="🏆 Total Histórico", value=cumplidas_historico)

with c4:
    # Si hay atrasadas, se resalta en la métrica
    st.metric(label="🚨 Atrasadas (Vencidas)", value=atrasadas, delta=-atrasadas if atrasadas > 0 else 0, delta_color="inverse")

with c5:
    st.metric(label="⏳ Pendientes (Por vencer)", value=pendientes_futuras)

st.write("---")

# SECCIÓN DE ACCIÓN OPERATIVA
col_izq, col_der = st.columns(2)

with col_izq:
    st.subheader("🚨 Radar de Tareas Atrasadas")
    df_atrasadas = df[(df['Fecha_Solo'] < hoy) & (df['Estado'] == False)].sort_values('Fecha')
    
    if not df_atrasadas.empty:
        vista_atrasadas = df_atrasadas.copy()
        vista_atrasadas['Fecha'] = vista_atrasadas['Fecha'].dt.strftime('%d/%m/%Y')
        st.dataframe(vista_atrasadas[['Fecha', 'Descripcion', 'Observaciones']], use_container_width=True, hide_index=True)
    else:
        st.success("¡Sin tareas atrasadas! Cero pendientes del pasado.")

with col_der:
    st.subheader("📌 Tareas Programadas para Hoy")
    df_hoy = df[df['Fecha_Solo'] == hoy].sort_values('Estado')
    
    if not df_hoy.empty:
        vista_hoy = df_hoy.copy()
        vista_hoy['Estado_Icono'] = vista_hoy['Estado'].apply(lambda x: "✅ Listo" if x else "⏳ Pendiente")
        st.dataframe(vista_hoy[['Estado_Icono', 'Descripcion', 'Observaciones']], use_container_width=True, hide_index=True)
    else:
        st.info("No hay tareas específicas programadas para el día de hoy.")

# HISTORIAL COMPLETO
with st.expander("📋 Ver registro general de la hoja"):
    df_mostrar = df.copy()
    df_mostrar['Fecha'] = df_mostrar['Fecha'].dt.strftime('%d/%m/%Y')
    st.dataframe(df_mostrar[['Fecha', 'Estado', 'Descripcion', 'Observaciones']], use_container_width=True, hide_index=True)
