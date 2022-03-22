# Import Required Libraries
import pandas as pd
from dash import Dash, dcc, html, Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = Dash(__name__)

# Create an app layout
app.layout = html.Div(
    children=[
        html.H1(
            'SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36','font-size': 40}
        ),
        # The default select value is for ALL sites
        dcc.Dropdown(
            id='site-dropdown',
            options=[
                {'label': 'All sites', 'value': 'all'},
                {'label': 'CCAFS LC-40', 'value': 'CCAFS LC-40'},
                {'label': 'VAFB SLC-4E', 'value': 'VAFB SLC-4E'},
                {'label': 'KSC LC-39A', 'value': 'KSC LC-39A'},
                {'label': 'CCAFS SLC-40', 'value': 'CCAFS SLC-40'}
            ],
            value='all',
            placeholder='Select a launch site',
            searchable=True
        ),
        html.Br(),
        
        # Add a pie chart to show the total successful launches count for all sites
        # If a specific launch site was selected, show the Success vs. Failed counts for the site
        html.Div(dcc.Graph(id='success-pie-chart')),
        html.Br(),
        
        html.P("Payload range (Kg):"),
        # Add a slider to select payload range
        dcc.RangeSlider(
            id='payload-slider',
            min=0,
            max=10_000,
            step=1_000,
            value=[min_payload, max_payload]
        ),

        # Add a scatter chart to show the correlation between payload and launch success
        html.Div(dcc.Graph(id='success-payload-scatter-chart')),
    ]
)

# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value')
)
def get_pie_chart(site):
    if site =='all':
        df_pie = spacex_df[['Launch Site', 'class']].groupby('Launch Site', as_index=False).sum()
        fig = px.pie(
            df_pie,
            values='class',
            names='Launch Site',
            title='Successful launches by site'
        )
    else:
        df_pie = spacex_df[spacex_df['Launch Site'] == site].copy()
        df_pie = df_pie[['Flight Number', 'class']].groupby('class', as_index=False).count()
        fig = px.pie(
            df_pie,
            values='Flight Number',
            names='class',
            title='Success for launches from site ' + site
        )
    return fig

# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value'),
     Input(component_id='payload-slider', component_property='value')]
)
def get_scatter_chart(site, min_max_payload):
    if site == 'all':
        scat_df = spacex_df[(spacex_df['Payload Mass (kg)'] >= min_max_payload[0])
                            & (spacex_df['Payload Mass (kg)'] <= min_max_payload[1])].copy()
        fig = px.scatter(
            scat_df,
            x='Payload Mass (kg)',
            y='class',
            color='Booster Version Category',
            title='Correlation between payload and success for all launching sites'
        )
    else:
        scat_df = spacex_df[(spacex_df['Payload Mass (kg)'] >= min_max_payload[0])
                            & (spacex_df['Payload Mass (kg)'] <= min_max_payload[1])
                            & (spacex_df['Launch Site'] == site)].copy()
        fig = px.scatter(
            scat_df,
            x='Payload Mass (kg)',
            y='class',
            color='Booster Version Category',
            title='Correlation between payload and success for launch site ' + site
        )
    return fig

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
