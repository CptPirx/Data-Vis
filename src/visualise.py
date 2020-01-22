# Visualise
# This script will be responsible for visualising the dataframes it receives

import altair as alt
import panel as pn
from vega_datasets import data as vega_data


def gen_charts(data, color_scheme='bluegreen'):
    """

    :param data:
    :param color_scheme:
    :return:
    """
    print(data)
    data = data.round(3)

    alt.data_transformers.disable_max_rows()

    # Color scheme
    color_gradient = 'yelloworangered'
    color_category = 'tableau10'

    map_json = alt.topo_feature('https://cdn.jsdelivr.net/npm/world-atlas@2/countries-50m.json', 'countries')

    tooltip_map = ['country:N', 'percent_wins:Q', 'total_games:Q']
    selector = alt.selection_multi(fields=['country'], empty='none')

    # options_list = list(data.tournament.unique())
    # options_list.sort()

    # Cutoff
    slider = alt.binding_range(min=1880, max=2019, step=1)
    slider_selector = alt.selection_single(name="The", fields=['date'],
                                           bind=slider, init={'date': 2018})

    # Tournament selection
    input_dropdown = alt.binding_select(options=['Friendly',
                                                 'FIFA World Cup',
                                                 'FIFA World Cup qualification',
                                                 'UEFA Euro',
                                                 'UEFA Euro qualification',
                                                 'UEFA Nations League'])

    dropdown_selector = alt.selection_single(fields=['tournament'], bind=input_dropdown, name='Type of')

    """
    Generates world map
    """

    # Add Base Layer
    base_map = alt.Chart(
        map_json,
        title="International football visualisation"
    ).mark_geoshape(
        stroke='black',
        strokeWidth=1
    ).encode(

    ).properties(
        width=900,
        height=500
    ).add_selection(
        dropdown_selector
    ).add_selection(
        slider_selector
    ).add_selection(
        selector
    )

    choro_map = alt.Chart(
        data
    ).transform_lookup(
        lookup='CountryCode',
        from_=alt.LookupData(map_json, 'id'),
        as_='geo',
        default='Other'
    ).transform_calculate(
        geometry='datum.geo.geometry',
        type='datum.geo.type'
    ).transform_filter(
        dropdown_selector
    ).transform_filter(
        slider_selector
    ).mark_geoshape(
        stroke='black',
        strokeWidth=1
    ).encode(
        color=alt.Color('percent_wins:Q',
                        legend=alt.Legend(format='0.0%',
                                          title="Proportion of wins"),
                        scale=alt.Scale(scheme=color_gradient)),
        tooltip=tooltip_map
    ).properties(

    )

    map = (base_map + choro_map).project('naturalEarth1')
    """
    Generate the bar chart with statistics
    """

    left_bar = alt.Chart(
        data,
        title="Proportion of home wins"
    ).mark_bar().encode(
        x=alt.X('country:N', title="Country"),
        y=alt.Y('percent_home_wins:Q', title="Percentage", axis=alt.Axis(format='0.0%')),
        # color=alt.Color('country:N',
        #                 scale=alt.Scale(scheme=color_category)),
        tooltip=['percent_home_wins:Q',
                 'home_games:Q',
                 'home_wins:Q']
    ).transform_filter(
        selector
    ).transform_filter(
        slider_selector
    ).transform_filter(
        dropdown_selector
    ).transform_calculate(
        home_games='datum.home_wins + datum.home_draws + datum.home_losses'
    )

    right_bar = alt.Chart(
        data,
        title="Proportion of away wins"
    ).mark_bar().encode(
        x=alt.X('country:N', title="Country"),
        y=alt.Y('percent_away_wins:Q', title="Percentage", axis=alt.Axis(format='0.0%')),
        # color=alt.Color('country:N',
        #                 scale=alt.Scale(scheme=color_category)),
        tooltip=['percent_away_wins:Q',
                 'away_games:Q',
                 'away_wins:Q']
    ).transform_filter(
        selector
    ).transform_filter(
        slider_selector
    ).transform_filter(
        dropdown_selector
    ).transform_calculate(
        away_games='datum.away_wins + datum.away_draws + datum.away_losses'
    )

    """
    Generate the line chart
    """
    line = alt.Chart(data).mark_area(opacity=0.3).encode(
        alt.X('binned_date:Q', scale=alt.Scale(zero=False)),
        alt.Y('percent_wins:Q', scale=alt.Scale(zero=False), stack=False),
        color='country:N'
    ).transform_filter(
        selector
    ).properties(
        width=1000
    ).transform_bin(
        'binned_date', 'date', bin=alt.Bin(maxbins=20)
    )

    """
    Return all charts 
    """
    return (left_bar | map | right_bar)


def gen_online_map(data):
    def plot_map(area_type, width=500, height=300):
        map_json = alt.topo_feature('https://cdn.jsdelivr.net/npm/world-atlas@2/countries-50m.json', 'countries')

        country_map = alt.Chart(
            data,
            title=f'# Respondents by {area_type}'
        ).transform_filter(
            col1_brush
        ).transform_filter(
            col2_brush
        ).transform_lookup(
            lookup='CountryCode',
            from_=alt.LookupData(map_json, 'properties.id'),
            as_='geom',
            default='Other'
        ).transform_aggregate(
            counter='count()',
            groupby=['geom', area_type]
        ).transform_calculate(
            geometry='datum.geom.geometry',
            type='datum.geom.type'
        ).transform_filter(
            alt.datum.date == 2018
        ).mark_geoshape(
        ).encode(
            color='counter:Q',
            tooltip=[
                alt.Tooltip(f'{area_type}:N', title='Area'),
                alt.Tooltip('counter:Q', title='# Respondents')
            ]
        ).properties(
            width=width,
            height=width
        )

        borders = alt.Chart(map_json).mark_geoshape(
            fill='#EEEEEE',
            stroke='gray',
            strokeWidth=1
        ).properties(
            width=width,
            height=height
        )

        return (borders + country_map)

    def plot_bar(col_name, selection=None, width=500):
        chart = alt.Chart(
            data[[col_name]],
            title=''
        ).mark_bar().encode(
            y=f'{col_name}:N',
            x='count():Q',
            tooltip=[
                alt.Tooltip('count()', title='Count')
            ],
            color=alt.condition(selection, alt.value('steelblue'), alt.value('lightgray'))
        ).add_selection(
            selection
        ).properties(
            width=width
        ).transform_filter(
            alt.datum.date == 2018
        )

        return chart

    def plot_dash(area_type):
        return (plot_map(area_type) & plot_bar(col1_name, col1_brush) & plot_bar(col2_name, col2_brush)).resolve_legend(
            'independent')

    area_type = 'country'
    col1_name = 'percent_home_wins'
    col1_brush = alt.selection_multi(fields=[col1_name])
    col2_name = 'percent_away_wins'
    col2_brush = alt.selection_multi(fields=[col2_name])

    return plot_dash(area_type)


def visualise_results(data):
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
                        color_scheme='yelloworangered')

    charts.serve()

    # dashboard = pn.Row(pn.Column(title, subtitle), get_plot)
    #
    # dashboard.show()
