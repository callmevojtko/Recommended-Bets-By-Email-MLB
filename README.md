# MLB Betting Recommendation Emailer
Using a Linear Regression method, this machine learning model generates a recommended spread bet. The Odds API is used by the model to gather data from well-known sportsbooks like Fanduel, DraftKings, and Barstool.

More specifically, the model takes into account a number of important performance measures that are representative of a team's previous success for the current 2023 season like:
> R: Runs,

> H: Hits,
  
> R/G: Runs per Game,
  
> OPS: On-base Plus Slugging,
  
  etc.
  
It can anticipate which spreads are most likely to succeed by contrasting these measurements with the most recent betting lines offered.
## Example Email

![Example](https://user-images.githubusercontent.com/43586291/235729092-86301d2e-3ccc-4912-9ad3-c3c22c88258b.png)

## Technologies Used
Python
Pandas
NumPy
Scikit-learn
HTML
CSS
Google APIs
The Odds API

## How to Use
To use the model, you will need to first create an account with The Odds API and obtain an API key. The API key is then passed as a parameter to the fetch_data_from_api() function in the code.

You will also need to obtain credentials for the Google APIs, specifically the Gmail API. These credentials should be stored in a credentials.json file in the project directory.

Once these prerequisites are met, you can simply run the main() function to fetch the betting lines, generate recommendations, and send an email containing the recommendations to a specified recipient.

## Disclaimer
Please note that this project is intended for educational purposes only, and should not be used as a basis for actual betting.
