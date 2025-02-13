import dash
from dash import dcc, html, callback
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px
from api_requests import get_departments, get_top_categories_for_dep
import logging

# Page Top 5 des catégories d'emplois recrutant le plus par département

# setup logger
log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
logging.basicConfig(format=log_format, level=logging.DEBUG)
logger = logging.getLogger(__name__)

dash.register_page(__name__, path= "/top-categories-for-department")

app = dash.get_app()

departments = get_departments()

# Layout de la page
layout = html.Div([
    html.H2("Top 5 des catégories d'emplois recrutant le plus par département"),
    html.Div([
        dcc.Dropdown(
            id="dropdown-department",
            options = [{'label': f"{dept['code']} - {dept['libelle']}", 
                        'value': dept['code']} for dept in get_departments()],
            value="75"  # Valeur par défaut : premier département
        )
    ]),
    html.Div(dcc.Graph(id="pie-top-categories-for-department"))
], style={'background': 'beige'})

# Fonction de création du graphique en camember
def create_pie_top_categories_for_department(df):
    fig = px.pie(df,
        values="count",
        names="_id")
    
    fig.update_traces(textfont=dict(
        size=18  # Définir la taille du texte
    ))
        
    fig.update_layout(legend=dict(
        font=dict(
            size=18  # Définir la taille du texte de la légende
        )
    ))
    
    return fig

# Mise à jour du graphique en camember
@callback(
    Output("pie-top-categories-for-department", "figure"),
    Input("dropdown-department", "value")
)
def update_pie_chart(selected_department):
    data = get_top_categories_for_dep(selected_department)
    
    if data == None:
        logger.error("No data obtained")
        return dash.no_update
    
    df = pd.DataFrame(data["result"])
    df = df.sort_values(by="count", ascending=False)
    return create_pie_top_categories_for_department(df)