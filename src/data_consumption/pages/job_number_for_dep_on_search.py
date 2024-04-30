import dash
from dash import dcc, html, callback
from dash.dependencies import Input, Output
from api_requests import get_departments, get_job_number_for_dep_on_search
import logging

# Page Nombre de jobs pour un département avec recherche par texte libre

# setup logger
log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
logging.basicConfig(format=log_format, level=logging.DEBUG)
logger = logging.getLogger(__name__)

dash.register_page(__name__, path= "/job-number-for-dep-on-search")

app = dash.get_app()

# Layout de la page
layout = html.Div([
    html.H2("Nombre de jobs pour un département avec recherche par texte libre"),
    html.Div([
        dcc.Dropdown(
            id="dropdown-department",
            options = [{'label': f"{dept['code']} - {dept['libelle']}", 
                        'value': dept['code']} for dept in get_departments()],
            value="75"  # Valeur par défaut : premier département
        )
    ]),
    html.Label('Texte de recherche'),
    dcc.Input(id='search-text', type='text', value=''),
    html.Button('Lancer la recherche', id='search-button', n_clicks=0),
    html.Div(id='resultat')
], style={'background': 'beige'})

# Mise à jour du résultat
@callback(
    Output('resultat', 'children'),
    [Input('search-button', 'n_clicks')],
    [Input('dropdown-department', 'value')],
    [Input('search-text', 'value')]
)
def update_result(n_clicks, selected_department, search_text):
    if n_clicks > 0:
        data = get_job_number_for_dep_on_search(selected_department, search_text)
        if data == None:
            logger.error("No data obtained")
            return dash.no_update
        
        return data