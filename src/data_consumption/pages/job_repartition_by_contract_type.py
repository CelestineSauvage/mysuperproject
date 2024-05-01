import dash
from dash import dcc, html, callback
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px
from api_requests import get_departments, get_job_repartition_by_contract_type_for_dep
import logging

# Page de la répartition des jobs par type de contrat

# setup logger
log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
logging.basicConfig(format=log_format, level=logging.DEBUG)
logger = logging.getLogger(__name__)
 
dash.register_page(__name__, path= "/job-repartition-by-contract-type-for-dep")

app = dash.get_app()

# Layout de la page
layout = html.Div([
    html.H2("Répartition des jobs par type de contrat pour un département"),
    html.Div([
        dcc.Dropdown(
            id="dropdown-department",
            options = [{'label': f"{dept['code']} - {dept['libelle']}", 
                        'value': dept['code']} for dept in get_departments()],
            value="75"  # Valeur par défaut : premier département
        )
    ]),
    html.Div(dcc.Graph(id="pie-job-repartition-by-contract-type-for-dep"))
], style={'background': 'beige'})

# Fonction de création du graphique à barres
def create_pie_job_repartition_by_contract_type_for_dep(df):
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

# Mise à jour du graphique à barres
@callback(
    Output("pie-job-repartition-by-contract-type-for-dep", "figure"),
    Input("dropdown-department", "value")
)
def update_bar_chart(selected_department):
    data = get_job_repartition_by_contract_type_for_dep(selected_department)
    
    if data == None:
        logger.error("No data obtained")
        return dash.no_update
    
    df = pd.DataFrame(data["result"])
    df = df.sort_values(by="count", ascending=False)
    return create_pie_job_repartition_by_contract_type_for_dep(df)