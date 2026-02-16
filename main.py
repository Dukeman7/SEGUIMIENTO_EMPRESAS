import dash
from dash import dcc, html, dash_table, Input, Output
import pandas as pd
import plotly.graph_objects as go
import os

# 1. INICIALIZACIÓN ÚNICA (Orden jerárquico estricto)
app = dash.Dash(__name__)
server = app.server  # El servidor reconoce a la APP de inmediato

# 2. FUNCIÓN DE CARGA DE DATOS
def cargar_datos():
    try:
        if os.path.exists('data.csv'):
            df_cargado = pd.read_csv('data.csv')
            df_cargado.columns = df_cargado.columns.str.strip()
            return df_cargado
        else:
            raise FileNotFoundError
    except Exception as e:
        return pd.DataFrame({
            'id': [0], 'cliente': ['ESPERANDO DATA'], 'obligacion': ['Subir data.csv al repositorio'],
            'peso': [0], 'responsable': ['Sistema'], 'estatus': ['NO'], 'vencimiento': ['N/A']
        })

# 3. DISEÑO DE LA INTERFAZ (ALTO CONTRASTE PARA LA VISTA)
app.layout = html.Div(style={'backgroundColor': '#000000', 'color': '#FFFFFF', 'minHeight': '100vh', 'padding': '20px'}, children=[
    
    html.H1("RADNET COMPLIANCE v2.0-ALPHA", 
            style={'textAlign': 'center', 'color': '#00D4FF', 'fontSize': '45px', 'marginBottom': '30px'}),

    # Selector de Cliente
    html.Div([
        html.Label("SELECCIONE CLIENTE:", style={'fontSize': '28px', 'fontWeight': 'bold', 'color': '#FFCC00'}),
        dcc.Dropdown(
            id='sel-cliente',
            options=[], 
            style={'backgroundColor': '#FFF', 'color': '#000', 'fontSize': '22px'}
        )
    ], style={'width': '60%', 'margin': 'auto', 'marginBottom': '40px'}),

    # Velocímetro
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
            style_header={'backgroundColor': '#1A1A1A', 'color': '#00D4FF', 'fontSize': '20px', 'fontWeight': 'bold'},
            style_cell={'backgroundColor': '#000000', 'color': '#FFFFFF', 'textAlign': 'left', 'fontSize': '18px', 'padding': '15px'},
            style_data_conditional=[
                {
                    'if': {'column_id': 'responsable', 'filter_query': '{responsable} eq "Cliente"'},
                    'color': '#FF8C00', 'fontWeight': 'bold'
                },
                {
                    'if': {'column_id': 'estatus', 'filter_query': '{estatus} eq "NO"'},
                    'backgroundColor': '#2A0000'
                }
            ]
        )
    ], style={'padding': '20px'})
])

# 4. LÓGICA DE ACTUALIZACIÓN
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
    
    if not cliente_seleccionado and not df.empty:
        cliente_seleccionado = df['cliente'].unique()[0]

    dff = df[df['cliente'] == cliente_seleccionado]
    
    # Cálculo dinámico 94/6
    peso_total = dff['peso'].sum()
    peso_cumplido = dff[dff['estatus'].str.upper() == 'SI']['peso'].sum()
    
    porcentaje_final = ((peso_cumplido / peso_total * 94) + 6) if peso_total > 0 else 6

    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = porcentaje_final,
        number = {'suffix': "%", 'font': {'size': 80}},
        title = {'text': f"SALUD REGULATORIA: {cliente_seleccionado}", 'font': {'size': 32, 'color': '#00D4FF'}},
        gauge = {
            'axis': {'range': [0, 100], 'tickwidth': 2, 'tickcolor': "white"},
            'bar': {'color': "#00D4FF"},
            'bgcolor': "#111",
            'steps': [
                {'range': [0, 50], 'color': "#800000"},
                {'range': [50, 85], 'color': "#B8860B"},
                {'range': [85, 100], 'color': "#006400"}
            ],
            'threshold': {'line': {'color': "white", 'width': 4}, 'value': 94}
        }
    ))
    fig.update_layout(paper_bgcolor='#000000', font={'color': "white"})

    return opciones, cliente_seleccionado, fig, dff.to_dict('records')

# 5. LANZAMIENTO (Modo Nube)
if __name__ == '__main__':
    # Usamos el puerto que la nube nos asigne, o el 8050 por defecto
    port = int(os.environ.get("PORT", 8050))
    app.run(host='0.0.0.0', port=port, debug=False)
