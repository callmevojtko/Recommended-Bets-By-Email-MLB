"""
email_utils.py
--------------

This module contains utility functions related to email handling for the MLB betting application.

Functions:
- url_to_base64: Convert a PNG image from a URL into a base64 encoded string.
- create_email_template: Construct an email template with the provided game details.
- send_email: Send an email with the game predictions and model evaluation metrics.
- get_credentials: Load and refresh the Google OAuth2 credentials.

Notes:
- Ensure your Gmail API is authorized to send emails from your account from the cloud console.
- Run 'quickstart.py' to generate a token in data/token.json.
- If you get an error about the 'token.json' file not existing, delete the old token.json and run 'quickstart.py' again.

Imports:
- Standard libraries: datetime, os, base64, requests
- External libraries: googleapiclient, google_auth_oauthlib, google.oauth2, email, pytz
"""

# Imports
from datetime import datetime
import os
import base64
import requests
from io import BytesIO
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import pytz


def url_to_base64(url):
    """
    Convert a PNG image from a URL into a base64 encoded string.

    Args:
    - url (str): URL of the PNG image.

    Returns:
    - str: Base64 encoded representation of the PNG image.
    """

    response = requests.get(url)
    image_data = BytesIO(response.content)
    base64_encoded = base64.b64encode(image_data.read()).decode('utf-8')
    return base64_encoded


def create_email_template(games):
    """
    Construct an email template with the provided game details.

    Args:
    - games (list): List of games with details.

    Returns:
    - str: HTML content for the email.
    """

    email_body = f"""
    <html>
    <head>
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background-color: #f6f6f6;
                padding: 20px;
                margin: 0;
            }}
            .container {{
                max-width: 600px;
                margin: auto;
                background-color: #fff;
                border-radius: 10px;
                overflow: hidden;
                box-shadow: 0 0 15px rgba(0, 0, 0, 0.1);
            }}
            .header {{
                background-color: #2E7D32;
                color: #fff;
                padding: 20px;
                text-align: center;
                font-size: 28px;
                border-bottom: 3px solid #1B5E20;
            }}
            .date {{
                text-align: center;
                font-size: 18px;
                color: #2E7D32;
                padding: 10px;
                background-color: #E8F5E9;
            }}
            .game {{
                padding: 20px;
                border-bottom: 1px solid #ECEFF1;
            }}
            .game:last-child {{
                border-bottom: 0;
            }}
            h2 {{
                margin-top: 0;
                font-size: 22px;
                color: #333;
                border-bottom: 1px solid #ECEFF1;
                padding-bottom: 10px;
            }}
            .start-time {{
                font-size: 16px;
                color: #555;
                margin-bottom: 15px;
                font-style: italic;
            }}
            .recommendation {{
                font-size: 18px;
                color: #008000;  /* Green color for recommendation */
                margin-bottom: 15px;
            }}
            .recommendation strong {{
                color: #333;
                font-weight: bold;
            }}
            .bookmaker-icon {{
                height: 25px;
                width: 25px;
                vertical-align: middle;
                margin-right: 5px;
            }}
            .bookmaker-label {{
                font-size: 18px;
            }}
            .bookmaker-draftkings .bookmaker-label {{
                color: #008000;  /* Green color for DraftKings */
            }}
            .bookmaker-fanduel .bookmaker-label {{
                color: #0000FF;  /* Blue color for FanDuel */
            }}
            .bookmaker-barstool .bookmaker-label {{
                color: #FF0000;  /* Red color for Barstool Sportsbook */
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">MLB Betting Lines</div>
            <div class="date">{datetime.now().strftime('%B %d, %Y')}</div>
    """

    bookmaker_classes = {
        "FanDuel": "bookmaker-fanduel",
        "DraftKings": "bookmaker-draftkings",
        "Barstool Sportsbook": "bookmaker-barstool"
    }

    bookmaker_icon_urls = {
        "FanDuel": "https://s3.amazonaws.com/rical-misc/FanDuel-vertical-logo.png",
        "DraftKings": "https://companieslogo.com/img/orig/DKNG-e9ded183.png?t=1660587881",
        "Barstool Sportsbook": "https://www.pinclipart.com/picdir/big/36-361767_chicago-transparent-barstool-sports-clip-art-royalty-barstool.png",
    }

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
        rec = game.get('recommendation')
        if rec and isinstance(rec, dict):
            bookmaker_name = rec.get('bookmaker', "")
            bookmaker_class = bookmaker_classes.get(bookmaker_name, "")
            bookmaker_icon_data = url_to_base64(
                bookmaker_icon_urls.get(bookmaker_name, ""))
            email_body += f"""
            <div class="recommendation">
                Recommendation: <strong>{rec.get('team', 'N/A')} ({rec.get('price', 'N/A')}) at </strong>
                <img src="data:image/png;base64,{bookmaker_icon_data}" alt="{bookmaker_name} logo" width="50" height="50">
            </div>
            """
        email_body += "</div>"

    email_body += """
        </div>
    </body>
    </html>
    """
    return email_body


def send_email(mae, mse, r2, email_body):
    """
    Send an email with game predictions and model evaluation metrics.

    Args:
    - mae (float): Mean Absolute Error metric.
    - mse (float): Mean Squared Error metric.
    - r2 (float): R-squared Score metric.
    - email_body (str): Email body content.

    Returns:
    - None: Sends the email and prints a confirmation message.
    """

    creds = get_credentials()
    service = build('gmail', 'v1', credentials=creds)

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"MLB Moneyline Predictions for {datetime.now().strftime('%B %d, %Y')}"
    msg["From"] = os.getenv("BET_EMAIL")
    msg["To"] = os.getenv("RECIPENT_EMAIL")

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
    """
    Load and refresh the Google OAuth2 credentials.

    Args:
    - None

    Returns:
    - creds (Credentials): Loaded or refreshed Google OAuth2 credentials.
    """

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
