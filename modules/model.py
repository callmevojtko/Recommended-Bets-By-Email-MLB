"""
model.py
--------

This module contains functions related to the training, testing, and application of the RandomForestRegressor model for MLB betting predictions.

Functions:
- train_and_test_model: Train the RandomForestRegressor model using grid search and test its performance.
- parse_data: Parse the API data, make predictions using the trained model, and get recommendations for betting.

Imports:
- Standard libraries: datetime
- External libraries: sklearn, eli5, modules.recommendation, modules.constants
"""

from datetime import datetime
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import eli5
from eli5.sklearn import PermutationImportance
from modules.recommendation import get_recommendation_for_game, format_output
from modules.constants import features, param_grid


def train_and_test_model(train_data, test_data):
    """
    Train the RandomForestRegressor model using grid search and test its performance.

    Args:
    - train_data (DataFrame): Training data.
    - test_data (DataFrame): Testing data.

    Returns:
    - tuple: Contains the trained model, MAE, MSE, R2, and test feature data.
    """

    # Convert the 'stand_W' and 'stand_L' columns to float type and then compute the Win-Loss Percentage (W-L%).
    train_data['stand_W'] = train_data['stand_W'].astype(float)
    train_data['stand_L'] = train_data['stand_L'].astype(float)
    train_data['W-L%'] = train_data['stand_W'] / \
        (train_data['stand_W'] + train_data['stand_L'])

    test_data['stand_W'] = test_data['stand_W'].astype(float)
    test_data['stand_L'] = test_data['stand_L'].astype(float)
    test_data['W-L%'] = test_data['stand_W'] / \
        (test_data['stand_W'] + test_data['stand_L'])

    # Prepare the training data
    X_train = train_data[features]
    y_train = train_data["W-L%"]

    # Prepare the testing data
    X_test = test_data[features]
    y_test = test_data["W-L%"]

    # Create the base model to tune
    rf = RandomForestRegressor(random_state=42)

    # Instantiate the grid search model
    grid_search = GridSearchCV(estimator=rf, param_grid=param_grid,
                               cv=3, n_jobs=-1, verbose=2, scoring='neg_mean_squared_error')

    # Fit the grid search to the data
    grid_search.fit(X_train, y_train)

    # Get the best model
    best_grid = grid_search.best_estimator_

    # Evaluate the best model
    y_pred = best_grid.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)

    perm = PermutationImportance(best_grid, random_state=1).fit(X_test, y_test)
    eli5.show_weights(perm, feature_names=X_test.columns.tolist())

    return best_grid, mae, mse, r2, X_test


def parse_data(api_data, model, train_data, team_to_id):
    """
    Parse the API data, make predictions using the trained model, and get recommendations for betting.

    Args:
    - api_data (list): Data fetched from the API.
    - model (RandomForestRegressor): The trained model.
    - train_data (DataFrame): Training data.
    - team_to_id (dict): Dictionary mapping team names to team IDs.

    Returns:
    - list: List of games with recommendations.
    """

    current_date = datetime.utcnow().date()  # Get today's date in UTC
    games = []

    for game in api_data:
        commence_time = datetime.strptime(
            game['commence_time'], '%Y-%m-%dT%H:%M:%SZ')
        commence_date_utc = commence_time.date()

        if commence_date_utc != current_date:
            continue

        recommendation = get_recommendation_for_game(
            game, model, train_data, team_to_id)
        if recommendation:
            print(format_output(recommendation))

            games.append({
                'home_team': game['home_team'],
                'away_team': game['away_team'],
                'commence_time': game['commence_time'],
                'recommendation': recommendation,
            })

    return games
