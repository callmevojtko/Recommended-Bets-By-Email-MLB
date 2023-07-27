from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import pandas as pd
import time

def fetch_data(driver):
    # Let the JavaScript load
    time.sleep(5)  # wait 10 seconds

    # Get the table's HTML
    table_html = driver.find_element(
        By.ID, 'div_teams_standard_pitching').get_attribute('innerHTML')

    # Use pandas to read the HTML
    df = pd.read_html(table_html)[0]

    return df


def swap_rows(df):
    """Swap data between rows with 'Team_ID' values of 1 and 2."""
    # Get indices where 'Team_ID' is 1 and 2
    i1 = df[df['Team_ID'] == 1].index[0]
    i2 = df[df['Team_ID'] == 2].index[0]

    # Make copies of the two rows
    row1, row2 = df.loc[i1].copy(), df.loc[i2].copy()

    # Swap the data in the two rows
    df.loc[i1], df.loc[i2] = row2, row1

    # Swap the 'Team_ID' values back to their original values
    df.loc[i1, 'Team_ID'], df.loc[i2, 'Team_ID'] = 1, 2

    return df


def clean_data(df):
    df = df.rename(columns={'Tm': 'Team_ID'})
    df['Team_ID'] = range(1, len(df) + 1)
    df = df[df.Team_ID <= 30]

    df = swap_rows(df)

    return df

def save_data(df, filename):
    df.to_csv(filename, index=False)


def main():
    # Set up Chrome options
    chrome_options = Options()
    chrome_options.add_experimental_option('prefs', {
        "download.default_directory": "./",
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    })

    # Set up the Selenium driver
    driver = webdriver.Chrome(service=Service(
        ChromeDriverManager().install()), options=chrome_options)

    # Navigate to the webpage
    driver.get(
        "https://www.baseball-reference.com/leagues/majors/2023.shtml#teams_standard_pitching")

    df = fetch_data(driver)
    df = clean_data(df)
    # Set your own path to MLB DATA file
    save_data(df, './data/2023_MLB_Pitching_Data.csv')

    # Close the driver
    driver.quit()


if __name__ == '__main__':
    main()
