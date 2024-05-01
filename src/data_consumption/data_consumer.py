import dash
from dash import dcc, html

# Création de l'application Dash
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, 
                external_stylesheets=external_stylesheets, 
                use_pages=True,
                suppress_callback_exceptions=True
        )

app.layout = html.Div([
    #html.Div(
    #    html.Img(src=image_url, style={'width': '100%'}),
    #    style={'textAlign': 'center'}
    #),
    html.H1('Projet JOB Market', 
            style={'color': 'blue', 'textAlign': 'center', 
                'font-size': '50px', 'font-weight': 'bold'}),
    html.Div([
        html.Div(
            dcc.Link(page["name"], href=page["relative_path"]), 
            style={'margin': '10px', 'padding': '10px', 'border': '1px solid #ccc',
            'borderRadius': '5px', 'background': 'lightblue', 
            'textAlign': 'center', 'font-weight': 'bold'}
        ) for page in dash.page_registry.values()
        ], style={'display': 'flex', 'flexDirection': 'column', 'alignItems': 'center', 
            'marginTop': '20px', 'backgroundColor': '#f9f9f9', 'padding': '20px'}),
    html.Br(),
    dash.page_container
])

if __name__ == '__main__':
    app.run_server(debug=True, host="0.0.0.0")