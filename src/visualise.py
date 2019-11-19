# Visualise
# This script will be responsible for visualising the dataframes it receives

import altair as alt


def gen_charts(data, color_scheme='bluegreen'):
    """

    :param color_column:
    :param title:
    :param tooltip_map:
    :param color_scheme:
    :return:
    """

    """
    Generates world map
    """

    tooltip_map = ['properties.country:O', 'properties.percent_wins:Q']
    selector = alt.selection_multi()

    # Add Base Layer
    base = alt.Chart(data, title='Percentage of home wins', width=1080).mark_geoshape(
        stroke='black',
        strokeWidth=1
    ).encode(
    ).properties(
        width=1000,
        height=1000
    )

    # Add Choropleth Layer
    choro = alt.Chart(data).mark_geoshape(
        fill='lightgray',
        stroke='black'
    ).encode(
        color=alt.condition(selector,
                            alt.Color('properties.percent_wins', type='nominal',
                                      scale=alt.Scale(scheme=color_scheme)),
                            alt.value('lightgray')),
        tooltip=tooltip_map
    ).add_selection(selector)

    map = base + choro

    """ 
    Generate time chart
    """
    tooltip_timeline = ['properties.country:O', 'properties.games:Q']
    brush = alt.selection_interval(encodings=['x'], empty='none')

    timeline = alt.Chart(data, width=1080).mark_area(opacity=0.3).encode(
        x='properties.date:Q',
        y=alt.Y('properties.games:Q'),
        color=alt.Color('properties.country:N', scale=alt.Scale(scheme=color_scheme)),
        tooltip=tooltip_timeline
    ).transform_filter(
        selector
    )

    return alt.vconcat(map, timeline)


def visualise_results(geodata):
    """

    :param geodata:
    :param data:
    :return:
    """

    charts = gen_charts(data=geodata,
                        color_scheme='yelloworangered')

    charts.serve()
