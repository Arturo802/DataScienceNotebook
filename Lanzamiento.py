from dash import Dash, dcc, html, Input, Output
import pandas as pd
import plotly.express as px

# Cargar el archivo CSV con los datos de lanzamientos de SpaceX
spacex_df = pd.read_csv("spacex_launch_dash.csv")

# Obtener nombres únicos de sitios de lanzamiento
launch_sites = spacex_df['Launch Site'].unique()

# Crear opciones del menú desplegable
dropdown_options = [{'label': 'All Sites', 'value': 'ALL'}] + [
    {'label': site, 'value': site} for site in launch_sites
]

# Definir valores mínimos y máximos de carga útil
min_payload = spacex_df['Payload Mass (kg)'].min()
max_payload = spacex_df['Payload Mass (kg)'].max()

# Inicializar la aplicación Dash
app = Dash(__name__)

# Definir el layout de la aplicación
app.layout = html.Div([
    html.H1("SpaceX Launch Dashboard", style={'textAlign': 'center'}),

    # Menú desplegable para sitios de lanzamiento
    dcc.Dropdown(
        id='site-dropdown',
        options=dropdown_options,
        value='ALL',  # Selección predeterminada
        placeholder="Select a Launch Site here",
        searchable=True
    ),

    # Gráfico de pastel
    html.Div(dcc.Graph(id='success-pie-chart')),

    # Control deslizante de rango para carga útil
    dcc.RangeSlider(
        id='payload-slider',
        min=0,
        max=10000,
        step=1000,
        value=[min_payload, max_payload],  # Rango seleccionado inicialmente
        marks={0: '0 kg', 2500: '2500 kg', 5000: '5000 kg', 7500: '7500 kg', 10000: '10000 kg'}
    ),

    # Gráfico de dispersión
    html.Div(dcc.Graph(id='success-payload-scatter-chart'))
])

# Callback para actualizar el gráfico de pastel basado en el sitio seleccionado
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value')
)
def get_pie_chart(entered_site):
    if entered_site == 'ALL':
        # Agrupar por sitio de lanzamiento y contar lanzamientos exitosos (class=1)
        pie_data = spacex_df[spacex_df['class'] == 1].groupby('Launch Site').size().reset_index(name='count')
        
        fig = px.pie(
            pie_data, values='count',
            names='Launch Site',
            title='Porcentaje de lanzamientos exitosos por sitio'
        )
    else:
        # Filtrar por sitio de lanzamiento y contar éxitos y fallos
        filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]
        pie_data = filtered_df.groupby('class').size().reset_index(name='count')

        fig = px.pie(
            pie_data, values='count',
            names='class',
            title=f'Resultados de lanzamientos en {entered_site}'
        )

    return fig

# Callback para actualizar el gráfico de dispersión basado en el sitio y el rango de carga útil
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value'),
     Input(component_id='payload-slider', component_property='value')]
)
def get_scatter_chart(entered_site, payload_range):
    # Filtrar los datos según el rango de carga útil
    filtered_df = spacex_df[(spacex_df['Payload Mass (kg)'] >= payload_range[0]) & 
                             (spacex_df['Payload Mass (kg)'] <= payload_range[1])]

    if entered_site == 'ALL':
        # Graficar todos los lanzamientos, con el color según la versión del cohete
        fig = px.scatter(
            filtered_df, x="Payload Mass (kg)", y="class",
            color="Booster Version Category",
            title="Relación entre carga útil y éxito de lanzamientos (Todos los sitios)"
        )
    else:
        # Filtrar los datos por el sitio de lanzamiento seleccionado
        filtered_df = filtered_df[filtered_df['Launch Site'] == entered_site]
        # Graficar los lanzamientos del sitio seleccionado
        fig = px.scatter(
            filtered_df, x="Payload Mass (kg)", y="class",
            color="Booster Version Category",
            title=f"Relación entre carga útil y éxito en {entered_site}"
        )

    return fig

# Ejecutar la aplicación
if __name__ == '__main__':
    app.run()
