import dash
from dash import dcc, html, callback
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px
from api_requests import get_top_categories_for_dep
from departments_list import departments
import logging


# setup logger
log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
logging.basicConfig(format=log_format, level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Variable contenant le dernier JSON des données obtenues de l'API Rest
data = None

dash.register_page(__name__, path= "/top-categories-for-department")

app = dash.get_app()

# Page Top 5 des catégories d'emplois recrutant le plus par département
layout = html.Div([
    html.H1("Top 5 des catégories d'emplois recrutant le plus par département"),
    html.Div([
        dcc.Dropdown(
            id="dropdown-department",
            options=[{"label": f"{dept} - {dept_name}", "value": dept}
                    for dept, dept_name in departments.items()],
            value="75"  # Valeur par défaut : premier département
        )
    ]),
    html.Div(dcc.Graph(id="bar-top-categories-for-department"))
    #html.Div(dcc.Link('Revenir à la page d\'accueil', href='/'))
], style={'background': 'beige'})

# Fonction de création du graphique à barres pour la page du top 5 des catégories d'emplois recrutant le plus par département
def create_bar_top_categories_for_department(df):
    fig = px.pie(df,
        values="count",
        names="_id")
    return fig

# Mise à jour du graphique à barres pour la page du top 5 des catégories d'emplois recrutant le plus par département
@callback(
    Output("bar-top-categories-for-department", "figure"),
    Input("dropdown-department", "value")
)
def update_bar_chart(selected_department):
    if not get_data(selected_department):
        return dash.no_update
    df = pd.DataFrame(data["result"])
    df = df.sort_values(by="count", ascending=False)
    return create_bar_top_categories_for_department(df)

def get_data(selected_department):
    global data
    data = get_top_categories_for_dep(selected_department)
    if data == None:
        logger.error("No data obtained")
        return False
    else:
        return True