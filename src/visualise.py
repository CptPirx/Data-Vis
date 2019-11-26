# Visualise
# This script will be responsible for visualising the dataframes it receives

import altair as alt
import pandas as pd
import panel as pn
import datetime as dt


def gen_charts(data, geodata, color_scheme='bluegreen'):
    """

    :param data:
    :param color_scheme:
    :return:
    """
    alt.data_transformers.disable_max_rows()

    map_json = alt.topo_feature('https://cdn.jsdelivr.net/npm/world-atlas@2/countries-50m.json', 'countries')

    tooltip_timeline = ['country:N', 'games:Q', 'date_x:Q']
    brush = alt.selection_interval(encodings=['x'], empty='all')

    tooltip_map = ['country:N', 'percent_wins:Q']
    selector = alt.selection_multi(fields=['country'], empty='all')

    """
    Generates world map
    """

    # Add Base Layer
    base = alt.Chart(map_json).mark_geoshape(
        stroke='black',
        strokeWidth=1
    ).encode(
        color=alt.condition(selector, alt.Color('percent_wins:Q',
                                                scale=alt.Scale(scheme=color_scheme)),
                            alt.value('lightgray')),
        tooltip=tooltip_map
    ).transform_lookup(
        lookup='id',
        from_=alt.LookupData(data, 'CountryCode', ['country', 'percent_wins'])
    ).properties(
        width=800,
        height=600
    ).add_selection(
        selector
    )

    map = base.project('equirectangular')

    """ 
    Generate timeline
    """

    timeline = alt.Chart(data).mark_area(opacity=0.3).encode(
        x='date_x:Q',
        y=alt.Y('games:Q', stack=False),
        color=alt.condition(brush, 'country:N', alt.value('lightgrey')),
        tooltip=tooltip_timeline
    ).properties(
        width=1000
    ).add_selection(
        brush
    ).transform_filter(
        selector
    )

    """
    Generate the side bar charts
    """

    data = pd.melt(data, id_vars=['country', 'date_x'], value_vars=['percent_home_wins',
                                                                    'percent_away_wins',
                                                                    'percent_neutral_wins'],
                   var_name='statistics',
                   value_name='values')

    left_bar = alt.Chart(data).mark_bar().encode(
        x='statistics:N',
        y=alt.Y('values:Q'),
        color='statistics:N',
        column='country:N'
    ).transform_filter(
        selector
    )

    """
    Return all charts 
    """
    return alt.vconcat(map,
                       left_bar,

                       title="International football results")


def visualise_results(data, geodata):
    """

    :param geodata:
    :return:
    """

    # """
    # Create the dashboard
    # """
    #
    # pn.extension('vega')
    #
    # title = '  ### Stock Price Dashboard'
    # subtitle = 'This dashboard allows you to select a company and date range to see stock prices.'
    #
    # @pn.depends()
    # def get_plot():
    #     # create the Altair chart object
    #     charts = gen_charts(data=data,
    #                         geodata=geodata,
    #                         color_scheme='yelloworangered')
    #
    #     return charts

    charts = gen_charts(data=data,
                        geodata=geodata,
                        color_scheme='yelloworangered')

    charts.serve()

    # dashboard = pn.Row(pn.Column(title, subtitle), get_plot)
    #
    # dashboard.show()
