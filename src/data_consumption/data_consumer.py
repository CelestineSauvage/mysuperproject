import dash
from dash import dcc, html, Input, Output
import pandas as pd
import plotly.express as px

# Données d'exemple
data = {
    "75": {"Paris": 5000, "Boulogne-Billancourt": 3000, "Levallois-Perret": 2500, "Neuilly-sur-Seine": 2000, 
           "Issy-les-Moulineaux": 1800, "Montrouge": 1500, "Vincennes": 1400, "Vanves": 1300, 
           "Saint-Mandé": 1200, "Malakoff": 1100, "Clichy": 1000, "Gentilly": 900, "Bagnolet": 800,
           "Pantin": 700, "Suresnes": 600, "Montreuil": 500, "Le Kremlin-Bicêtre": 400,
           "Saint-Ouen-sur-Seine": 300, "Ivry-sur-Seine": 200, "Fontenay-sous-Bois": 100,
           "Cachan": 100, "Arcueil": 100, "Charenton-le-Pont": 100, "Le Pré-Saint-Gervais": 100,
           "Les Lilas": 100, "Nogent-sur-Marne": 100, "Romainville": 100, "Joinville-le-Pont": 100,
           "Alfortville": 100},
    "31": {"Toulouse": 4000, "Colomiers": 2500, "Blagnac": 2000, "Muret": 1500},
    "30": {"Nîmes": 4500, "Alès": 3200, "Bagnols-sur-Cèze": 2800, "Beaucaire": 2000, 
           "Saint-Gilles": 1800, "Vauvert": 1700, "Marguerittes": 1600, "Pont-Saint-Esprit": 1500,
           "Uzès": 1400, "Les Angles": 1300, "Pujaut": 1200, "Aigues-Mortes": 1100,
           "La Grand-Combe": 1000, "Le Grau-du-Roi": 900, "Le Vigan": 800, "Saint-Christol-lès-Alès": 700,
           "Calvisson": 600, "Redessan": 500, "Nîmes": 400, "Nîmes": 300,
           "Nîmes": 200, "Nîmes": 100}
}

# Création du dictionnaire de numéro de département et nom de département
departments = {
    "75": "Paris",
    "31": "Haute-Garonne",
    "30": "Gard"
}


# Création de l'application Dash
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets,suppress_callback_exceptions=True)
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id = 'page-content')
])

# Page d'accueil
home_page_layout = html.Div([
    html.H1('Projet JOB Market', style={'color' : 'aquamarine', 'textAlign': 'center'}),
    html.Button(dcc.Link('Top des villes recrutant le plus par département', href='/top-cities-for-department')),
    #html.Br(),
    #html.Button(dcc.Link('Autre-page', href='/autre-page'))
], style={'alignItems': 'center', 'background' : 'beige'})


# Page Top des villes recrutant le plus par département
top_cities_for_department_layout = html.Div([
    html.H1("Top N des villes recrutant le plus par département"),
    html.Div([
        dcc.Dropdown(
            id="dropdown-department",
            options=[{"label": f"{dept} - {dept_name}", "value": dept} for dept, dept_name in departments.items()],
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
    html.Div(dcc.Graph(id="bar-top-cities-for-department")),
    html.Button(dcc.Link('Revenir à la page d\'accueil', href='/'))
], style = {'background' : 'beige'})

# Fonction de création du graphique à barres pour la page du top des villes recrutant le plus par département
def create_bar_top_cities_for_department(df):
    fig = px.bar(df, 
        x=df.index, 
        y="Nombre d'offres", 
        text=df["Nombre d'offres"], 
        title=f"Top {df.shape[0]} villes recrutant le plus")

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
            title='Nom de la ville',  # Ajout du titre de l'axe des abscisses
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
            showgrid=False,
            zeroline=False,
            showline=False,
            showticklabels=False,
        ),
        margin=dict(l=40, r=30, b=80, t=100),
        showlegend=True
    )

    return fig

# Fonction de mise à jour du nombre maximal de villes dans le slider
@app.callback(
    Output("slider-top-cities", "max"),
    [Input("dropdown-department", "value")]
)
def update_slider_max(selected_department):
    cities_of_dep = len(data[selected_department])
    return min(cities_of_dep, 20)  # s'assurer que le nombre maximal est 20

# Fonction de mise à jour du graphique à barres pour la page du top des villes recrutant le plus par département
@app.callback(
    Output("bar-top-cities-for-department", "figure"),
    [Input("dropdown-department", "value"),
    Input("slider-top-cities", "value")]
)
def update_bar_chart(selected_department, top_cities):
    df = pd.DataFrame.from_dict(data[selected_department], orient='index', columns=["Nombre d'offres"])
    df = df.sort_values(by="Nombre d'offres", ascending=False).head(top_cities)
    return create_bar_top_cities_for_department(df)


# Mise à jour de l'index
@app.callback(dash.dependencies.Output('page-content', 'children'),
    [dash.dependencies.Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/top-cities-for-department':
        return top_cities_for_department_layout
    # elif pathname == '/autre-page....':
        #return autre_page_layout...
    else:
        return home_page_layout


# Lancement de l'application
if __name__ == '__main__':
    app.run_server(debug=True,host="0.0.0.0")