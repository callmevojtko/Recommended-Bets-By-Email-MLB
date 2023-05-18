# MLB Betting Recommendation Emailer
Using a Linear Regression method, this machine learning model generates a recommended spread bet. The trustworthy The Odds API is used by the model to gather data from well-known sportsbooks like Fanduel, DraftKings, and Barstool.

The model considers several key performance metrics that reflect a team's past performance in the current 2023 season such as:
> R: Runs,

> H: Hits,
  
> R/G: Runs per Game,
  
> OPS: On-base Plus Slugging,
  
and more.

By comparing these metrics with the latest betting lines offered, the model can predict which spreads are most likely to be successful.

## Example Email

![Example](https://user-images.githubusercontent.com/43586291/235729092-86301d2e-3ccc-4912-9ad3-c3c22c88258b.png)

## Technologies Used
- Python
- Pandas
- NumPy
- Scikit-learn
- HTML
- CSS
- Google APIs
- The Odds API

## How to Use
1. Create an account with The Odds API to get an API key. The API key is then used as an argument to the `fetch_data_from_api()` function in the script.

2. Obtain credentials for Google APIs, specifically the Gmail API. These credentials should be stored in a `credentials.json` file in the root directory of the project.

3. Once the above prerequisites are completed, you can run the `main()` function to fetch the betting lines, generate recommendations, and send an email with the recommendations to a specified recipient.

## Contribute
Everyone is welcome to contribute to this project! Feel free to add new features, fix bugs, or make improvements. Just fork the repository, make your changes, and submit a pull request. I appreciate your help! :)

## Contribute

Everyone is welcome to contribute to this project! Feel free to add new features, fix bugs, or make improvements. Just fork the repository, make your changes, and submit a pull request. I appreciate your help! :)

## Disclaimer
This project is intended for educational purposes only. It should not be used as the sole basis for actual betting decisions. Betting involves risk, and you should only bet with money you can afford to lose. Always bet responsibly.
