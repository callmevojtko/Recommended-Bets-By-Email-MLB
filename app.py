"""
app.py - MLB Betting Predictions Application
Author: Brian Vojtko
---------------------------------------------

Description:
This application is designed to provide MLB game betting predictions by leveraging data fetched from multiple sources,
including a proprietary API and the pybaseball module. The predictions are based on statistical models trained on 
historical MLB data, including batting, pitching, fielding, and standings metrics. 

Workflow:
1. Data Acquisition:
    - Fetches current game data from a proprietary API to identify games scheduled for today.
    - Retrieves historical baseball statistics from the pybaseball module for the current year.

2. Data Preprocessing:
    - Columns of the dataframes are prefixed to differentiate data types (e.g., batting, pitching).
    - Data is filtered to focus on the teams playing today.
    - The relevant features are selected for model training.

3. Model Training:
    - A Random Forest Regressor model is trained on the processed data.
    - The model is optimized using a grid search for hyperparameter tuning.

4. Predictions:
    - The trained model predicts the win percentages for the teams playing today.
    - Recommendations are generated based on the predicted win percentages and current betting odds.

5. Reporting:
    - Predictions are printed in the console in a human-readable format.
    - An email template is constructed with the predictions.
    - The email is sent to a predefined recipient with the predictions and model evaluation metrics.
    - The predictions are also saved in a JSON file for future reference.

Note:
    Exception handling mechanisms are in place to manage potential issues during the execution. 
    Detailed error messages will be printed to the console if any issues arise.
"""

# Standard library imports
import json
import pandas as pd

# Modules imports
from modules.constants import team_to_id
from modules.data_fetching import fetch_data_from_api, fetch_data_from_pybaseball, year
from modules.data_processing import get_games_playing_today, load_and_preprocess_data, prefix_columns
from modules.model import train_and_test_model, parse_data
from modules.recommendation import format_output
from modules.email_utils import create_email_template, send_email

# Main function
if __name__ == "__main__":
    try:
        # Fetch data from API
        print("Fetching data from API...")
        api_data = fetch_data_from_api()
        
        # Get today's games
        print("Getting today's games...")
        games_playing_today_ids = get_games_playing_today(api_data, team_to_id)

        # Fetch data from pybaseball
        print("Fetching data from pybaseball...")
        batting_data, pitching_data, fielding_data, standings_data = fetch_data_from_pybaseball(
            year)

        # Prefix the columns
        batting_data = prefix_columns(batting_data, 'bat_')
        pitching_data = prefix_columns(pitching_data, 'pit_')
        fielding_data = prefix_columns(fielding_data, 'field_')
        standings_data = prefix_columns(standings_data, 'stand_')

        # Load and preprocess the data
        print("Loading and preprocessing data...")
        train_data, test_data = load_and_preprocess_data(games_playing_today_ids, batting_data, pitching_data, fielding_data, standings_data)

        # Train and test the model
        print("Training and testing the model...")
        best_grid, mae, mse, r2, X_test = train_and_test_model(
            train_data, test_data)

        # Parse the data
        print("Parsing data...")
        games = parse_data(api_data, best_grid, train_data, team_to_id)

        # Print recommendations in a formatted manner
        for game in games:
            recommendation = game.get('recommendation')
            if recommendation:
                print(format_output(recommendation))

        # Create email template
        print("Creating email template...")
        email_body = create_email_template(games)

        # Send email
        print("Sending email...")
        send_email(mae, mse, r2, email_body)

        print("Done!")

        # Save the games data as a JSON file 'data.json'
        with open('data/data.json', 'w') as f:
            json.dump(games, f, default=str)

    # Handle exceptions
    except Exception as e:
        print(f"An error occurred: {str(e)}")
