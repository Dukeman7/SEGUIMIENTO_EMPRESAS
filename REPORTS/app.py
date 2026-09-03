import streamlit as st
import pandas as pd
from datetime import datetime

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Control Mensual CONATEL", page_icon="📅", layout="centered")

SHEET_ID = "1GYEizLwSybQ9-ezFD1gPnSytQyaNF2DWiJrwKcR68V4"
SHEET_NAME = "REPORTES_MES"

@st.cache_data(ttl=15)
def cargar_control_mensual():
    url = f"https://docs.google.com/spreadsheets/d/1GYEizLwSybQ9-ezFD1gPnSytQyaNF2DWiJrwKcR68V4/gviz/tq?tqx=out:csv&sheet=REPORTES_MES"
    try:
        df = pd.read_csv(url)
        
        # Nos aseguramos de tomar las 5 columnas clave
        df = df.iloc[:, :5]
        df.columns = ['Empresa', 'Reporte', 'Remitieron', 'Enviado', 'Entregado']
        
        # Rellenamos el nombre de la empresa hacia abajo por si la celda está combinada
        df['Empresa'] = df['Empresa'].ffill()
        
        # Limpiamos filas vacías
        df = df.dropna(subset=['Reporte'])
        
        # Convertimos los estados a Booleanos
        for col in ['Remitieron', 'Enviado', 'Entregado']:
            df[col] = df[col].apply(lambda x: str(x).strip().lower() in ['true', '1', 't', 'yes', 'si', 'verdadero', 'x'])
            
        return df
    except Exception as e:
        st.error(f"⚠️ Error al conectar con Google Sheets: {e}")
        return pd.DataFrame()

df = cargar_control_mensual()

st.title("🚨 Control Cierre Mensual CONATEL")
st.caption("Seguimiento de entregas de los primeros 5 Días Hábiles")

if not df.empty:
    # MÉTRICAS GLOBALES POR REPORTE INDIVIDUAL
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

    # AGRUPACIÓN POR EMPRESA
    empresas = df['Empresa'].unique()

    for emp in empresas:
        sub_df = df[df['Empresa'] == emp]
        
        # Contamos cuántos reportes tiene esta empresa y cuántos ha completado
        tot_emp = len(sub_df)
        comp_emp = len(sub_df[sub_df['Entregado'] == True])
        
        listo = (comp_emp == tot_emp)
        icono = "✅" if listo else "⏳"
        
        with st.expander(f"{icono} {emp} ({comp_emp}/{tot_emp} Entregados)"):
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
else:
    st.warning("No se encontraron datos en la hoja de cálculo.")
