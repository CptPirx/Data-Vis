# Data Manipulator
# Script that will transform the data into frames that will be visualised

import pandas as pd
import numpy as np


# This method will be called from main
def run_manipulation(data, start_year, end_year):
    assign_victories(data, start_year, end_year)


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
    mask = (data['date'] > start_date) & (data['date'] <= end_date)
    data = data.loc[mask]
    return data


# This method will create a data frame that assigns number of
# games. wins. losses and draws for each country in a given time period between 1872 and 2019
def assign_victories(data, start_date, end_date):
    # Test print
    print(data)
    print(data.dtypes)

    # New empty data frame
    results_assigned = pd.DataFrame(
        columns=['country',
                 'wins', 'home_wins', 'away_wins', 'neutral_wins',
                 'draws', 'home_draws', 'away_draws', 'neutral_draws',
                 'losses', 'home_losses', 'away_losses', 'neutral_losses',
                 'home_games', 'away_games', 'neutral_games'])

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

        country_id = country_id + 1

    # Sort results alphabetically and reset indices
    results_assigned = results_assigned.sort_values('country')
    results_assigned = results_assigned.reset_index(drop=True)
    print(results_assigned)

    return results_assigned

