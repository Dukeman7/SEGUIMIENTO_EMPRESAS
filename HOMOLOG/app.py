import os
import streamlit as st
import pandas as pd

# 1. Configuración de página
st.set_page_config(
    page_title="Radar Homologaciones CONATEL v1.0",
    page_icon="📡",
    layout="wide"
)

st.title("📡 Radar de Equipos Homologados - CONATEL (v1.0)")
st.markdown("Herramienta de consulta y auditoría de homologaciones de telecomunicaciones.")
st.markdown("---")

# 2. Cargar el archivo manual (con manejo de errores por si cambia de nombre o ubicación)
@st.cache_data
def cargar_datos():
    # Intenta buscar el archivo CSV en la carpeta actual
    archivo = "homologaciones.csv"
    if not os.path.exists(archivo):
        return None
    
    # Leemos el archivo asegurando que los códigos se traten como texto
    df = pd.read_csv(archivo, dtype=str)
    return df

df = cargar_datos()

# 3. Validación de seguridad (Modo Gumersinda)
if df is None:
    st.error("⚠️ No se encontró el archivo 'homologaciones.csv' en la carpeta. Súbelo al repositorio para activar el radar.")
    st.stop()

# 4. Barra lateral de filtros
st.sidebar.header("🔍 Filtros de Búsqueda")

# Filtro por Marca (ordenado alfabéticamente)
marcas_disponibles = sorted(df["Marca"].dropna().unique())
marcas_seleccionadas = st.sidebar.multiselect(
    "1. Filtrar por Marca(s):",
    options=marcas_disponibles,
    default=[]
)

# Filtro por texto libre (Modelo o Código de Homologación)
busqueda_libre = st.sidebar.text_input("2. Buscar Modelo o Código HET/EAT:")

# 5. Aplicar los filtros a la tabla
df_filtrado = df.copy()

if marcas_seleccionadas:
    df_filtrado = df_filtrado[df_filtrado["Marca"].isin(marcas_seleccionadas)]

if busqueda_libre:
    df_filtrado = df_filtrado[
        df_filtrado["Modelo"].str.contains(busqueda_libre, case=False, na=False) |
        df_filtrado["C. Homologación"].str.contains(busqueda_libre, case=False, na=False) |
        df_filtrado["Código"].str.contains(busqueda_libre, case=False, na=False)
    ]

# 6. Mostrar métricas de control
col1, col2, col3 = st.columns(3)
col1.metric("Equipos en Pantalla", f"{len(df_filtrado):,}")
col2.metric("Total en Base de Datos", f"{len(df):,}")
col3.metric("Marcas Únicas", f"{df['Marca'].nunique():,}")

st.markdown("### 📋 Resultados de la Consulta")
st.dataframe(df_filtrado, use_container_width=True, hide_index=True)

# 7. Botón de exportación limpia
st.markdown("---")
csv_descarga = df_filtrado.to_csv(index=False).encode("utf-8")
st.download_button(
    label="📥 Descargar esta selección en CSV",
    data=csv_descarga,
    file_name="consulta_homologacion_filtrada.csv",
    mime="text/csv"
)
