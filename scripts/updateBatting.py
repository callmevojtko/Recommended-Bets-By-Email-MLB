from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import pandas as pd
import time
import os

def fetch_additional_data(driver):
    # Navigate to the other webpage
    driver.get(
        "https://www.baseball-reference.com/leagues/majors/2023.shtml#all_teams_standard_batting")

    # Let the JavaScript load
    time.sleep(5)  # wait 5 seconds

    # Get the table's HTML
    table_html = driver.find_element(
        By.ID, 'div_teams_standard_batting').get_attribute('innerHTML')

    # Use pandas to read the HTML
    additional_df = pd.read_html(table_html)[0]

    # Keep only the first 30 rows and the "Runs Scored/Game" column
    additional_df = additional_df.loc[:29, ['Tm', 'R/G']]

    # Sort the DataFrame by 'Tm' to ensure it's in the same order as the original DataFrame
    additional_df = additional_df.sort_values(by='Tm')
    
    # Swap 'R/G' values for team IDs 1 and 2
    additional_df.loc[0, 'R/G'], additional_df.loc[1, 'R/G'] = additional_df.loc[1, 'R/G'], additional_df.loc[0, 'R/G']

    return additional_df

def main():
    # Set up Chrome options
    chrome_options = Options()
    chrome_options.add_experimental_option('prefs', {
        # Change to your desired directory
        "download.default_directory": "/Users/vojtkobrian/Downloads/",
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    })

    # Delete the existing file if it exists
    if os.path.exists("/Users/vojtkobrian/Downloads/expected_stats.csv"):
        os.remove("/Users/vojtkobrian/Downloads/expected_stats.csv")

    # Set up the Selenium driver
    driver = webdriver.Chrome(service=Service(
        ChromeDriverManager().install()), options=chrome_options)

    # Navigate to the webpage
    driver.get("https://baseballsavant.mlb.com/leaderboard/expected_statistics?type=batter-team&year=2023&position=&team=&min=q&sort=0&sortDir=asc")

    # Let the JavaScript load
    time.sleep(5)  # wait 10 seconds

    # Click the download button
    driver.find_element(By.ID, 'btnCSV').click()

    # Wait for the download to complete
    time.sleep(5)  # wait 5 seconds

    # Assuming the downloaded file has a specific name, we can load it into a pandas DataFrame
    # Replace "downloaded.csv" with the name of the downloaded file
    df = pd.read_csv("/Users/vojtkobrian/Downloads/expected_stats.csv")

    # Reorder the dataframe, rename columns, and perform other transformations
    df = df.sort_values(by=['team_id'], ascending=True)
    df = df.drop(columns=['team', 'year'])
    df['team_id'] = df['team_id'].rank(method='min').astype(int)
    # Rename columns
    df = df.rename(columns={
        'team_id': 'Team_ID',
        'pa': 'PA',
        'bip': 'BIP',
        'ba': 'BA',
        'est_ba': 'xBA',
        'slg': 'SLG',
        'est_slg': 'xSLG',
        'woba': 'wOBA',
        'est_woba': 'xwOBA'
    })

    # Fetch the additional data
    additional_df = fetch_additional_data(driver)

    # Append the "Runs Scored/Game" column to the original DataFrame
    df['R/G'] = additional_df['R/G'].values

    # Write the DataFrame to a local CSV file
    df.to_csv('./data/2023_MLB_Batting_Data.csv', index=False)

    # Close the driver
    driver.quit()


if __name__ == '__main__':
    main()
