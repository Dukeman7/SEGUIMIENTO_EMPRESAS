import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Control Mensual CONATEL", page_icon="📅", layout="centered")

SHEET_ID = "https://docs.google.com/spreadsheets/d/1GYEizLwSybQ9-ezFD1gPnSytQyaNF2DWiJrwKcR68V4/edit?gid=966836474#gid=966836474"
SHEET_NAME = "REPORTES_MENSUALES"

@st.cache_data(ttl=15)
def cargar_control_mensual():
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={SHEET_NAME}"
    df = pd.read_csv(url)
    # Limpieza básica de datos
    df = df[['Empresa', 'Reporte', 'Remitieron', 'Enviado', 'Entregado']].dropna(subset=['Empresa'])
    for col in ['Remitieron', 'Enviado', 'Entregado']:
        df[col] = df[col].apply(lambda x: str(x).strip().lower() in ['true', '1', 't', 'yes', 'si', 'verdadero'])
    return df

st.title("🚨 Control Cierre Mensual CONATEL")
st.caption("Seguimiento de entregas - Primeros 5 Días Hábiles del Mes")

df = cargar_control_mensual()

# MÈTRICAS DE CUMPLIMIENTO GLOBAL
total_reportes = len(df)
completados = len(df[(df['Remitieron'] == True) & (df['Entregado'] == True)])
pct = (completados / total_reportes * 100) if total_reportes > 0 else 0

col1, col2 = st.columns(2)
with col1:
    st.metric("Total Entregados", f"{completados} / {total_reportes}")
with col2:
    st.metric("Cumplimiento Mes", f"{pct:.1f}%")

st.progress(pct / 100)
st.write("---")

# VISTA POR OPERADOR (FÁCIL LECTURA EN CELULAR)
empresas = df['Empresa'].unique()

for emp in empresas:
    sub_df = df[df['Empresa'] == emp]
    # Determinar si la empresa completó todo
    listo = all(sub_df['Entregado'])
    icono = "✅" if listo else "⏳"
    
    with st.expander(f"{icono} {emp}"):
        for idx, row in sub_df.iterrows():
            st.markdown(f"**📌 {row['Reporte']}**")
            c1, c2, c3 = st.columns(3)
            with c1:
                st.checkbox("Remitieron", value=row['Remitieron'], key=f"rem_{idx}", disabled=True)
            with c2:
                st.checkbox("Enviado 📧", value=row['Enviado'], key=f"env_{idx}", disabled=True)
            with c3:
                st.checkbox("Entregado 🏛️", value=row['Entregado'], key=f"ent_{idx}", disabled=True)
            st.write("---")
