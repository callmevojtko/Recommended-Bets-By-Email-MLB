"""
constants.py
------------

This module contains various constants used throughout the application. These constants include parameters for
model training, mappings of team names to their respective IDs, and features used in the model.

Variables:
- param_grid: Dictionary containing hyperparameters for grid search.
- team_to_id: Dictionary mapping team names to their respective IDs.
- team_names_only: Dictionary mapping shortened team names (from fielding data) to their respective IDs.
- team_abbrev_to_id: Dictionary mapping team abbreviations to their respective IDs.
- features: List of feature names used in the model.
"""

# Hyperparameters for RandomForestRegressor grid search
param_grid = {
    'n_estimators': [100, 200, 500],
    'max_features': ['sqrt', 'log2'],
    'max_depth': [30, 50, 70, None],
    'min_samples_split': [2, 5, 10, 15],
    'min_samples_leaf': [1, 2, 5],
    'bootstrap': [True, False]
}

# Create dictionary that maps team names to team ID's
team_to_id = {
    "Atlanta Braves": 1,
    "Arizona Diamondbacks": 2,
    "Baltimore Orioles": 3,
    "Boston Red Sox": 4,
    "Chicago Cubs": 5,
    "Chicago White Sox": 6,
    "Cincinnati Reds": 7,
    "Cleveland Guardians": 8,
    "Colorado Rockies": 9,
    "Detroit Tigers": 10,
    "Houston Astros": 11,
    "Kansas City Royals": 12,
    "Los Angeles Angels": 13,
    "Los Angeles Dodgers": 14,
    "Miami Marlins": 15,
    "Milwaukee Brewers": 16,
    "Minnesota Twins": 17,
    "New York Mets": 18,
    "New York Yankees": 19,
    "Oakland Athletics": 20,
    "Philadelphia Phillies": 21,
    "Pittsburgh Pirates": 22,
    "San Diego Padres": 23,
    "Seattle Mariners": 24,
    "San Francisco Giants": 25,
    "St. Louis Cardinals": 26,
    "Tampa Bay Rays": 27,
    "Texas Rangers": 28,
    "Toronto Blue Jays": 29,
    "Washington Nationals": 30
}

# Creating a dictionary with just the team names for fielding data
team_names_only = {
    "Braves": 1,
    "Diamondbacks": 2,
    "Orioles": 3,
    "Red Sox": 4,
    "Cubs": 5,
    "White Sox": 6,
    "Reds": 7,
    "Guardians": 8,
    "Rockies": 9,
    "Tigers": 10,
    "Astros": 11,
    "Royals": 12,
    "Angels": 13,
    "Dodgers": 14,
    "Marlins": 15,
    "Brewers": 16,
    "Twins": 17,
    "Mets": 18,
    "Yankees": 19,
    "Athletics": 20,
    "Phillies": 21,
    "Pirates": 22,
    "Padres": 23,
    "Mariners": 24,
    "Giants": 25,
    "Cardinals": 26,
    "Rays": 27,
    "Rangers": 28,
    "Blue Jays": 29,
    "Nationals": 30
}

# Create a dictionary that maps team abbreviations to team IDs
team_abbrev_to_id = {
    "ATL": 1,
    "ARI": 2,
    "BAL": 3,
    "BOS": 4,
    "CHC": 5,
    "CHW": 6,
    "CIN": 7,
    "CLE": 8,
    "COL": 9,
    "DET": 10,
    "HOU": 11,
    "KCR": 12,
    "LAA": 13,
    "LAD": 14,
    "MIA": 15,
    "MIL": 16,
    "MIN": 17,
    "NYM": 18,
    "NYY": 19,
    "OAK": 20,
    "PHI": 21,
    "PIT": 22,
    "SDP": 23,
    "SEA": 24,
    "SFG": 25,
    "STL": 26,
    "TBR": 27,
    "TEX": 28,
    "TOR": 29,
    "WSN": 30
}

# Features list used for training and predicting with the model
features = [
    # Batting
    "bat_G", "bat_AB", "bat_PA", "bat_H", "bat_1B", "bat_2B",
    "bat_3B", "bat_HR", "bat_R", "bat_RBI", "bat_BB", "bat_SO",
    "bat_AVG", "bat_wOBA", "bat_wRAA", "bat_wRC", "bat_WAR",
    "bat_OBP", "bat_SLG", "bat_ISO", "bat_Clutch", "bat_Swing%",
    "bat_Contact%", "bat_Zone%", "bat_F-Strike%", "bat_Pull%",

    # Pitching
    "pit_W", "pit_L", "pit_ERA", "pit_G", "pit_GS", "pit_SV",
    "pit_IP", "pit_H", "pit_R", "pit_ER", "pit_HR", "pit_BB",
    "pit_SO", "pit_WHIP", "pit_FIP", "pit_xFIP", "pit_WAR",
    "pit_K/BB",

    # Fielding
    "field_G", "field_GS", "field_Inn", "field_PO", "field_A",
    "field_E", "field_DP", "field_DRS", "field_UZR",

    # Standings
    "stand_W", "stand_L", "stand_W-L%"
]
