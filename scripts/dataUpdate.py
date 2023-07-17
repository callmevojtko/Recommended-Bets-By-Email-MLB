import requests
from bs4 import BeautifulSoup
import pandas as pd


def fetch_data(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # The id might need to be adjusted
    table = soup.find('table', {'id': 'teams_standard_batting'})
    df = pd.read_html(str(table))[0]

    return df


def clean_data(df):
    df = df.rename(columns={'Tm': 'Team_ID'})
    df['Team_ID'] = range(1, len(df) + 1)
    df = df[df.Team_ID <= 30]

    return df

def save_data(df, filename):
    df.to_csv(filename, index=False)


def main():
    url = 'https://www.baseball-reference.com/leagues/majors/2023.shtml#teams_standard_batting'
    df = fetch_data(url)
    df = clean_data(df)
    save_data(
        df, '') # Set your own path to MLB DATA file


if __name__ == '__main__':
    main()
