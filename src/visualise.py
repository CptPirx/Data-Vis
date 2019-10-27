# Visualise
# This script will be responsible for visualising the dataframes it receives

import pandas as pd
import geopandas as gpd
import altair as alt
import vega_datasets
import json


def gen_map(geodata, color_column, title, tooltip, color_scheme='bluegreen'):
    '''
    Generates world map
    '''

    selection = alt.selection_multi(fields=[color_column])
    color = alt.condition(selection,
                          alt.Color(color_column, type='nominal',
                                    scale=alt.Scale(scheme=color_scheme)),
                          alt.value('lightgray'))

    # Add Base Layer
    base = alt.Chart(geodata, title=title).mark_geoshape(
        stroke='black',
        strokeWidth=1
    ).encode(
    ).properties(
        width=800,
        height=800
    )
    # Add Choropleth Layer
    choro = alt.Chart(geodata).mark_geoshape(
        fill='lightgray',
        stroke='black'
    ).encode(
        color=color,
        tooltip=tooltip
    ).add_selection(
        selection
    )
    return base + choro


def gen_comparison(geodata, color_column, title, tooltip, color_scheme='bluegreen'):
    """

    """

    brush = alt.selection_interval()  # selection of type "interval"

    chart = alt.Chart(geodata).mark_point().encode(
        y='percent_wins:Q',
        color=alt.condition(brush, 'name:O', alt.value('lightgray'))
    ).properties(
        width=250,
        height=250
    ).add_selection(
        brush
    )

    chart.encode(x='percent_home_wins:Q')

    return chart


def open_geojson(geo_json_file_loc):
    with open(geo_json_file_loc) as json_data:
        d = json.load(json_data)
    return d


def get_gpd_df(geo_json_file_loc):
    toronto_json = open_geojson(geo_json_file_loc)
    gdf = gpd.GeoDataFrame.from_features((toronto_json))
    return gdf


def visualise_results(data):
    data = data[(data['total_games'] >= 0)]

    geo_json_file_loc = 'D:/OneDrive/Aarhus/Semestr 3/Data Visualization/Project/Data/custom.geo.json'

    gdf = get_gpd_df(geo_json_file_loc)

    # Sort results alphabetically and reset indices
    gdf = gdf.sort_values('name')
    gdf = gdf.reset_index(drop=True)

    # Manually fixing few countries
    data.loc[data['country'].str.contains('China'), 'country'] = 'China'
    data.loc[data['country'].str.contains('Czech'), 'country'] = 'Czech Rep.'
    data.loc[data['country'].str.contains('DR Congo'), 'country'] = 'Dem. Rep. Congo'
    data.loc[data['country'].str.contains('Central Africa'), 'country'] \
        = 'Central African Rep.'

    gdf = gdf.merge(data, left_on='name', right_on='country', how='inner')
    choro_json = json.loads(gdf.to_json())
    choro_data = alt.Data(values=choro_json['features'])

    map_chart = gen_map(geodata=choro_data,
                        color_column='properties.percent_wins',
                        title=f'Percentage of home wins',
                        tooltip=['properties.country:O', 'properties.percent_wins:Q'],
                        color_scheme='yelloworangered')

    slider_chart = gen_comparison(geodata=choro_data,
                                  color_column='properties.percent_home_wins',
                                  title=f'Percentage of home wins',
                                  tooltip=['properties.country:O', 'properties.percent_home_wins:Q'],
                                  color_scheme='yelloworangered')

    charts = alt.vconcat(map_chart, slider_chart)

    charts.serve()
