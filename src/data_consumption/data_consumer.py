import dash
from dash import dcc, html

# Création de l'application Dash
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, 
                external_stylesheets=external_stylesheets, 
                use_pages=True,
                suppress_callback_exceptions=True
        )

dash.register_page("home",  path='/')

app.layout = html.Div([
    html.H1('Projet JOB Market', style={
            'color': 'aquamarine', 'textAlign': 'center'}),
    html.Div([
        html.Div(
            dcc.Link(f"{page['name']}", href=page["relative_path"])
        ) for page in dash.page_registry.values()
    ], style={'alignItems': 'center', 'background': 'beige'}),
    html.Br(),
    dash.page_container
])

if __name__ == '__main__':
    app.run_server(debug=True, host="0.0.0.0")