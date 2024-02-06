import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output, State, ctx
import json

#********DATA********
population_data = pd.read_csv("world_population.csv")
map_json = json.load(open("countries.json", "r"))

population_data.rename(columns = {'Country Code':'CCA3', 'Area (km²)':'Area'}, inplace = True)
max_population = population_data['2022 Population'].max()

continents = sorted(population_data["Continent"].unique())
continents.append("World")

year_df = pd.DataFrame([1970, 1980, 1990, 2000, 2010, 2015, 2020, 2022], columns =['Year'])

#globally used variables
selected_countries_chor = []
selected_countries_bar = []
selected_conutries_continent = []


app = Dash(__name__)
server = app.server

#********APP LAYOUT********
app.layout = html.Div(
    style={'backgroundColor': '#323130',
           'color': 'white',
           'margin': 0,
           'padding': '15px'},

    children=[
        # Title
        html.H1("World Population", style={'text-align': 'center'}),
        html.H3('Visualisation of World Population or Population Density', style={'text-align': 'center'}),

        html.Hr(),
        html.Br(),

        html.Div(children=[
            'Select what you want to visualize: ',

            # Radio items - Population Density or Total Population
            dcc.RadioItems(
                options=[
                    {'label': 'Population Density', 'value': 'density'},
                    {'label': 'Total Population', 'value': 'total'}
                ],
                id='radio_items',
                value='total',
                inline=True
            )],
            style={'width': '100%', 'display': 'inline-flex'}
        ),

        html.Br(),

        html.Div(children=[
            'Select a year:',
            dcc.Slider(
                step=None,
                id='year_slider',
                marks={
                    1970: '1970',
                    1980: '1980',
                    1990: '1990',
                    2000: '2000',
                    2010: '2010',
                    2015: '2015',
                    2020: '2020',
                    2022: '2022',
                },
                value=2022,
            ),
        ],
            style={'width': '100%', 'display': 'inline-block'}
        ),
        html.Br(),
        html.Br(),
        html.Br(),

        # Choropleth map
        html.Div([
            dcc.Graph(id="choropleth_map", figure={}),
        ],
            style={'width': '50%', 'display': 'inline-block'}
        ),

        # continents population
        html.Div([
            dcc.Graph(id="continents_population", figure={}),
        ],
            style={'width': '50%', 'display': 'inline-block'}
        ),
        html.Hr(),
        dcc.Markdown('### Top countries/territories by total population or population density'),

        # select number of countries to display and continent
        html.Div(children=[
            'Select the number of countries to display: ',
            dcc.Input(id='number_input', value=15, type='number', min=2, max=30,
                      style={'backgroundColor': '#323130', 'color': 'white'}),
            html.Button('Submit', id='submit_button', n_clicks=0,
                        style={'backgroundColor': '#323130', 'color': 'white'}),
            html.Br(),
            html.Div(children=[
                'Select a continent: ',
                dcc.RadioItems(id='continent_dropdown',
                               options=[{'label': i, 'value': i} for i in continents],
                               value='World',
                               inline=True,
                               style={'backgroundColor': '#323130', 'color': 'white'}),
            ],
                style={'width': '100%', 'display': 'flex', 'align-items': 'center'}
            )
        ],
            style={'width': '100%', 'display': 'inline-block'}
        ),

        html.Br(),
        # Bar chart - top countries based on the mode selected
        html.Div([
            dcc.Graph(id="top_countries", figure={}),
        ],
            style={'width': '100%', 'display': 'inline-block'}
        ),
    ]
)


#********FUNCTIONS********

# Function to prepare data based on the year and mode selected
def get_data(year, mode):
    data = population_data.copy()
    population_column = str(year) + " Population"
    data['Population'] = data[population_column]
    data['Density'] = data['Population'] / data["Area"]

    column = 'Density' if mode == "density" else 'Population'

    return data, column

# Function to get the highlights for the selected countries
def get_highlights():
    district_lookup = {feature['properties']['geounit']: feature for feature in map_json['features']}
    geojson_highlights = dict()
    for k in map_json.keys():
        if k != 'features':
            geojson_highlights[k] = map_json[k]
        else:
            geojson_highlights[k] = [district_lookup[selection] for selection in selected_countries_chor]
    return geojson_highlights


# Function to get the choropleth map
def get_map(year, mode):
    data, column = get_data(year, mode)
    data['Density'] = data['Density'].apply(lambda x: round(x, 0))
    data['Density'] = data['Density'].apply(lambda x: int(x))
    color_range = [0, max_population] if mode == "total" else [0, 500]

    fig = px.choropleth_mapbox(data,  # data
                               geojson=map_json,
                               featureidkey='properties.geounit',  # property in geojson
                               locations='Country/Territory',  # column in dataframe matching featureidkey
                               color=column,  # dataframe
                               hover_name='Country/Territory',
                               hover_data=['Population', 'Density'],
                               color_continuous_scale='Reds',  # color scale
                               range_color=color_range,
                               mapbox_style="carto-positron",  # choose a mapbox style
                               center={"lat": 20, "lon": 0},  # set the initial map center
                               zoom=0.5,  # set the initial zoom level
                               opacity=0.8,
                               title='World Population',
                               width=900,
                               height=500,
                           )

    if len(selected_countries_chor) > 0:
        highlights = get_highlights()
        fig.add_trace(
            px.choropleth_mapbox(data,  # data
                                geojson=highlights,
                                 featureidkey='properties.geounit',  # property in geojson
                                 locations='Country/Territory',  # column in dataframe matching featureidkey
                                 color=column,  # dataframe
                                 hover_name='Country/Territory',
                                 hover_data={'Population': True, 'Density': True, 'Country/Territory': False},
                                 color_continuous_scale='Reds',  # color scale
                                 range_color=color_range,
                                 mapbox_style="carto-positron",  # choose a mapbox style
                                 center={"lat": 20, "lon": 0},  # set the initial map center
                                 zoom=0.5,  # set the initial zoom level
                                 opacity=1,
                                 title='World Population',
                                 width=900,
                                 height=500,
                                 ).data[0]
        )
    hover_template = "<b>%{customdata[0]}</b><br>" \
                     "Population: %{customdata[1]:,.0f}<br>" \
                     "Density: %{customdata[2]: } people/km²"
    fig.update_traces(hovertemplate=hover_template, customdata=data[['Country/Territory', 'Population', 'Density']])

    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
    fig.update_layout(geo_bgcolor="#323130", plot_bgcolor="#323130", paper_bgcolor="#323130", font_color="white", )
    return fig


# Function to get the bar chart
def get_top_countries_bar_chart(year, mode, number, continent, select_country):
    data = population_data.copy()
    population_column = str(year) + " Population"

    if select_country:
        country_name = selected_countries_bar[0]
        new_name = country_name + " (Selected)"
        selected_country_data = data[data['Country/Territory'] == country_name].copy()
        selected_country_data['Population'] = selected_country_data[population_column]
        selected_country_data['Density'] = selected_country_data['Population'] / selected_country_data["Area"]
        selected_country_data['Country/Territory'] = new_name

    if continent != "World":
        data = data[data['Continent'] == continent]

    population_column = str(year) + " Population"
    data['Population'] = data[population_column]
    data['Density'] = data['Population'] / data["Area"]
    column = 'Density' if mode == "density" else 'Population'
    data = data[['Country/Territory', 'Population', 'Density']]
    data = data.sort_values(by=column, ascending=False)
    data = data.head(number)

    if select_country:
        data = pd.concat([data, selected_country_data], ignore_index=True)

    else:
        record = {'Country/Territory': 'No Country Selected', 'Population': 0, 'Density': 0}
        data = pd.concat([data, pd.DataFrame([record])], ignore_index=True)

    # set the color of the selected country to red and not show the legend
    data['Color'] = 'gray'
    cd_map = {'gray': 'gray'}
    if select_country:
        data.loc[data['Country/Territory'] == new_name, 'Color'] = 'darkred'
        cd_map = {'gray': 'gray', 'darkred': 'darkred'}

    fig = px.bar(data, x='Country/Territory', y=column, color='Color', title='Top Countries by ' + mode,
                 color_discrete_map=cd_map)

    data['Density'] = data['Density'].apply(lambda x: int(x))
    hover_template = "<b>%{customdata[0]}</b><br>" \
                     "Population: %{customdata[1]:,.0f}<br>" \
                     "Density: %{customdata[2]: } people/km²"
    fig.update_traces(hovertemplate=hover_template, customdata=data[['Country/Territory', 'Population', 'Density']])

    fig.update_layout(title_text='Top Countries by ' + mode)
    fig.update_layout(showlegend=False)
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
    fig.update_layout(plot_bgcolor="#323130", paper_bgcolor="#323130", font_color="white")
    return fig


# Function to get the pie chart
def get_continents_population_pie_chart(year, mode):
    highlight_continent = None
    if len(selected_conutries_continent) > 0:
        highlight_country = selected_conutries_continent[0]
        highlight_continent = population_data[population_data['Country/Territory'] == highlight_country]['Continent'].values[0]
    print('year:', year, 'mode:', mode, 'highlight_continent:', highlight_continent)
    data, column = get_data(year, mode)
    data = data.groupby('Continent').agg({'Population': 'sum', 'Area': 'sum'}).reset_index()
    data['Density'] = data['Population'] / data["Area"]
    data['Density'] = data['Density'].apply(lambda x: int(x))
    data['Color'] = 'orange'

    if highlight_continent is not None:
        # Check if highlight_continent is not None before trying to locate it
        if highlight_continent in data['Continent'].values:
            data.loc[data['Continent'] == highlight_continent, 'Color'] = 'darkred'

    cd_map = {'Asia': 'yellow', 'Europe': 'salmon', 'Africa': 'orange', 'Oceania': 'lightyellow', 'North America': 'gold', 'South America': 'linen'}
    if highlight_continent is not None:
        cd_map[highlight_continent] = 'darkred'

    fig = px.pie(data, values='Population', names='Continent',
                 color='Continent', color_discrete_sequence=px.colors.sequential.Greys, title='Continents Population',
                 hover_name='Continent', labels={'Population': 'Population'}, hover_data=['Density'])

    if highlight_continent is not None:
        highlighted_mask = data['Continent'] == highlight_continent
        fig.update_traces(
            marker=dict(colors=['darkred' if highlighted else 'grey' for highlighted in highlighted_mask]))

    hover_template = "<b>%{label}</b><br>" \
                     "Population: %{value:,.0f}<br>" \
                     "Density: %{customdata[0]: } people/km²"

    fig.update_traces(hovertemplate=hover_template, customdata=data['Density'])
    fig.update_layout(title_text='Continents Population', title_y=0.99)
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
    fig.update_layout(plot_bgcolor="#323130", paper_bgcolor="#323130", font_color="white")
    return fig


# Function to get the country name based on trigger_id
def get_selected_country(selected_choropleth, selected_bar, trigger_id):
    if trigger_id == "choropleth_map":
        return selected_choropleth['points'][0]['location']
    elif trigger_id == "top_countries":
        return selected_bar['points'][0]['x']
    else:
        return None


#********CALLBACKS********

@app.callback(
    Output("choropleth_map", "figure"),
    [Input("year_slider", "value"),
     Input("radio_items", "value"),
     Input("choropleth_map", "clickData"),
     Input("top_countries", "clickData")]

)
def update_choropleth_map(year, mode, selected_choropleth, selected_bar):
    trigger_id = ctx.triggered_id
    selected_country = get_selected_country(selected_choropleth, selected_bar, trigger_id)
    if selected_country:
        if selected_country in selected_countries_chor:
            selected_countries_chor.clear()
        else:
            selected_countries_chor.clear()
            selected_countries_chor.append(selected_country)

    fig = get_map(year, mode)
    return fig


@app.callback(
    Output("top_countries", "figure"),
    [Input("year_slider", "value"),
     Input("radio_items", "value"),
     Input("submit_button", "n_clicks"),
     Input("continent_dropdown", "value"),
     Input("choropleth_map", "clickData"),
     Input("top_countries", "clickData"),],
    State("number_input", "value")
)
def update_top_countries(year, mode, n_cliks, continent, select_choropleth, select_bar, number_input):
    number = 6
    if n_cliks is not None:
        number = number_input
    trigger_id = ctx.triggered_id
    selected_country = get_selected_country(select_choropleth, select_bar, trigger_id)
    if selected_country:
        if selected_country in selected_countries_bar:
            selected_countries_bar.clear()
        else:
            selected_countries_bar.clear()
            selected_countries_bar.append(selected_country)

    selected = True if len(selected_countries_bar) > 0 else False
    fig = get_top_countries_bar_chart(year, mode, number, continent, selected)
    return fig


@app.callback(
    Output("continents_population", "figure"),
    [Input("year_slider", "value"),
     Input("radio_items", "value"),
     Input("choropleth_map", "clickData"),
     Input("top_countries", "clickData")]
)
def update_continents_population(year, mode, selected_choropleth, selected_bar):  #,selected_bar):
    trigger_id = ctx.triggered_id
    print("trigger_id: ", trigger_id)

    country_name = get_selected_country(selected_choropleth, selected_bar, trigger_id)

    if country_name:
        if country_name in selected_conutries_continent:
            selected_conutries_continent.clear()
        else:
            selected_conutries_continent.clear()
            selected_conutries_continent.append(country_name)


    fig = get_continents_population_pie_chart(year, mode)
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)