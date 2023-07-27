from datetime import timedelta
import os
import json
import requests
import pandas as pd
import base64
import pytz
from datetime import datetime, timedelta
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv

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


def fetch_data_from_api():
    # Fetch game data from The Odds API
    load_dotenv()
    api_data = os.getenv("API_LINK")
    response = requests.get(api_data)

    if response.status_code != 200:
        raise Exception("Failed to fetch data from API")

    return json.loads(response.text)


def get_games_playing_today(api_data, team_to_id):
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


def load_and_preprocess_data(api_data, games_playing_today_ids):
    # Load the CSV data
    batting_data = pd.read_csv("data/2023_MLB_Batting_Data.csv")
    pitching_data = pd.read_csv("data/2023_MLB_Pitching_Data.csv")
    standings_data = pd.read_csv("data/2023_MLB_Standings_Data.csv")

    # Function to convert win-loss records into win percentages
    def win_loss_to_percentage(x):
        win, loss = map(float, x.split('-'))
        return win / (win + loss) if win + loss > 0 else 0

    # Convert win-loss records into win percentages
    for col in ['≥.500', '<.500']:
        standings_data[col] = standings_data[col].apply(win_loss_to_percentage)

    # Merge the batting, pitching and standings data on 'Team_ID'
    mlb_data = pd.merge(batting_data, pitching_data, on=['Team_ID'])
    mlb_data = pd.merge(mlb_data, standings_data, on=['Team_ID'])

    # Check if the CSV data is not empty
    if mlb_data.empty:
        raise Exception("The CSV data is empty.")

    # Filter the mlb_data DataFrame to only include rows where the team ID is in games_playing_today_ids
    mlb_data_today = mlb_data[mlb_data['Team_ID'].isin(
        games_playing_today_ids)]

    # Check if the filtered DataFrame is not empty
    if mlb_data_today.empty:
        raise Exception("The filtered DataFrame is empty.")

    # Split the data into training and testing sets
    train_data, test_data = train_test_split(mlb_data_today, test_size=0.2)

    return train_data, test_data

def train_and_test_model(train_data, test_data):
    # Prepare the training data
    features = ["xBA", "xSLG", "xwOBA", "RA/G", "ERA", "WHIP", "SO9",
                "W-L%", "Win/Loss%", "Rdiff", "SOS", "SRS", "Luck", "≥.500", "<.500"]
    X_train = train_data[features]
    y_train = train_data["R/G"]

    # Prepare the testing data
    X_test = test_data[features]
    y_test = test_data["R/G"]

    # Create and train the model
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    # Evaluate the model
    y_pred = model.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)

    return model, mae, mse, r2, X_test


def get_recommendation(bookmakers, model, train_data, team_to_id):
    h2h_recommendations = []
    features = ["xBA", "xSLG", "xwOBA", "RA/G", "ERA", "WHIP", "SO9",
                "W-L%", "Win/Loss%", "Rdiff", "SOS", "SRS", "Luck", "≥.500", "<.500"]

    for bookmaker in bookmakers:
        for market in bookmaker["markets"]:
            if market["key"] == "h2h":
                for outcome in market["outcomes"]:
                    team_name = outcome['name']
                    team_id = team_to_id.get(team_name, -1)
                    if team_id != -1:  # Only proceed if team ID is valid
                        team_features = train_data.loc[train_data['Team_ID'] == team_id]
                        if not team_features.empty:
                            predicted_value = model.predict(
                                team_features[features])[0]

                            h2h_recommendations.append({
                                "team": team_name,  # Use team name here for human-readable output
                                "price": outcome["price"],
                                "bookmaker": bookmaker["title"],
                                "predicted_value": predicted_value,
                            })
                    else:
                        print(
                            f"Skipping team {team_name} because no ID could be found for it")

    if not h2h_recommendations:
        return None  # Return None instead of an error dictionary

    sorted_recommendations = sorted(
        h2h_recommendations, key=lambda x: x["predicted_value"], reverse=True)

    return sorted_recommendations


def parse_data(api_data, model, train_data, team_to_id):
    current_date = datetime.utcnow().date()  # Get today's date in UTC
    games = []
    for game in api_data:
        commence_time = datetime.strptime(
            game['commence_time'], '%Y-%m-%dT%H:%M:%SZ')
        commence_date_utc = commence_time.date()

        # Skip the game if its commence date in UTC is not today
        if commence_date_utc != current_date:
            continue

        home_team_id = team_to_id.get(game['home_team'], None)
        away_team_id = team_to_id.get(game['away_team'], None)
        if home_team_id is None or away_team_id is None:
            continue  # Skip if team ID is not found

        if home_team_id in games_playing_today_ids or away_team_id in games_playing_today_ids:
            try:
                bookmakers = game['bookmakers']

                # Generate recommendations for all bookmakers
                all_recommendations = get_recommendation(
                    bookmakers, model, train_data, team_to_id)

                # Select the top recommendation from all
                recommendations = []
                if all_recommendations:
                    recommendations.append(
                        max(all_recommendations, key=lambda x: x['predicted_value']))
                    print(recommendations)

                if not recommendations:  # Skip this game if no recommendation could be generated
                    continue

                games.append({
                    'home_team': game['home_team'],
                    'away_team': game['away_team'],
                    'commence_time': game['commence_time'],
                    'bookmakers': bookmakers,
                    'recommendation': recommendations,
                })
            except Exception as e:
                print(e)
                continue

    return games

def create_email_template(games):
    email_body = f"""
    <html>
    <head>
        <style>
            body {{
                font-family: Arial, sans-serif;
                background-color: #f6f6f6;
                padding: 20px;
            }}
            h1 {{
                text-align: center;
                color: #222;
            }}
            .date {{
                text-align: center;
                font-size: 18px;
                color: #555;
                margin-bottom: 20px;
            }}
            .game {{
                background-color: #fff;
                border-radius: 5px;
                padding: 20px;
                margin-bottom: 20px;
            }}
            h2 {{
                margin-top: 0;
                font-size: 22px;
                color: #333;
            }}
            .start-time {{
                font-size: 16px;
                color: #777;
                margin-bottom: 10px;
            }}
            .recommendation {{
                font-size: 18px;
                color: #444;
            }}
        </style>
    </head>
    <body>
        <h1>MLB Betting Lines</h1>
        <div class="date">{datetime.now().strftime('%B %d, %Y')}</div>
    """

    for game in games:
        commence_time = datetime.strptime(
            game['commence_time'], '%Y-%m-%dT%H:%M:%SZ')
        commence_time = commence_time.replace(tzinfo=pytz.utc).astimezone(
            pytz.timezone('America/New_York'))  # Convert to EST/EDT
        # Format time to human-readable here
        commence_time = commence_time.strftime('%B %d, %Y at %I:%M%p EST')
        email_body += f"""
        <div class="game">
            <h2>{game['home_team']} vs {game['away_team']}</h2>
            <div class="start-time">Start time: {commence_time}</div>
        """
        for rec in game['recommendation']:
            email_body += f"""
            <div class="recommendation">Recommendation: <span style="color: green;">{rec['team']} ({rec['price']})</span> at <span style="color: red;">{rec['bookmaker']}</span></div>
            """
        email_body += "</div>"
    return email_body


def send_email(games, mae, mse, r2, email_body):
    # Send email with game predictions and model evaluation metrics
    creds = get_credentials()
    service = build('gmail', 'v1', credentials=creds)

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"MLB Moneyline Predictions for {datetime.now().strftime('%B %d, %Y')}"
    msg["From"] = bet_email = os.getenv("BET_EMAIL")
    msg["To"] = "callmevojtko@yahoo.com"  # Replace with your email address

    # Added model evaluation metrics to the email body
    email_body += f"""
    <h2>Model Evaluation Metrics</h2>
    <p>Mean Absolute Error: {mae}</p>
    <p>Mean Squared Error: {mse}</p>
    <p>R-squared Score: {r2}</p>
    """

    # Create the email body with predictions and evaluation metrics
    msg.attach(MIMEText(email_body, "html"))

    create_message = {'raw': base64.urlsafe_b64encode(msg.as_bytes()).decode()}
    send_message = (service.users().messages().send(
        userId="me", body=create_message).execute())
    print(F'Sent message to {msg["To"]} Message Id: {send_message["id"]}')


def get_credentials():
    # Load and refresh the Google OAuth2 credentials
    creds = None
    if os.path.exists("data/token.json"):
        creds = Credentials.from_authorized_user_file("data/token.json")

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "data/credentials.json", [
                    "https://www.googleapis.com/auth/gmail.send"]
            )
            creds = flow.run_local_server(port=0)
        with open("data/token.json", "w") as token:
            token.write(creds.to_json())

    return creds


if __name__ == "__main__":
    try:
        print("Fetching data from API...")
        api_data = fetch_data_from_api()
        print("Getting today's games...")
        games_playing_today_ids = get_games_playing_today(api_data, team_to_id)
        print("Loading and preprocessing data...")
        train_data, test_data = load_and_preprocess_data(
            api_data, games_playing_today_ids)
        print("Training and testing the model...")
        model, mae, mse, r2, X_test = train_and_test_model(
            train_data, test_data)
        print("Parsing data...")
        games = parse_data(api_data, model, train_data, team_to_id)
        print("Creating email template...")
        email_body = create_email_template(games)
        print("Sending email...")
        send_email(games, mae, mse, r2, email_body)
        print("Done!")

        # Save the games data as a JSON file
        with open('data/data.json', 'w') as f:
            json.dump(games, f, default=str)

    except Exception as e:
        print(f"An error occurred: {str(e)}")
