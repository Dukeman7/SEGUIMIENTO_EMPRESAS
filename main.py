import dash
from dash import dcc, html, dash_table, Input, Output
import pandas as pd
import plotly.graph_objects as go
import os

# 1. Creando la APP 
# Se usa __name__ (con doble guion bajo al principio y al final)
app = dash.Dash(__name__)

# 2. SERVER (Ahora sí sabe qué es 'app')
server = app.server

# 1. CARGA DE DATOS
# El sistema lee el archivo que estás creando ahora mismo
def cargar_datos():
    try:
        df_cargado = pd.read_csv('data.csv')
        # Limpieza básica de espacios
        df_cargado.columns = df_cargado.columns.str.strip()
        return df_cargado
    except Exception as e:
        print(f"Error al cargar data.csv: {e}")
        # Data de respaldo por si el archivo falla
        return pd.DataFrame({
            'id': [0], 'cliente': ['ERROR'], 'obligacion': ['Archivo data.csv no detectado'],
            'peso': [0], 'responsable': ['Duque'], 'estatus': ['NO'], 'vencimiento': ['N/A']
        })

app = dash.Dash(__name__)

# 2. DISEÑO DE LA INTERFAZ (ALTO CONTRASTE)
app.layout = html.Div(style={'backgroundColor': '#000000', 'color': '#FFFFFF', 'minHeight': '100vh', 'padding': '20px'}, children=[
    
    html.H1("RADNET COMPLIANCE v2.0-ALPHA", 
            style={'textAlign': 'center', 'color': '#00D4FF', 'fontSize': '45px', 'marginBottom': '30px'}),

    # Selector de Cliente (Gigante)
    html.Div([
        html.Label("SELECCIONE CLIENTE:", style={'fontSize': '28px', 'fontWeight': 'bold', 'color': '#FFCC00'}),
        dcc.Dropdown(
            id='sel-cliente',
            options=[], # Se llena en el callback
            style={'backgroundColor': '#FFF', 'color': '#000', 'fontSize': '22px'}
        )
    ], style={'width': '60%', 'margin': 'auto', 'marginBottom': '40px'}),

    # Velocímetro Plotly
    dcc.Graph(id='gauge-chart', style={'height': '500px'}),

    # Tabla de Obligaciones
    html.Div([
        html.H2("MATRIZ DE SEGUIMIENTO", style={'color': '#00D4FF', 'borderBottom': '2px solid #00D4FF'}),
        dash_table.DataTable(
            id='tabla-obligaciones',
            columns=[
                {"name": "ID", "id": "id"},
                {"name": "OBLIGACIÓN", "id": "obligacion"},
                {"name": "RESPONSABLE", "id": "responsable"},
                {"name": "ESTATUS", "id": "estatus"},
                {"name": "VENCIMIENTO", "id": "vencimiento"}
            ],
            style_header={
                'backgroundColor': '#1A1A1A',
                'color': '#00D4FF',
                'fontSize': '20px',
                'fontWeight': 'bold',
                'border': '1px solid #444'
            },
            style_cell={
                'backgroundColor': '#000000',
                'color': '#FFFFFF',
                'textAlign': 'left',
                'fontSize': '18px',
                'padding': '15px',
                'border': '1px solid #333'
            },
            # Condicional para resaltar al CLIENTE en NARANJA
            style_data_conditional=[
                {
                    'if': {'column_id': 'responsable', 'filter_query': '{responsable} eq "Cliente"'},
                    'color': '#FF8C00',
                    'fontWeight': 'bold'
                },
                {
                    'if': {'column_id': 'estatus', 'filter_query': '{estatus} eq "NO"'},
                    'backgroundColor': '#2A0000' # Fondo rojizo oscuro para pendientes
                }
            ]
        )
    ], style={'padding': '20px'})
])

# 3. LÓGICA DE CÁLCULO Y ACTUALIZACIÓN
@app.callback(
    [Output('sel-cliente', 'options'),
     Output('sel-cliente', 'value'),
     Output('gauge-chart', 'figure'),
     Output('tabla-obligaciones', 'data')],
    [Input('sel-cliente', 'value')]
)
def update_dashboard(cliente_seleccionado):
    df = cargar_datos()
    opciones = [{'label': i, 'value': i} for i in df['cliente'].unique()]
    
    if not cliente_seleccionado:
        cliente_seleccionado = df['cliente'].unique()[0]

    dff = df[df['cliente'] == cliente_seleccionado]
    
    # CÁLCULO DEL 100% DINÁMICO (Lógica Duque: 94% + 6% reserva)
    peso_total = dff['peso'].sum()
    peso_cumplido = dff[dff['estatus'].str.upper() == 'SI']['peso'].sum()
    
    if peso_total > 0:
        cumplimiento_base = (peso_cumplido / peso_total) * 94
        porcentaje_final = cumplimiento_base + 6
    else:
        porcentaje_final = 6 # Solo la reserva si no hay tareas

    # Configuración del Gauge Chart
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = porcentaje_final,
        number = {'suffix': "%", 'font': {'size': 80}},
        title = {'text': f"SALUD REGULATORIA: {cliente_seleccionado}", 'font': {'size': 32, 'color': '#00D4FF'}},
        gauge = {
            'axis': {'range': [0, 100], 'tickwidth': 2, 'tickcolor': "white"},
            'bar': {'color': "#00D4FF"},
            'bgcolor': "#111",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, 50], 'color': "#800000"},   # Peligro (Rojo oscuro)
                {'range': [50, 85], 'color': "#B8860B"}, # Alerta (Dorado)
                {'range': [85, 100], 'color': "#006400"} # Seguro (Verde oscuro)
            ],
            'threshold': {
                'line': {'color': "white", 'width': 4},
                'thickness': 0.75,
                'value': 94
            }
        }
    ))
    
    fig.update_layout(paper_bgcolor='#000000', plot_bgcolor='#000000', font={'color': "white", 'family': "Arial"})

    return opciones, cliente_seleccionado, fig, dff.to_dict('records')

if __name__ == '__main__':
    # Para la nube, host debe ser 0.0.0.0 y debug debe ser False
    app.run(host='0.0.0.0', port=8080, debug=False)
