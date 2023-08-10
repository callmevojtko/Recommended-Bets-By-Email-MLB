# MLB Betting Recommendation Emailer

This advanced machine learning model utilizes a Random Forest Regressor to generate betting recommendations for Major League Baseball (MLB) games. 
By leveraging aggregated data from reputed sportsbooks such as Fanduel, DraftKings, and Barstool via The Odds API, and combining it with the team's performance metrics from the 2023 season, 
the model provides insightful betting line recommendations.

## Features

Data Aggregation: Fetches game data from The Odds API, which includes the latest betting lines from renowned sportsbooks.

Machine Learning Model: Utilizes a Random Forest Regressor to make predictions based on team performance metrics pulled from pybaseball.

Email Notifications: Sends betting recommendations via email, using a well-formatted HTML template.

Comprehensive Analysis: Considers various key performance metrics such as Runs, Hits, Runs per Game, On-base Plus Slugging, and more.

Modular Structure: The codebase is organized into modules for data fetching, processing, model training, and email utilities, making it easy to understand and extend.

## Example Email

<img width="400" alt="Screenshot 2023-08-10 at 1 37 43 PM" src="https://github.com/callmevojtko/Recommended-Bets-By-Email-MLB/assets/43586291/69296959-8a0d-48f1-bd56-8f04f6f77580">


## Technologies Used
- Python
- Pandas
- Scikit-learn
- [pybaseball](https://github.com/jldbc/pybaseball)
- Gmail API
- [The Odds API](https://the-odds-api.com/) 
- HTML & CSS

## How to Use
1. API Setup: Create a free account with [The Odds API](https://the-odds-api.com/) to obtain an API key. Store this key in a `.env` file as `API_KEY=<apiKey>`.
   - Please see the Odds API docs for more info [here](https://the-odds-api.com/liveapi/guides/v4/)

2. Gmail API Setup: Obtain credentials for the Gmail API and store them in a `credentials.json` file in the data directory. Then run `modules/quickstart.py` to generate a `token.json` file.
   - Read more on setting up the Gmail API with Python [here](https://developers.google.com/gmail/api/quickstart/python)

3. Environment Variables: In your `.env` file, specify the email that is authorized with the Gmail API as `BET_EMAIL` and the recipient's email as `RECIPENT_EMAIL`.

4. Execution: Run the `app.py` script. This will fetch the betting lines, train the model, generate recommendations, and send an email with the betting recommendations to the specified recipient.

## Contribute
Everyone is welcome to contribute to this project! Feel free to add new features, fix bugs, or make improvements. Just fork the repository, make your changes, and submit a pull request. I appreciate your help! :)

## Disclaimer
This project is intended for educational purposes only. It should not be used as the sole basis for actual betting decisions. Betting involves risk, and you should only bet with money you can afford to lose. Always bet responsibly.
