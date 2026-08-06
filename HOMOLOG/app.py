import streamlit as st
import pandas as pd

st.set_page_config(page_title="Radar CONATEL", page_icon="📡", layout="wide")

st.title("📡 Buscador y Radar de Homologaciones CONATEL")
st.markdown("---")

# Cargar datos desde el CSV del repositorio
@st.cache_data
def load_data():
    return pd.read_csv("Homologaciones_CONATEL_Total.csv")

df = load_data()

# Filtros laterales
st.sidebar.header("🔍 Filtros de Búsqueda")
marca = st.sidebar.multiselect("Selecciona Marca(s):", options=df["Marca"].unique())
buscar_modelo = st.sidebar.text_input("Buscar por Modelo o Certificado:")

# Aplicar filtros
df_filtrado = df.copy()
if marca:
    df_filtrado = df_filtrado[df_filtrado["Marca"].isin(marca)]
if buscar_modelo:
    df_filtrado = df_filtrado[df_filtrado["Modelo"].str.contains(buscar_modelo, case=False, na=False) | 
                              df_filtrado["C. Homologación"].str.contains(buscar_modelo, case=False, na=False)]

# Mostrar métricas y tabla
col1, col2 = st.columns(2)
col1.metric("Equipos Encontrados", len(df_filtrado))
col2.metric("Total Base de Datos", len(df))

st.dataframe(df_filtrado, use_container_width=True)

# Botón de descarga
st.download_button(
    label="📥 Descargar esta selección en CSV",
    data=df_filtrado.to_csv(index=False).encode('utf-8'),
    file_name="reporte_homologacion_filtrado.csv",
    mime="text/csv"
)
