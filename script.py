import os
import json
import requests
import pandas as pd
import base64
import pytz
from datetime import datetime
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


def fetch_data_from_api():
    # Fetch game data from The Odds API
    load_dotenv()
    api_data = os.getenv("API_LINK")
    response = requests.get(api_data)
    
    if response.status_code != 200:
        raise Exception("Failed to fetch data from API")
    
    return json.loads(response.text)

def get_teams_playing_today(api_data):
    teams_playing_today = set()
    for game in api_data:
        game_time = datetime.strptime(
            game['commence_time'], '%Y-%m-%dT%H:%M:%SZ')
        if game_time.date() == datetime.today().date():
            teams_playing_today.add(game['home_team'])
            teams_playing_today.add(game['away_team'])
    return teams_playing_today

def load_and_preprocess_data(api_data, teams_playing_today):
    # Load the CSV data
    mlb_data = pd.read_csv("data/2023_MLB_Data.csv")
    
    # Check if the CSV data is not empty
    if mlb_data.empty:
        raise Exception("The CSV data is empty.")
    
    # Create dictionary that maps team names to team ID's
    team_to_id = {
        "Arizona Diamondbacks": 1,
        "Atlanta Braves": 2,
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

    # Get the IDs of the teams playing today
    teams_playing_today_ids = {team_to_id[team] for team in teams_playing_today}
    
    # Check if there are teams playing today
    if not teams_playing_today_ids:
        raise Exception("There are no games scheduled for today.")

    # Filter the mlb_data DataFrame to only include rows where the team ID is in teams_playing_today_ids
    mlb_data = mlb_data[mlb_data['Team_ID'].isin(teams_playing_today_ids)]
    
    # Check if the filtered DataFrame is not empty
    if mlb_data.empty:
        raise Exception("The filtered DataFrame is empty.")

    # Split the data into training and testing sets
    train_data, test_data = train_test_split(mlb_data, test_size=0.2)

    return train_data, test_data, team_to_id


def train_and_test_model(train_data, test_data):
    # Prepare the training data
    X_train = train_data.drop("R/G", axis=1)
    y_train = train_data["R/G"]

    # Prepare the testing data
    X_test = test_data.drop("R/G", axis=1)
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
    spreads = []
    for bookmaker in bookmakers:
        for market in bookmaker["markets"]:
            if market["key"] == "spreads":
                for outcome in market["outcomes"]:
                    team_name = outcome['name']
                    team_id = team_to_id.get(team_name, -1)
                    if team_id != -1:  # Only proceed if team ID is valid
                        team_features = train_data.loc[train_data['Team_ID'] == team_id]
                        if not team_features.empty:
                            predicted_rg_value = model.predict(
                                team_features.drop("R/G", axis=1))[0]

                            spreads.append({
                                "team": team_name,  # Use team name here for human-readable output
                                "price": outcome["price"],
                                "point": outcome["point"],
                                "bookmaker": bookmaker["title"],
                                "predicted_rg": predicted_rg_value,
                            })
                    else:
                        print(
                            f"Skipping team {team_name} because no ID could be found for it")

    if not spreads:
        return None  # Return None instead of an error dictionary

    sorted_spreads = sorted(
        spreads, key=lambda x: (x["predicted_rg"], -x["price"]), reverse=True)

    return sorted_spreads


def parse_data(mlb_data, model, train_data, team_to_id, teams_playing_today):
    games = []
    for game in mlb_data:
        try:
            home_team = game['home_team']
            away_team = game['away_team']
            commence_time = datetime.fromisoformat(
                game['commence_time'].replace("Z", ""))
            bookmakers = game['bookmakers']

            # Skip the game if neither team is playing today
            if home_team not in teams_playing_today and away_team not in teams_playing_today:
                continue

            # Only get recommendations for teams that are playing today
            if home_team in teams_playing_today or away_team in teams_playing_today:
                # Generate recommendations for all bookmakers
                all_recommendations = get_recommendation(
                    bookmakers, model, train_data, team_to_id)

                # Select the top recommendation from all
                recommendation = []
                if all_recommendations:
                    recommendation.append(
                        max(all_recommendations, key=lambda x: x['predicted_rg']))

                if not recommendation:  # Skip this game if no recommendation could be generated
                    continue

            games.append({
                'home_team': home_team,
                'away_team': away_team,
                'commence_time': commence_time,
                'bookmakers': bookmakers,
                'recommendation': recommendation,
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
        commence_time = game['commence_time'].strftime('%H:%M')  # Format time
        email_body += f"""
        <div class="game">
            <h2>{game['home_team']} vs {game['away_team']}</h2>
            <div class="start-time">Start time: {commence_time} Local Time</div>
        """
        for rec in game['recommendation']:
            email_body += f"""
            <div class="recommendation">Recommendation: <span style="color: green;">{rec['team']} ({rec['point']}/{rec['price']})</span> at <span style="color: red;">{rec['bookmaker']}</span></div>
            """
        email_body += "</div>"
    return email_body

def send_email(games, mae, mse, r2, email_body):
    # Send email with game predictions and model evaluation metrics
    creds = get_credentials()
    service = build('gmail', 'v1', credentials=creds)

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"MLB Game Predictions for {datetime.now().strftime('%B %d, %Y')}"
    msg["From"] = bet_email = os.getenv("BET_EMAIL")
    msg["To"] = "" # Replace with your email address

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
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json")

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", [
                    "https://www.googleapis.com/auth/gmail.send"]
            )
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    return creds

if __name__ == "__main__":
    try:
        print("Fetching data from API...")
        api_data = fetch_data_from_api()
        print("Getting today's games...")
        teams_playing_today = get_teams_playing_today(api_data)
        print("Loading and preprocessing data...")
        train_data, test_data, team_to_id = load_and_preprocess_data(api_data, teams_playing_today)
        print("Training and testing the model...")
        model, mae, mse, r2, X_test = train_and_test_model(train_data, test_data)
        print("Parsing data...")
        games = parse_data(api_data, model, train_data, team_to_id, teams_playing_today)
        print("Creating email template...")
        email_body = create_email_template(games)
        print("Sending email...")
        send_email(games, mae, mse, r2, email_body)
        print("Done!")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
