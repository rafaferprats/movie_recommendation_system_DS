# Import packages
from dash import Dash, html, dash_table, dcc, callback, Output, Input
import pandas as pd
import plotly.express as px
import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State

# Incorporate data
df = pd.read_csv('data/movie_reco_scores.csv')

# Initialize the app
app = dash.Dash(__name__, 
                ### THE ONLY CHANGE FROM THE ABOVE, PLEASE ADD IN THIS LINE
                requests_pathname_prefix='/dashboard1/')

# App layout
app.layout = html.Div([
    html.Div(children='Evaluation Dashboard, Time, Nº cluster and Scores'),
    html.Hr(),
    dcc.RadioItems(options=['retraining_time_seconds','num_users','db_score_reco_user_15','db_score_reco_user_25','db_score_reco_user_35','db_score_reco_user_45','db_score_reco_movie_15','db_score_reco_movie_25','db_score_reco_movie_35','db_score_reco_movie_45','ch_score_reco_user_15','ch_score_reco_user_25','ch_score_reco_user_35','ch_score_reco_user_45','ch_score_reco_movie_15','ch_score_reco_movie_25','ch_score_reco_movie_35','ch_score_reco_movie_45'], value='retraining_time_seconds', id='controls-and-radio-item'),
    dash_table.DataTable(data=df.to_dict('records'), page_size=6),
    dcc.Graph(figure={}, id='controls-and-graph')
])

# Add controls to build the interaction
@callback(
    Output(component_id='controls-and-graph', component_property='figure'),
    Input(component_id='controls-and-radio-item', component_property='value')
)
def update_graph(col_chosen):
    fig = px.line(df, x='num_retraining', y=col_chosen)
    return fig

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
    
