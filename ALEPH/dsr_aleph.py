import streamlit as st
import plotly.graph_objects as go

# Configuración de Marca
st.image("URL_LOGO_EMPRESA", width=150)
st.title("Sistema ALEPH: Control de Obligaciones")

# Simulación de Datos (esto vendrá de tu Google Sheet)
cumplimiento_actual = 70.0 # Valor validado por ti

# 1. El Relojito (Plotly Gauge)
fig = go.Figure(go.Indicator(
    mode = "gauge+number",
    value = cumplimiento_actual,
    title = {'text': "Estado de Cumplimiento"},
    gauge = {
        'axis': {'range': [0, 100]},
        'bar': {'color': "black"},
        'steps': [
            {'range': [0, 43], 'color': "red"},
            {'range': [43, 73], 'color': "yellow"},
            {'range': [73, 100], 'color': "green"}
        ],
        'threshold': {
            'line': {'color': "black", 'width': 4},
            'thickness': 0.75,
            'value': cumplimiento_actual}
    }
))
st.plotly_chart(fig)

# 2. Puntos Prioritarios (Interacción Cliente)
st.subheader("🎯 Prioridades del Mes")
p1 = st.checkbox("Punto 1: Actualización de RIF")
if p1:
    st.info("Simulación: Al validar este punto, su cumplimiento llegaría al 75%")
    # Aquí iría la función para enviarte el aviso

# 3. Reportes Mensuales (Tachado)
st.subheader("📋 Reportes Obligatorios")
reportes = ["Precios Efectivos", "Reclamos", "Despliegue", "Reunión de Seguimiento"]
for rep in reportes:
    if st.checkbox(rep):
        st.markdown(f"~~{rep}~~ ✅")
        # Disparar alerta de revisión
