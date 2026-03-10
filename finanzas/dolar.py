import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta
import requests
import io

# --- 1. COORDENADAS DEL HISTÓRICO ---
# ID de la hoja: Historico Dolar v2
SHEET_ID_FIN = "1qFoejGsS959tbrnWySx1eSl8D6WAHbYcR84h4cgDkHY"
URL_FINANZAS = f"https://docs.google.com/spreadsheets/d/{SHEET_ID_FIN}/export?format=csv&gid=1936830046"

st.set_page_config(page_title="Wellcomm: Monitor de Tesorería", layout="wide")

def load_financial_data():
    try:
        response = requests.get(URL_FINANZAS)
        # Limpieza de comas y puntos para asegurar lectura numérica
        raw_text = response.content.decode('utf-8').replace(',', '.')
        df = pd.read_csv(io.StringIO(raw_text))
        
        # Ajuste de nombres de columnas según tu hoja
        df.columns = df.columns.str.strip()
        
        # Convertimos 'Vigencia' a fecha y 'Tasa' a número
        df['Vigencia'] = pd.to_datetime(df['Vigencia'], dayfirst=True, errors='coerce')
        df['Tasa'] = pd.to_numeric(df['Tasa'], errors='coerce')
        
        return df.dropna(subset=['Vigencia', 'Tasa']).sort_values('Vigencia')
    except Exception as e:
        st.error(f"Error cargando el historial: {e}")
        return pd.DataFrame()

df_fin = load_financial_data()

# --- 2. CONTROLES DE NAVEGACIÓN (SIDEBAR) ---
with st.sidebar:
    st.header("🔭 Radar de Divisas")
    
    if not df_fin.empty:
        # Selector de Rango de Análisis
        min_date = df_fin['Vigencia'].min().to_pydatetime()
        max_date = df_fin['Vigencia'].max().to_pydatetime()
        
        f_inicio, f_fin = st.date_input(
            "Rango de Análisis Histórico:",
            value=(max_date - timedelta(days=30), max_date),
            min_value=min_date,
            max_value=max_date
        )
        
        st.divider()
        st.header("🔮 Oráculo (Predicción)")
        f_futura = st.date_input("Fecha a Proyectar:", value=datetime(2026, 3, 18))

# --- 3. LÓGICA DE CÁLCULO Y EXTRAPOLACIÓN ---
if not df_fin.empty:
    # Filtrado por rango seleccionado
    mask = (df_fin['Vigencia'] >= pd.to_datetime(f_inicio)) & (df_fin['Vigencia'] <= pd.to_datetime(f_fin))
    df_filtered = df_fin.loc[mask]
    
    promedio_rango = df_filtered['Tasa'].mean()
    ultima_tasa = df_fin['Tasa'].iloc[-1]
    
    # --- EXTRAPOLACIÓN (Basada en los últimos 30 días de data) ---
    df_recent = df_fin.tail(30)
    x = np.arange(len(df_recent))
    y = df_recent['Tasa'].values
    slope, intercept = np.polyfit(x, y, 1) # Regresión lineal simple
    
    # Calcular días desde el último registro hasta la fecha futura
    dias_al_futuro = (pd.to_datetime(f_futura) - df_fin['Vigencia'].max()).days
    tasa_proyectada = ultima_tasa + (slope * dias_al_futuro)

    # --- 4. PANEL DE CONTROL (KPIs) ---
    st.title("🛡️ Búnker Financiero Wellcomm")
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Tasa Promedio (Rango)", f"{promedio_rango:.4f} Bs/$")
    c2.metric("Última Tasa Oficial", f"{ultima_tasa:.4f} Bs/$", 
              delta=f"{((ultima_tasa/df_fin['Tasa'].iloc[-2])-1)*100:.2f}%")
    c3.metric(f"Predicción al {f_futura.strftime('%d-%b')}", f"{tasa_proyectada:.4f} Bs/$", 
              delta=f"{(tasa_proyectada - ultima_tasa):.2f} Bs", delta_color="inverse")

    # --- 5. GRÁFICO DE EVOLUCIÓN Y TENDENCIA ---
    fig = go.Figure()

    # Histórico Real
    fig.add_trace(go.Scatter(x=df_fin['Vigencia'], y=df_fin['Tasa'], 
                             name="Histórico BCV", line=dict(color='#00e5ff', width=3)))

    # Línea de Promedio en el rango
    fig.add_trace(go.Scatter(x=[f_inicio, f_fin], y=[promedio_rango, promedio_rango], 
                             name="Promedio Seleccionado", line=dict(color='yellow', dash='dash')))

    # Punto de Predicción
    fig.add_trace(go.Scatter(x=[df_fin['Vigencia'].max(), pd.to_datetime(f_futura)], 
                             y=[ultima_tasa, tasa_proyectada], 
                             name="Extrapolación", line=dict(color='#ff4081', dash='dot')))

    fig.update_layout(
        template="plotly_dark", 
        height=600, 
        xaxis_range=[pd.to_datetime(f_inicio) - timedelta(days=5), pd.to_datetime(f_futura) + timedelta(days=5)],
        title=f"Evolución Cambiaria y Proyección al {f_futura.strftime('%d/%m/%Y')}",
        hovermode="x unified"
    )
    st.plotly_chart(fig, use_container_width=True)

    # --- 6. IMPACTO EN WELLCOMM (SIMULACIÓN) ---
    st.divider()
    st.subheader("📊 Simulación de Recaudación (60% Activos)")
    usd_factura = 384560 # El 60% de los activos que calculamos antes
    bs_hoy = usd_factura * ultima_tasa
    bs_futuro = usd_factura * tasa_proyectada
    
    s1, s2 = st.columns(2)
    s1.write(f"**Recaudación hoy ({ultima_tasa:.2f}):** {bs_hoy:,.2f} Bs")
    s2.write(f"**Recaudación proyectada ({tasa_proyectada:.2f}):** {bs_futuro:,.2f} Bs")
    st.info(f"💡 El retraso en el cobro hasta el {f_futura.strftime('%d-%b')} representa un ajuste inflacionario de **{bs_futuro - bs_hoy:,.2f} Bs**.")

else:
    st.warning("⚠️ No se pudo conectar con el Histórico. Revisa el ID de la hoja.")
