"""
recommendation.py
-----------------

This module contains functions related to generating betting recommendations based on the trained model's predictions.

Functions:
- expected_value: Calculate the expected value of a bet.
- get_best_odds_for_team: Find the best odds for a given team across multiple bookmakers.
- get_recommendation_for_game: Generate recommendation for a single game.
- format_output: Format the recommendation for better terminal output.

Imports:
- External libraries: modules.data_processing, modules.constants
"""

from modules.data_processing import fetch_team_features
from modules.constants import features


def expected_value(odds, predicted_win_pct):
    """
    Calculate the expected value of a bet.

    Args:
    - odds (float): Betting odds.
    - predicted_win_pct (float): Predicted win percentage of the team.

    Returns:
    - float: Expected value of the bet.
    """

    if odds > 0:
        return (odds / 100) * predicted_win_pct - (1 - predicted_win_pct)
    else:
        return (100 / abs(odds)) * predicted_win_pct - (1 - predicted_win_pct)


def get_best_odds_for_team(team_name, bookmakers):
    """
    Find the best odds for a given team across multiple bookmakers.

    Args:
    - team_name (str): Name of the team.
    - bookmakers (list): List of bookmakers and their odds.

    Returns:
    - tuple: Contains the best odds and the corresponding bookmaker for the given team.
    """

    best_odds = None
    best_bookmaker = None

    for bookmaker in bookmakers:
        for market in bookmaker["markets"]:
            if market["key"] == "h2h":
                for outcome in market["outcomes"]:
                    if outcome["name"] == team_name:
                        if best_odds is None or (outcome["price"] > 0 and outcome["price"] > best_odds) or (outcome["price"] < 0 and abs(outcome["price"]) < abs(best_odds)):
                            best_odds = outcome["price"]
                            best_bookmaker = bookmaker["title"]

    return best_odds, best_bookmaker


def get_recommendation_for_game(game, model, train_data, team_to_id):
    """
    Generate recommendation for a single game.

    Args:
    - game (dict): Information about the game.
    - model (RandomForestRegressor): The trained model.
    - train_data (DataFrame): Training data.
    - team_to_id (dict): Dictionary mapping team names to team IDs.

    Returns:
    - dict: Contains the recommendation details.
    """

    home_team_name = game['home_team']
    away_team_name = game['away_team']

    home_team_id = team_to_id.get(home_team_name, None)
    away_team_id = team_to_id.get(away_team_name, None)

    if home_team_id is None or away_team_id is None:
        return None

    home_team_features = fetch_team_features(home_team_id, train_data)
    away_team_features = fetch_team_features(away_team_id, train_data)

    if home_team_features.empty or away_team_features.empty:
        return None

    home_team_predicted_win_pct = model.predict(
        home_team_features[features])[0]
    away_team_predicted_win_pct = model.predict(
        away_team_features[features])[0]

    if home_team_predicted_win_pct > away_team_predicted_win_pct:
        recommended_team = home_team_name
        predicted_win_pct = home_team_predicted_win_pct
    else:
        recommended_team = away_team_name
        predicted_win_pct = away_team_predicted_win_pct

    best_odds, best_bookmaker = get_best_odds_for_team(
        recommended_team, game['bookmakers'])
    ev = expected_value(best_odds, predicted_win_pct)

    return {
        "team": recommended_team,
        "price": best_odds,
        "bookmaker": best_bookmaker,
        "predicted_win_pct": predicted_win_pct,
        "expected_profit": predicted_win_pct * best_odds,
        "expected_value": ev
    }


def format_output(recommendation):
    """
    Format the recommendation for better terminal output.

    Args:
    - recommendation (dict): Recommendation details.

    Returns:
    - str: Formatted recommendation output.
    """

    team = recommendation.get('team', 'N/A')
    price = recommendation.get('price', 'N/A')
    bookmaker = recommendation.get('bookmaker', 'N/A')
    predicted_win_pct = recommendation.get('predicted_win_pct', 'N/A')
    expected_profit = recommendation.get('expected_profit', 'N/A')

    return (
        f"Team: {team}\n"
        f"Bookmaker: {bookmaker}\n"
        f"Price: {price}\n"
        f"Predicted Win Percentage: {predicted_win_pct * 100:.2f}%\n"
        f"Expected Profit: ${expected_profit:.2f} for every $100 bet\n"
        "-----------------------------------------\n"
    )
