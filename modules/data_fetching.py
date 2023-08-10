"""
data_fetching.py
----------------

This module provides functions for fetching data required for the MLB betting application.
It uses both The Odds API and the pybaseball library to retrieve game data and statistics for MLB teams.

Functions:
- fetch_data_from_api: Fetch game data from The Odds API.
- fetch_data_from_pybaseball: Fetch MLB statistics for teams using the pybaseball library.

Constants:
- year: Represents the year for which the data is fetched.

Imports:
- Standard libraries: os, requests, json, pandas
- External libraries: dotenv, pybaseball
- Local modules: constants
"""

import os
import requests
import json
import pandas as pd
from dotenv import load_dotenv
from pybaseball import team_batting, team_pitching, team_fielding, standings
from modules.constants import team_to_id, team_names_only, team_abbrev_to_id

year = 2023


def fetch_data_from_api():
    """
    Fetch game data from The Odds API.

    This function reads the API link from the environment, fetches data, and returns it in JSON format.

    Returns:
    - Dictionary: JSON formatted data fetched from the API.
    """
    load_dotenv()
    api_data = os.getenv("API_LINK")
    response = requests.get(api_data)

    if response.status_code != 200:
        raise Exception("Failed to fetch data from API")

    return json.loads(response.text)


def fetch_data_from_pybaseball(year):
    """
    Fetch MLB statistics for teams using the pybaseball library.

    This function fetches team statistics for batting, pitching, fielding, and standings.
    It then maps the team names/abbreviations to team IDs, reorders the columns, and saves the data to CSV files.

    Args:
    - year (int): The year for which to fetch the data.

    Returns:
    - Tuple: Four DataFrames containing batting, pitching, fielding, and standings data.
    """
    batting_data = team_batting(year)
    pitching_data = team_pitching(year)
    fielding_data = team_fielding(year)
    standings_data_list = standings(year)

    # Concatenate the list of DataFrames to form a single DataFrame
    standings_data = pd.concat(standings_data_list, ignore_index=True)

    # Map 'Tm' column to 'Team_ID' using the team_to_id dictionary
    standings_data['Team_ID'] = standings_data['Tm'].map(team_to_id)

    # Map team abbreviations to team IDs
    batting_data["Team_ID"] = batting_data["Team"].map(team_abbrev_to_id)
    pitching_data["Team_ID"] = pitching_data["Team"].map(team_abbrev_to_id)
    fielding_data["Team_ID"] = fielding_data["Team"].map(team_names_only)
    standings_data["Team_ID"] = standings_data["Tm"].map(team_to_id)

    # Reorder columns to have 'Team_ID' as the first column
    for df in [batting_data, pitching_data, fielding_data, standings_data]:
        cols = list(df.columns)
        cols.insert(0, cols.pop(cols.index('Team_ID')))
        df = df[cols]

    # Save data to CSV files
    batting_data.to_csv('/data/batting_data.csv', index=False)
    pitching_data.to_csv('/data/pitching_data.csv', index=False)
    fielding_data.to_csv('/data/fielding_data.csv', index=False)
    standings_data.to_csv('/data/standings_data.csv', index=False)

    return batting_data, pitching_data, fielding_data, standings_data
