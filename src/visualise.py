# Visualise
# This script will be responsible for visualising the dataframes it receives

import pandas as pd
import altair as alt


def visualise_results(data):

    data = data[(data['percent_neutral_wins'] >= 0.4) & (data['neutral_games'] >= 20)]

    chart = alt.Chart(data).mark_point().encode(
        x='country',
        y='percent_wins',
        color='percent_home_wins'
    )

    chart.serve()



