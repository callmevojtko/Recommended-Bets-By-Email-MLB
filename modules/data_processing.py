"""
data_processing.py
-------------------

This module contains utility functions for processing and transforming data for the MLB betting application.

Functions:
- get_games_playing_today: Identify games that are scheduled for today.
- load_and_preprocess_data: Load, merge, and preprocess the MLB data.
- fetch_team_features: Fetch features for a specific team using its ID.
- prefix_columns: Add a prefix to all columns in a dataframe with an exception for 'Team_ID'.

Imports:
- Standard libraries: datetime, pandas
- External libraries: sklearn.model_selection
"""

# Imports
from datetime import datetime
import pandas as pd
from sklearn.model_selection import train_test_split


def get_games_playing_today(api_data, team_to_id):
    """
    Identify games that are scheduled for today based on the provided API data.

    Args:
    - api_data (list): List of games fetched from the API.
    - team_to_id (dict): Dictionary mapping team names to their respective IDs.

    Returns:
    - set: A set of team IDs that have games scheduled for today.
    """

    games_playing_today_ids = set()
    current_date_utc = datetime.utcnow().date()
    print(f"Current date in UTC: {current_date_utc}")
    for game in api_data:
        commence_time = datetime.strptime(
            game['commence_time'], '%Y-%m-%dT%H:%M:%SZ')
        commence_date_utc = commence_time.date()
        print(
            f"Commence time for {game['home_team']} vs {game['away_team']}: {commence_date_utc}")
        if commence_date_utc == current_date_utc:
            print(f"This game is considered a 'today's game'")
            games_playing_today_ids.add(team_to_id[game['home_team']])
            games_playing_today_ids.add(team_to_id[game['away_team']])

    return games_playing_today_ids


def load_and_preprocess_data(games_playing_today_ids, batting_data, pitching_data, fielding_data, standings_data):
    """
    Load, merge, and preprocess the MLB data. Then split the data into training and testing sets.

    Args:
    - games_playing_today_ids (set): A set of team IDs that have games scheduled for today.
    - batting_data, pitching_data, fielding_data, standings_data (DataFrame): DataFrames containing MLB statistics.

    Returns:
    - Tuple: Training and testing datasets.
    """

    # Merge the batting, pitching, and standings data on 'Team_ID'
    mlb_data = pd.merge(batting_data, pitching_data, on='Team_ID')
    mlb_data = pd.merge(mlb_data, fielding_data, on='Team_ID')
    mlb_data = pd.merge(mlb_data, standings_data, on='Team_ID')

    # Print out the unique team IDs present in the resulting DataFrame
    print("Unique Team IDs in Merged Data:", mlb_data['Team_ID'].unique())

    # Check if the pybaseball data is not empty
    if mlb_data.empty:
        raise Exception("The pybaseball data is empty.")

    # Filter the mlb_data DataFrame to only include rows where the team ID is in games_playing_today_ids
    mlb_data_today = mlb_data[mlb_data['Team_ID'].isin(
        games_playing_today_ids)]

    # Check if the filtered DataFrame is not empty
    if mlb_data_today.empty:
        raise Exception("The filtered DataFrame is empty.")

    # Split the data into training and testing sets
    train_data, test_data = train_test_split(mlb_data_today, test_size=0.2)

    return train_data, test_data


def fetch_team_features(team_id, train_data):
    """
    Fetch features for a specific team using its ID.

    Args:
    - team_id (str): The ID of the team.
    - train_data (DataFrame): Training data containing team features.

    Returns:
    - DataFrame: Features of the specified team.
    """

    return train_data.loc[train_data['Team_ID'] == team_id]


def prefix_columns(dataframe, prefix):
    """
    Add a prefix to all columns in a dataframe with an exception for 'Team_ID'.

    Args:
    - dataframe (DataFrame): Input dataframe.
    - prefix (str): Prefix to add to columns.

    Returns:
    - DataFrame: DataFrame with updated column names.
    """

    dataframe.columns = [prefix + col if col !=
                         'Team_ID' else col for col in dataframe.columns]
    return dataframe
