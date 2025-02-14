# Import required libraries
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                # dcc.Dropdown(id='site-dropdown',...)
                                html.Div([
                                    dcc.Dropdown(
                                        id='site-dropdown',
                                        options=[{'label': 'All Sites', 'value': 'ALL'}] + 
                                                [{'label': site, 'value': site} for site in spacex_df['Launch Site'].unique()],
                                        value='ALL',
                                        placeholder="Select a Launch Site here",
                                        searchable=True
                                    )
                                ]),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                dcc.RangeSlider(
                                    id='payload-slider',
                                    min=min_payload,
                                    max=max_payload,
                                    step=1000,
                                    marks={i: str(i) for i in range(int(min_payload), int(max_payload)+1, 2000)}, 
                                    value=[min_payload, max_payload]
                                ),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output

@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value')
)

def update_pie_chart(selected_site):
    # Filter the dataframe based on selection
    if selected_site == 'ALL':
        # Group by Launch Site and count successful launches
        success_counts = spacex_df[spacex_df['class'] == 1].groupby('Launch Site').size()
        fig = px.pie(
            names=success_counts.index, 
            values=success_counts.values, 
            title="Total Successful Launches by Site"
        )
    else:
        # Filter dataframe for the selected site
        filtered_df = spacex_df[spacex_df['Launch Site'] == selected_site]
        site_counts = filtered_df['class'].value_counts()
        fig = px.pie(
            names=site_counts.index.map({0: "Failed", 1: "Success"}), 
            values=site_counts.values, 
            title=f"Launch Outcomes for {selected_site}"
        )
    
    return fig

# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value'),
     Input(component_id='payload-slider', component_property='value')]
)
def update_scatter_chart(selected_site, payload_range):
    # Filter data based on payload range
    filtered_df = spacex_df[(spacex_df['Payload Mass (kg)'] >= payload_range[0]) &
                             (spacex_df['Payload Mass (kg)'] <= payload_range[1])]
    
    # Further filter by selected launch site
    if selected_site != 'ALL':
        filtered_df = filtered_df[filtered_df['Launch Site'] == selected_site]

    # Create scatter plot
    fig = px.scatter(
        filtered_df, 
        x='Payload Mass (kg)', 
        y='class',
        color='Booster Version',
        title=f"Payload vs. Outcome for {selected_site}" if selected_site != 'ALL' else "Payload vs. Outcome for All Sites",
        labels={'class': 'Launch Outcome'}
    )

    return fig


# Run the app
if __name__ == '__main__':
    app.run_server()
