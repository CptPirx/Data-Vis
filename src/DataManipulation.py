# Data Manipulator
# Script that will transform the data into frames that will be visualised

import LoadData as DataLoader
import pandas as pd
import geopandas as gpd
import numpy as np
import altair as alt
import json


# This method will be called from main
def run_manipulation(results, regions, start_year, end_year):
    stat_data = assign_victories(results, regions, start_year, end_year)
    time_data = to_history_chart(results)

    # Manually fixing a few countries
    stat_data.loc[stat_data['country'].str.contains('China'), 'country'] = 'China'
    stat_data.loc[stat_data['country'].str.contains('Czech'), 'country'] = 'Czech Rep.'
    stat_data.loc[stat_data['country'].str.contains('DR Congo'), 'country'] = 'Dem. Rep. Congo'
    stat_data.loc[stat_data['country'].str.contains('Central Africa'), 'country'] \
        = 'Central African Rep.'

    time_data.loc[time_data['country'].str.contains('China'), 'country'] = 'China'
    time_data.loc[time_data['country'].str.contains('Czech'), 'country'] = 'Czech Rep.'
    time_data.loc[time_data['country'].str.contains('DR Congo'), 'country'] = 'Dem. Rep. Congo'
    time_data.loc[time_data['country'].str.contains('Central Africa'), 'country'] \
        = 'Central African Rep.'

    data = for_altair(stat_data, time_data)

    return data


# Method to create an empty DataFrame
def create_empty_DataFrame(columns, index_col):
    index_type = next((t for name, t in columns if name == index_col))
    df = pd.DataFrame({name: pd.Series(dtype=t) for name, t in columns if name != index_col},
                      index=pd.Index([], dtype=index_type))
    cols = [name for name, _ in columns]
    cols.remove(index_col)
    return df[cols]


# Method to select games between specific dates. Dates are in format 'yyyy-mm-dd'
def select_between_dates(data, start_date, end_date):
    """

    :param data:
    :param start_date:
    :param end_date:
    :return:
    """
    mask = (data['date'] > start_date) & (data['date'] <= end_date)
    data = data.loc[mask]
    return data


# This method will create a data frame that assigns number of
# games. wins. losses and draws for each country in a given time period between 1872 and 2019
def assign_victories(data, regions, start_date, end_date):
    """

    :param data:
    :param regions:
    :param start_date:
    :param end_date:
    :return:
    """
    columns = [
        ('id', str),
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

    # Manually fixing few countries
    # print(regions.loc[regions['ShortName'].str.contains('Korea')])
    # print(results_assigned.loc[results_assigned['country'].str.contains('Korea')])

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


def to_history_chart(data):
    """

    :param data:
    :return:
    """

    data['date'] = data['date'].dt.year

    # Calculate number of home and away games for each year
    home_games = pd.crosstab(data.date, data.home_team)
    away_games = pd.crosstab(data.date, data.away_team)

    # Add those two values for number of total games per year
    time_stats = home_games.add(away_games, fill_value=0)

    # Change to 'classic' dataframe
    time_stats = time_stats.stack().reset_index()
    time_stats.columns = ['date', 'country', 'games']

    return time_stats


def for_altair(stat_data, time_data):
    """

    :param stat_data:
    :param time_data:
    :return:
    """
    print(time_data)
    print(stat_data)

    # Merge the (x, y) metadata into the long-form view
    data = pd.merge(time_data, stat_data, on='country')

    print(data)

    DataLoader.save_to_sql(data, "final_data")

    return data


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
    gdf = gpd.GeoDataFrame.from_features((toronto_json))
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
    # Create the geospacial data
    gdf = get_geodata()
    gdf = gdf.merge(data, left_on='name', right_on='country', how='inner')

    # Convert the geodata to json
    choro_json = json.loads(gdf.to_json())
    final_geo_data = alt.Data(values=choro_json['features'])

    return final_geo_data