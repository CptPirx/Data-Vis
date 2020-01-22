# Data Manipulator
# Script that will transform the data into frames that will be visualised

import LoadData as DataLoader
import pandas as pd
import geopandas as gpd
import numpy as np
import altair as alt
import pycountry
import urllib.request, json


def run_manipulation(results, regions, start_year, end_year):
    """
    This method will be called from main
    :param results:
    :param regions:
    :param start_year:
    :param end_year:
    :return:
    """
    stat_data = prepare_data(results, regions)

    # Manually fixing a few countries
    stat_data.loc[stat_data['country'].str.contains('China'), 'country'] = 'China'
    stat_data.loc[stat_data['country'].str.contains('Brunei'), 'country'] = 'Brunei Darussalam '
    stat_data.loc[stat_data['country'].str.contains('DR Congo'), 'country'] = 'Congo, The Democratic Republic of the'
    stat_data.loc[stat_data['country'].str.contains('Ivory'), 'country'] = 'Côte d\'Ivoire'
    stat_data.loc[stat_data['country'].str.contains('South Korea'), 'country'] = 'Korea, Republic of'

    data = for_altair(stat_data)

    return data


def create_empty_DataFrame(columns, index_col):
    """
    Method to create an empty DataFrame
    :param columns:
    :param index_col:
    :return:
    """
    index_type = next((t for name, t in columns if name == index_col))
    df = pd.DataFrame({name: pd.Series(dtype=t) for name, t in columns if name != index_col},
                      index=pd.Index([], dtype=index_type))
    cols = [name for name, _ in columns]
    cols.remove(index_col)
    return df[cols]


def select_between_dates(data, start_date, end_date):
    """
    Method to select games between specific dates. Dates are in format 'yyyy-mm-dd'
    :param data:
    :param start_date:
    :param end_date:
    :return:
    """
    mask = (data['date'] > start_date) & (data['date'] <= end_date)
    data = data.loc[mask]
    return data


def prepare_data(results, regions):
    results['date'] = results['date'].dt.year

    # Create table with number of home wins
    home_wins_table = results[['home_team', 'winner', 'date', 'tournament']][results.winner == results.home_team]
    home_wins_table = home_wins_table.groupby(
        ['home_team',
         'date',
         'tournament'])['winner'].count().reset_index(name="home_wins")

    # Create table with number of away wins
    away_wins_table = results[['away_team', 'winner', 'date', 'tournament']][results.winner == results.away_team]
    away_wins_table = away_wins_table.groupby(
        ['away_team',
         'date',
         'tournament'])['winner'].count().reset_index(name="away_wins")

    # Create table with number of away draws
    away_draw_table = results[['away_team', 'winner', 'date', 'tournament']][results.winner == 'draw']
    away_draw_table = away_draw_table.groupby(
        ['away_team',
         'date',
         'tournament'])['winner'].count().reset_index(name="away_draws")

    # Create table with number of home draws
    home_draw_table = results[['home_team', 'winner', 'date', 'tournament']][results.winner == 'draw']
    home_draw_table = home_draw_table.groupby(
        ['home_team',
         'date',
         'tournament'])['winner'].count().reset_index(name="home_draws")

    # Create table with number of away losses
    away_loss_table = results[['away_team', 'winner', 'date', 'tournament']][
        (results.winner != 'draw') & (results.winner != results.away_team)]
    away_loss_table = away_loss_table.groupby(
        ['away_team',
         'date',
         'tournament'])['winner'].count().reset_index(name="away_losses")

    # Create table with number of home losses
    home_loss_table = results[['home_team', 'winner', 'date', 'tournament']][
        (results.winner != 'draw') & (results.winner != results.home_team)]
    home_loss_table = home_loss_table.groupby(
        ['home_team',
         'date',
         'tournament'])['winner'].count().reset_index(name="home_losses")

    # Calculate the number of all games
    total_games_table = to_history_chart(results)

    # Create the summary table
    data_home_wins = pd.DataFrame(home_wins_table)
    data_home_draws = pd.DataFrame(home_draw_table)
    data_home_losses = pd.DataFrame(home_loss_table)
    data_home = pd.merge(data_home_wins,
                         data_home_draws,
                         how='outer',
                         on=['home_team', 'date', 'tournament'])
    data_home = pd.merge(data_home,
                         data_home_losses,
                         how='outer',
                         on=['home_team', 'date', 'tournament'])

    data_home.rename(columns={'home_team': 'country'}, inplace=True)

    data_away_wins = pd.DataFrame(away_wins_table)
    data_away_draws = pd.DataFrame(away_draw_table)
    data_away_losses = pd.DataFrame(away_loss_table)
    data_away = pd.merge(data_away_wins,
                         data_away_draws,
                         how='outer',
                         on=['away_team', 'date', 'tournament'])
    data_away = pd.merge(data_away,
                         data_away_losses,
                         how='outer',
                         on=['away_team', 'date', 'tournament'])

    data_away.rename(columns={'away_team': 'country'}, inplace=True)

    data = pd.merge(
        data_home,
        data_away,
        how='outer',
        on=['country', 'date', 'tournament'])

    data = pd.merge(
        data,
        total_games_table,
        how='inner',
        on=['country', 'date', 'tournament']
    )

    data.fillna(0, inplace=True)
    data.sort_values(by=['country', 'date'], inplace=True)
    data.reset_index(drop=True, inplace=True)

    data.rename(columns={0: 'total_games'}, inplace=True)
    # We have data for each year, each tournament
    # Now calculate all the percentages
    data['percent_wins'] = data.apply(
        lambda row: ((row.home_wins + row.away_wins) / row.total_games) if row.total_games > 0 else 0,
        axis=1)
    data['percent_home_wins'] = data.apply(
        lambda row: (row.home_wins / (row.home_wins + row.home_draws + row.home_losses))
        if (row.home_wins + row.home_draws + row.home_losses) > 0
        else 0,
        axis=1)
    data['percent_away_wins'] = data.apply(
        lambda row: (row.away_wins / (row.away_wins + row.away_draws + row.away_losses))
        if (row.away_wins + row.away_draws + row.away_losses) > 0
        else 0,
        axis=1)

    data_out = pd.merge(data, regions, how='inner', left_on=['country'], right_on=['ShortName'])

    DataLoader.save_to_sql(data_out, "results_assigned")

    return data_out


# Bin it
def assign_victories(data, regions, start_date, end_date):
    """
    This method will create a data frame that assigns number of
    games. wins. losses and draws for each country in a given time period between 1872 and 2019
    :param data:
    :param regions:
    :param start_date:
    :param end_date:
    :return:
    """
    columns = [
        ('id', str),
        ('date', str),
        ('country', str),
        ('home_wins', int),
        ('away_wins', int),
        ('neutral_wins', int),
        ('home_draws', int),
        ('away_draws', int),
        ('neutral_draws', int),
        ('home_losses', int),
        ('away_losses', int),
        ('neutral_losses', int),
        ('home_games', int),
        ('away_games', int),
        ('neutral_games', int),
        ('total_games', int),
        ('percent_wins', float),
        ('percent_home_wins', float),
        ('percent_away_wins', float),
        ('percent_neutral_wins', float)
    ]
    results_assigned = create_empty_DataFrame(columns, 'id')

    # Select entries between the given dates
    data = select_between_dates(data, start_date, end_date)

    # Populate the countries column
    results_assigned['country'] = pd.unique(data[['home_team', 'away_team']].values.ravel('K'))

    # Count the number of home, away and neutral games/wins/losses/draws for each team
    # Iterate through each country
    country_id = 0
    for country in results_assigned.country:
        team_games = data[((data['away_team'] == country) | (data['home_team'] == country))]
        home_games, away_games, neutral_games = 0, 0, 0
        home_wins, home_losses, home_draws = 0, 0, 0
        away_wins, away_losses, away_draws = 0, 0, 0
        neutral_wins, neutral_losses, neutral_draws = 0, 0, 0

        # Iterate through each game
        for pos, row in team_games.iterrows():
            # Count home values
            if (row.home_team == country) & (row.neutral == 'FALSE'):
                # Add home game
                home_games = home_games + 1
                # Add win
                if row.winner == country:
                    home_wins = home_wins + 1
                # Add draw
                elif row.winner == 'draw':
                    home_losses = home_losses + 1
                # Add loss
                else:
                    home_draws = home_draws + 1
            # Count away values
            elif (row.away_team == country) & (row.neutral == 'FALSE'):
                # Add away game
                away_games = away_games + 1
                # Add win
                if row.winner == country:
                    away_wins = away_wins + 1
                # Add draw
                elif row.winner == 'draw':
                    away_losses = away_losses + 1
                # Add loss
                else:
                    away_draws = away_draws + 1
            # Count neutral values
            elif row.neutral == 'TRUE':
                # Add neutral game
                neutral_games = neutral_games + 1
                # Add win
                if row.winner == country:
                    neutral_wins = neutral_wins + 1
                # Add draw
                elif row.winner == 'draw':
                    neutral_losses = neutral_losses + 1
                # Add loss
                else:
                    neutral_draws = neutral_draws + 1

        # Assign the counted numbers to each country
        # Assign number of games
        results_assigned.at[country_id, 'home_games'] = home_games
        results_assigned.at[country_id, 'away_games'] = away_games
        results_assigned.at[country_id, 'neutral_games'] = neutral_games
        results_assigned.at[country_id, 'total_games'] = home_games + away_games + neutral_games

        # Assign number of wins
        results_assigned.at[country_id, 'home_wins'] = home_wins
        results_assigned.at[country_id, 'home_losses'] = home_losses
        results_assigned.at[country_id, 'home_draws'] = home_draws

        # Assign number of losses
        results_assigned.at[country_id, 'away_wins'] = away_wins
        results_assigned.at[country_id, 'away_losses'] = away_losses
        results_assigned.at[country_id, 'away_draws'] = away_draws

        # Assign number of draws
        results_assigned.at[country_id, 'neutral_wins'] = neutral_wins
        results_assigned.at[country_id, 'neutral_losses'] = neutral_losses
        results_assigned.at[country_id, 'neutral_draws'] = neutral_draws

        # Assign the percentages
        total_wins = neutral_wins + away_wins + home_wins
        results_assigned.at[country_id, 'percent_wins'] = np.round(total_wins /
                                                                   (home_games + away_games + neutral_games), 2)

        if total_wins != 0:
            results_assigned.at[country_id, 'percent_home_wins'] = np.round(home_wins / total_wins, 2)
            results_assigned.at[country_id, 'percent_away_wins'] = np.round(away_wins / total_wins, 2)
            results_assigned.at[country_id, 'percent_neutral_wins'] = np.round(neutral_wins / total_wins, 2)
        else:
            results_assigned.at[country_id, 'percent_home_wins'] = 0
            results_assigned.at[country_id, 'percent_away_wins'] = 0
            results_assigned.at[country_id, 'percent_neutral_wins'] = 0

        country_id = country_id + 1

    # Sort results alphabetically and reset indices
    results_assigned = results_assigned.sort_values('country')
    results_assigned = results_assigned.reset_index(drop=True)

    results_assigned.loc[results_assigned['country'].str.contains('China'), 'country'] = 'China'
    results_assigned.loc[results_assigned['country'].str.contains('DR Congo'), 'country'] = 'Dem. Rep. Congo'
    results_assigned.loc[results_assigned['country'].str.contains('Republic of Ireland'), 'country'] = 'Ireland'
    regions.loc[regions['ShortName'].str.contains('Slovak'), 'ShortName'] = 'Slovakia'
    regions.loc[regions['ShortName'].str.contains('Ivoir'), 'ShortName'] = 'Ivory Coast'
    regions.loc[(regions['ShortName'].str.contains('Korea')) & (regions['IncomeGroup'].str.contains('OECD')),
                'ShortName'] = 'South Korea'

    results_assigned = pd.merge(results_assigned, regions, how='inner', left_on=['country'], right_on=['ShortName'])

    DataLoader.save_to_sql(results_assigned, "results_assigned")

    return results_assigned


# Bin it
def to_history_chart(data):
    """

    :param data:
    :return:
    """

    # data['date'] = data['date'].dt.year

    # Calculate number of home and away games for each year
    home_games = pd.crosstab(
        [data.home_team, data.tournament],
        data.date,
        rownames=['country', 'tournament'],
        colnames=['date']
    )

    away_games = pd.crosstab(
        [data.away_team, data.tournament],
        data.date,
        rownames=['country', 'tournament'],
        colnames=['date']
    )

    # home_games.rename(columns={'away_team': 'country'}, inplace=True)
    # home_games.set_index(['country', 'date'], inplace=True)
    #
    # away_games.rename(columns={'away_team': 'country'}, inplace=True)
    # away_games.set_index(['country', 'date'], inplace=True)

    # Add those two values for number of total games per year
    time_stats = home_games.add(away_games, fill_value=0)

    # Change to 'classic' dataframe
    time_stats = time_stats.stack().reset_index()

    return time_stats


def for_altair(stat_data):
    """

    :param stat_data:
    :param time_data:
    :return:
    """
    def country_search(name):
        country = pycountry.countries.get(name=name)
        if country is not None:
            return country.numeric
        else:
            country = pycountry.countries.search_fuzzy(name)
            return country[0].numeric

    print('country loop')
    stat_data['CountryCode'] = np.vectorize(country_search)(stat_data['country'])

    # print('melt')
    # data = pd.melt(stat_data, id_vars=['country',
    #                                    'date',
    #                                    'tournament',
    #                                    'total_games',
    #                                    'percent_wins',
    #                                    'CountryCode',
    #                                    'home_wins',
    #                                    'away_wins'],
    #                value_vars=['percent_home_wins',
    #                            'percent_away_wins'],
    #                var_name='statistics',
    #                value_name='values')

    DataLoader.save_to_sql(stat_data, "final_data")

    return stat_data


def open_geojson(geo_json_file_loc):
    """

    :param geo_json_file_loc:
    :return:
    """
    with open(geo_json_file_loc) as json_data:
        d = json.load(json_data)
    return d


def get_gpd_df(geo_json_file_loc):
    """

    :param geo_json_file_loc:
    :return:
    """
    toronto_json = open_geojson(geo_json_file_loc)
    gdf = gpd.GeoDataFrame.from_features(toronto_json)
    return gdf


def get_geodata():
    """

    :return:
    """
    geo_json_file_loc = 'D:/OneDrive/Aarhus/Semestr 3/Data Visualization/Project/Data/custom.geo.json'

    gdf = get_gpd_df(geo_json_file_loc)

    # Sort results alphabetically and reset indices
    gdf = gdf.sort_values('name')
    gdf = gdf.reset_index(drop=True)

    return gdf


def merge_geodata(data):
    """
    Create the geospacial data
    :param data:
    :return:
    """
    gdf = get_geodata()
    gdf = gdf.merge(data, left_on='iso_a3', right_on='CountryCode', how='inner')

    # Convert the geodata to json
    choro_json = json.loads(gdf.to_json())
    final_geo_data = alt.Data(values=choro_json['features'])

    return final_geo_data
