import dash
from dash import dcc, html, callback
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px
from api_requests import get_departments, get_job_repartition_by_experience_level_for_dep
import logging

# Page de la répartition des jobs par niveau d'expérience

# setup logger
log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
logging.basicConfig(format=log_format, level=logging.DEBUG)
logger = logging.getLogger(__name__)

dash.register_page(__name__, path= "/job-repartition-by-experience-level-for-dep")

app = dash.get_app()

# Layout de la page
layout = html.Div([
    html.H2("Répartition des jobs par niveau d'expérience pour un département"),
    html.Div([
        dcc.Dropdown(
            id="dropdown-department",
            options = [{'label': f"{dept['code']} - {dept['libelle']}", 
                        'value': dept['code']} for dept in get_departments()],
            value="75"  # Valeur par défaut : premier département
        )
    ]),
    html.Div(dcc.Graph(id="bar-job-repartition-by-experience-level-for-dep"))
], style={'background': 'beige'})

# Fonction de création du graphique à barres
def create_bar_job_repartition_by_experience_level_for_dep(df):
    # Calcul des pourcentages
    total = df['Nombre'].sum()
    df['Pourcentage'] = ((df['Nombre'] / total) * 100).round(0)

    # Création du graphique à barres
    fig = px.bar(df, x=df.index, y='Pourcentage', text='Pourcentage')

    # Modification du nom de l'axe des abscisses
    fig.update_layout(xaxis=dict(title='Expérience'))
    # Mise en forme du texte au-dessus des barres
    fig.update_traces(textposition='outside', texttemplate='%{text}%')

    # Ajustement de la marge supérieure du graphique
    fig.update_layout(margin=dict(b=1))

    return fig

# Mise à jour du graphique à barres
@callback(
    Output("bar-job-repartition-by-experience-level-for-dep", "figure"),
    Input("dropdown-department", "value")
)
def update_bar_chart(selected_department):
    data = get_job_repartition_by_experience_level_for_dep(selected_department)
    
    if data == None:
        logger.error("No data obtained")
        return dash.no_update

    # Création d'un dictionnaire pour mapper les nouvelles clés
    mapping = {
        "exp_1_4_an": "1 à 4 ans",
        "exp_4_an": "4 ans ou plus",
        "moins_1_an": "Moins d'1 an"
    }
    # Renommer les clés dans le dictionnaire result
    data["result"] = {mapping[key]: value for key, value in data["result"].items()}
        
    # Création du DataFrame à partir des données JSON
    df = pd.DataFrame.from_dict(data['result'], orient='index', columns=['Nombre'])
    
    return create_bar_job_repartition_by_experience_level_for_dep(df)
