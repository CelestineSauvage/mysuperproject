import dash
from dash import dcc, html, callback
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px
from api_requests import get_departments, get_top_cities_for_dep
import logging

# Page du top des villes recrutant le plus par département

# setup logger
log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
logging.basicConfig(format=log_format, level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Variable contenant le dernier JSON des données obtenues de l'API Rest
data = None

dash.register_page(__name__, path= "/top-cities-for-department")

app = dash.get_app()

# Layout de la page
layout = html.Div([
    html.H1("Top des villes recrutant le plus par département"),
    html.Div([
        dcc.Dropdown(
            id="dropdown-department",
            options = [{'label': f"{dept['code']} - {dept['libelle']}", 
                        'value': dept['code']} for dept in get_departments()],
            value="75"  # Valeur par défaut : premier département
        ),
        dcc.Slider(
            id="slider-top-cities",
            min=1,
            max=20,
            step=1,
            value=10,
            marks={i: str(i) for i in range(2, 31)}
        )
    ]),
    html.Div(dcc.Graph(id="bar-top-cities-for-department"))
], style={'background': 'beige'})

# Fonction de création du graphique à barres
def create_bar_top_cities_for_department(df):
    fig = px.bar(df,
        x="_id",
        y="count",
        title=f"Top {df.shape[0]}")

    # Personnalisation du graphique
    fig.update_traces(marker_color='rgb(0,102,204)',
        marker_line_color='rgb(8,48,107)',
        marker_line_width=1.5,
        opacity=0.8,
        name='Nombre d\'offres')  # Ajouter du nom pour la légende
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(
            title='Nom de la ville',
            showline=True,
            showgrid=False,
            showticklabels=True,
            linecolor='rgb(204, 204, 204)',
            linewidth=2,
            ticks='outside',
            tickfont=dict(
                family='Arial',
                size=12,
                color='rgb(82, 82, 82)',
            ),
        ),
        yaxis=dict(
            title="Nombre d'offres",
            showline=True,
            showgrid=False,
            showticklabels=True
        ),
        margin=dict(l=40, r=30, b=80, t=100),
        showlegend=True
    )

    return fig

# Mise à jour de la valeur max dans le slider du nombre de villes
@callback(
    [Output("slider-top-cities", "max"), Output("slider-top-cities", "value")],
    Input("dropdown-department", "value")
)
def update_max_slider_top_cities(selected_department):
    if not get_data(selected_department):
        return dash.no_update
    # s'assurer que la valeur ne dépasse pas 20 qui est le nombre
    # max de villes qu'on veut afficher dans le graphique
    return min(len(data["result"]), 20), min(len(data["result"]), 10)


# Mise à jour du graphique à barres
@callback(
    Output("bar-top-cities-for-department", "figure"),
    [Input("dropdown-department", "value"),
    Input("slider-top-cities", "value")]
)
def update_bar_chart(selected_department, top_cities_number):
    if not get_data(selected_department):
        return dash.no_update
    df = pd.DataFrame(data["result"])
    df = df.sort_values(by="count", ascending=False).head(top_cities_number)
    return create_bar_top_cities_for_department(df)

def get_data(selected_department):
    global data
    data = get_top_cities_for_dep(selected_department)
    if data == None:
        logger.error("No data obtained")
        return False
    else:
        return True