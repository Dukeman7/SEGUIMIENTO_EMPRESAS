import streamlit as st
import pandas as pd
from datetime import datetime

# Configuración del Búnker
st.set_page_config(page_title="Tablero de Operaciones - DANIEL", page_icon="🎯", layout="wide")
st.title("🎯 Tablero de Operaciones Tácticas: SIGESTEL & Proyectos")
st.markdown("### Asignado a: **Daniel** | Supervisión: **Luis (Director Técnico)**")
st.markdown("---")

# Inicializar los datos en el estado de la sesión si no existen
if 'datos_proyectos' not in st.session_state:
    st.session_state.datos_proyectos = pd.DataFrame({
        "Prioridad": ["🔴 ROJO (HOY)", "🔴 ROJO (HOY)", "🟠 NARANJA (2-3 Días)", "🟠 NARANJA (2-3 Días)", "🟢 VERDE (Próxima Semana)", "🟢 VERDE (Próxima Semana)"],
        "Proyecto": ["AyR NETWORK", "INFINET", "OPTIMUS", "FOURCOM", "PROTELECOM", "DATANET"],
        "Acción Requerida (Daniel)": [
            "Corregir ruta y ajustar económico urgente",
            "Subir económico (Luisito sube Técnico/Legal)",
            "Subir económico sin actualizar",
            "Liquidar el 10% restante e imprimir",
            "Hacer el económico tras recibir resumen de Luis",
            "Actualización económico/legal"
        ],
        "Deadline": ["2026-03-25", "2026-03-23", "2026-03-23", "2026-03-27", "2026-04-03", "2026-04-15"],
        "Estado": ["Pendiente", "Pendiente", "Pendiente", "Pendiente", "En Espera (Lado LD)", "Pendiente"]
    })

# Función para aplicar colores según la prioridad
def colorear_filas(val):
    color = ''
    if 'ROJO' in val:
        color = 'background-color: #ffcccc; color: #990000; font-weight: bold'
    elif 'NARANJA' in val:
        color = 'background-color: #ffe6cc; color: #cc6600; font-weight: bold'
    elif 'VERDE' in val:
        color = 'background-color: #e6f2ff; color: #004c99; font-weight: bold'
    return color

# Interfaz de edición
st.subheader("📋 Panel de Control de Tareas")
st.markdown("*Instrucción: Actualiza la columna 'Estado' al avanzar. Las fechas límite son inamovibles sin autorización.*")

# Mostrar el dataframe editable
df_editado = st.data_editor(
    st.session_state.datos_proyectos,
    column_config={
        "Estado": st.column_config.SelectboxColumn(
            "Estado de la Tarea",
            help="Actualiza tu progreso",
            options=["Pendiente", "Trabajando", "En Espera (Lado LD)", "Para Revisión LD", "COMPLETADO"],
            required=True
        ),
        "Prioridad": st.column_config.Column(disabled=True), # Daniel no puede cambiar la prioridad
        "Proyecto": st.column_config.Column(disabled=True),  # Daniel no puede cambiar el proyecto
        "Deadline": st.column_config.Column(disabled=True)   # Daniel no puede cambiar la fecha límite
    },
    hide_index=True,
    use_container_width=True
)

# Guardar cambios
if st.button("💾 Guardar Actualización de Estatus"):
    st.session_state.datos_proyectos = df_editado
    st.success("¡Estatus actualizado y reportado a la Dirección Técnica!")

# Mostrar tabla estilizada de solo lectura (Vista de Gerencia)
st.markdown("---")
st.subheader("👁️ Vista de Auditoría (Solo Lectura)")
st.dataframe(st.session_state.datos_proyectos.style.map(colorear_filas, subset=['Prioridad']), use_container_width=True)
