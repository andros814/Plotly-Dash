import pandas as pd
import dash
# import dash_html_components as html  # deprecated
from dash import html
# import dash_core_components as dcc  # deprecated
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px

spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()


app = dash.Dash(__name__)

app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}),
    dcc.Dropdown(
        id='site-dropdown',
        options=[
            {'label': 'All Sites', 'value': 'ALL'},
            {'label': 'Cape Canaveral Launch Complex 40 (CAFS LC-40)', 'value': 'CCAFS LC-40'},
            {'label': 'Cape Canaveral Space Launch Complex 40 (CCAFS SLC-40)', 'value': 'CCAFS SLC-40'},
            {'label': 'Kennedy Space Center Launch Complex 39A (KSC LC-39A)', 'value': 'KSC LC-39A'},
            {'label': 'Vandenberg Air Force Base Space Launch Complex (VAFB SLC-4E)', 'value': 'VAFB SLC-4E'}
        ],
        value='ALL',
        placeholder="Select a Launch Site",
        searchable=True
    ),

    html.Br(),
    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(),

    html.P("Payload range (Kg):"),
    dcc.RangeSlider(id='payload-slider',
                    min=0, max=10000, step=1000,
                    # marks={0: '0', 100: '100'},
                    value=[min_payload, max_payload]),
    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
    ])

@app.callback(Output(component_id='success-pie-chart', component_property='figure'),
              Input(component_id='site-dropdown', component_property='value'))
def get_pie_chart(entered_site):
    filtered_df = spacex_df.groupby(['Launch Site'], as_index=False).mean()
    if entered_site == 'ALL':
        return px.pie(filtered_df, values='class', names='Launch Site', title='Launch Success Rate For All Sites')
    filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]
    filtered_df['outcome'] = filtered_df['class'].apply(lambda x: 'Success' if (x == 1) else 'Failure')
    filtered_df['counts'] = 1
    return px.pie(filtered_df, values='counts', names='outcome', title='Launch Success Rate For ' + entered_site)

@app.callback(Output(component_id='success-payload-scatter-chart', component_property='figure'),
              [Input(component_id='site-dropdown', component_property='value'),
               Input(component_id="payload-slider", component_property="value")])
def get_scatter_chart(entered_site, slider):
    filtered_df = spacex_df[
        (slider[0] <= spacex_df['Payload Mass (kg)']) & (spacex_df['Payload Mass (kg)'] <= slider[1])
    ]
    if entered_site == 'ALL':
        return px.scatter(filtered_df,
                          x='Payload Mass (kg)', y='class',
                          color='Booster Version Category',
                          title='Launch Success Rate For All Sites')
 
    filtered_df = filtered_df[filtered_df['Launch Site'] == entered_site]
    filtered_df['outcome'] = filtered_df['class'].apply(lambda x: 'Success' if (x == 1) else 'Failure')
    filtered_df['counts'] = 1
    return px.scatter (filtered_df,
                       x='Payload Mass (kg)', y='class',
                       color='Booster Version Category',
                       title='Launch Success Rate For ' + entered_site)

if __name__ == '__main__':
    app.run_server()