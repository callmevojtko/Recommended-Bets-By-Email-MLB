import os
import json
import requests
import pandas as pd
import base64
from datetime import datetime, timezone
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def fetch_data_from_api():
    url = "https://api.the-odds-api.com/v4/sports/baseball_mlb/odds/?regions=us&markets=spreads&bookmakers=fanduel,draftkings,barstool&oddsFormat=american&apiKey=87a80126977d66cf58a3c2053a7f3b73"
    response = requests.get(url)
    return json.loads(response.text)


def load_and_preprocess_data():
    data = pd.read_csv("2023_MLB_Data.csv")

    # One-hot encoding for the team names
    teams = data["Team"].unique()
    team_mapping = {team: [0]*len(teams) for team in teams}
    for i, team in enumerate(teams):
        team_mapping[team][i] = 1
    data["Team"] = data["Team"].map(team_mapping)

    train_data, test_data = train_test_split(
        data, test_size=0.2, random_state=42)
    return train_data, test_data, team_mapping

def train_and_test_model(train_data, test_data):
    # Train the model
    X_train = train_data.drop("R/G", axis=1)
    y_train = train_data["R/G"]

    model = LinearRegression()
    model.fit(X_train, y_train)

    # Test the model
    X_test = test_data.drop("R/G", axis=1)
    y_test = test_data["R/G"]

    y_pred = model.predict(X_test)

    # Calculate evaluation metrics
    mae = mean_absolute_error(y_test, y_pred)
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)

    print("Mean Absolute Error:", mae)
    print("Mean Squared Error:", mse)
    print("R-squared Score:", r2)

    return model, mae, mse, r2, X_test


def get_recommendation(bookmakers, model, X_test, train_data, team_mapping):
    team_names = []
    for bookmaker in bookmakers:
        for market in bookmaker["markets"]:
            if market["key"] == "spreads":
                for outcome in market["outcomes"]:
                    team_name = outcome['name']
                    if team_name in team_mapping:
                        team_names.append(team_mapping[team_name])
    team_data = train_data[train_data[team_names].sum(axis=1) > 0]

    # Predict the R/G values for the teams in team_data
    predicted_rg = model.predict(team_data.drop("R/G", axis=1))

    # Concatenate all the team features into a single DataFrame
    team_features_list = []
    for team_name in team_names:
        team_features = train_data.loc[train_data[team_name] == 1]
        if not team_features.empty:
            team_features_list.append(team_features)
    if team_features_list:
        X_test = pd.concat([X_test] + team_features_list)

    spreads = []
    for bookmaker in bookmakers:
        for market in bookmaker["markets"]:
            if market["key"] == "spreads":
                for outcome in market["outcomes"]:
                    team_name = outcome['name']
                    if team_name in team_mapping:
                        team_features = team_data.loc[team_data[team_mapping[team_name]] == 1]
                        if not team_features.empty:
                            predicted_rg_value = model.predict(
                                team_features.drop("R/G", axis=1))[0]

                            spreads.append({
                                "team": outcome["name"],
                                "price": outcome["price"],
                                "point": outcome["point"],
                                "bookmaker": bookmaker["title"],
                                "predicted_rg": predicted_rg_value,
                            })

    if not spreads:
        return {"error": "No recommendations could be generated"}

    sorted_spreads = sorted(
        spreads, key=lambda x: x["predicted_rg"], reverse=True)
    best_spread = sorted_spreads[0]
    return best_spread


def parse_data(data, model, train_data, X_test, team_mapping):
    games = []
    for game in data:
        team1 = game['home_team']
        team2 = game['away_team']
        commence_time = game['commence_time']
        bookmakers = game['bookmakers']

        recommendation = get_recommendation(bookmakers, model, X_test, train_data, team_mapping)

        games.append({
            'team1': team1,
            'team2': team2,
            'commence_time': commence_time,
            'bookmakers': bookmakers,
            'recommendation': recommendation,
        })
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
        commence_time_formatted = commence_time.strftime('%m-%d-%Y')
        best_recommendation = game['recommendation']
        print(best_recommendation)
        email_body += f"""
        <div class="game">
            <h2>{game['team1']} vs {game['team2']}</h2>
            <div class="start-time">Start time: {commence_time_formatted}</div>
            <div class="recommendation">Recommendation: <span style="color: green;">{best_recommendation['team']} ({best_recommendation['point']}/{best_recommendation['price']})</span> at <span style="color: red;">{best_recommendation['bookmaker']}</span></div>
        </div>
        """

    email_body += "</body></html>"
    return email_body

def get_google_credentials():
    SCOPES = ['https://www.googleapis.com/auth/gmail.send']
    creds = None

    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)

        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    return creds


def send_email_with_gmail_api(email_body):
    creds = get_google_credentials()
    service = build('gmail', 'v1', credentials=creds)

    from_email = "briansbets216@gmail.com"
    to_email = "vojtko.brian@yahoo.com"
    subject = "Your Daily MLB Bets from Brian"

    message = MIMEMultipart()
    message['To'] = to_email
    message['Subject'] = subject
    message.attach(MIMEText(email_body, 'html'))

    create_message = {'raw': base64.urlsafe_b64encode(
        message.as_bytes()).decode()}
    send_message = (service.users().messages().send(
        userId="me", body=create_message).execute())
    print(F'sent message to {to_email} Message Id: {send_message["id"]}')


def main():
    print("Fetching data from API...")
    data = fetch_data_from_api()

    print("Loading and preprocessing data...")
    train_data, test_data, team_mapping = load_and_preprocess_data()
    print(train_data.dtypes)

    print("Training and testing the model...")
    model, mae, mse, r2, X_test = train_and_test_model(train_data, test_data)
    print("Mean Absolute Error:", mae)
    print("Mean Squared Error:", mse)
    print("R-squared Score:", r2)

    print("Parsing data...")
    games = parse_data(data, model, train_data, X_test, team_mapping)
    
    # Get the games for today
    print("Getting today's games...")
    todays_date = datetime.now(timezone.utc).date().isoformat()
    todays_games = [game for game in games if game['commence_time'].split('T')[0] == todays_date]

    # Create the email template
    print("Creating email template...")
    email_body = create_email_template(todays_games)

    print("Sending email...")
    send_email_with_gmail_api(email_body)

    print("Email sent.")

if __name__ == "__main__":
    main()
