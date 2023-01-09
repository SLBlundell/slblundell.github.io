# %%
# import required libraries
import pandas as pd
import requests
from bs4 import BeautifulSoup
from unidecode import unidecode
from difflib import SequenceMatcher
import numpy as np

# %%
def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

# %%
def team_scrape():
    
    teams = ["Boston Celtics", "Brooklyn Nets", "New York Knicks", "Philadelphia 76ers", "Toronto Raptors", "Chicago Bulls",
    "Cleveland Cavaliers", "Detroit Pistons", "Indiana Pacers", "Milwaukee Bucks", "Atlanta Hawks", "Charlotte Hornets",
    "Miami Heat", "Orlando Magic", "Washington Wizards", "Denver Nuggets", "Minnesota Timberwolves", "Oklahoma City Thunder",
    "Portland Trail Blazers", "Utah Jazz", "Golden State Warriors", "Los Angeles Clippers", "Los Angeles Lakers", "Phoenix Suns",
    "Sacramento Kings", "Dallas Mavericks", "Houston Rockets", "Memphis Grizzlies", "New Orleans Pelicans", "San Antonio Spurs"]

    url_team = 'https://www.basketball-reference.com/leagues/NBA_2023.html'
    url_team_payroll = 'https://hoopshype.com/salaries/'

    # TEAM STATS

    team_stats = requests.get(url_team)

    # create BeautifulSoup object
    soup = BeautifulSoup(team_stats.content, 'html.parser')

    # locate correct table
    table = soup.find(lambda tag: tag.name=='table' and tag.has_attr('id') and tag['id']=="per_game-team") 
    rows = table.findAll(lambda tag: tag.name=='tr')

    # create DataFrame
    df = pd.read_html(str(table))[0]

    # clean DataFrame
    df = df.drop(index=30)
    df.insert(2, "Year", 2023, True)
    df = df.drop(columns=["G","Rk"])
    df = df.reset_index(drop=True)

    # add advanced stats to DataFrame
    table = soup.find(lambda tag: tag.name=='table' and tag.has_attr('id') and tag['id']=="advanced-team") 
    rows = table.findAll(lambda tag: tag.name=='tr')

    df_adv = pd.read_html(str(table))[0]

    df_adv.columns = df_adv.columns.droplevel()
    df_adv = df_adv.drop(index=30)
    df_adv['Team'] = df_adv['Team'].str.replace('*', '')
    df_adv = df_adv.drop(columns=["Rk", "L", "PW", "PL", "Unnamed: 17_level_1", "Unnamed: 22_level_1", "Unnamed: 27_level_1", "Arena"])
    df_adv = df_adv.reset_index(drop=True)

    # merge per game and advanced stats
    df_team = pd.merge(df, df_adv, on='Team')

    # further cleaning
    df_team.columns.values[40] = "Op_eFG%"
    df_team.insert(46, "Playoff_W", 0)

    # TEAM SALARIES

    payrolls = requests.get(url_team_payroll)
    soup = BeautifulSoup(payrolls.content, 'html.parser')

    table = soup.find("table", class_="hh-salaries-ranking-table hh-salaries-table-sortable responsive")
    rows = table.findAll(lambda tag: tag.name=='tr')

    df_payroll = pd.read_html(str(table))[0]

    # cleaning
    df_payroll = df_payroll.iloc[:, [1,2]]
    df_payroll['2022/23'] = df_payroll['2022/23'].str.replace('[$,]', '').astype(int)
    df_payroll = df_payroll.rename(columns={'2022/23': 'Payroll'})

    team_replace = {row: team for row in df_payroll['Team'].to_list() for team in teams if similar(row, team)>=0.53}

    for index, team in team_replace.items():
        df_payroll.loc[df_payroll['Team'] == index, 'Team'] = team

    # merge per game and advanced stats
    df_team = pd.merge(df_team, df_payroll, on='Team')
    df_team = df_team.replace(r'^\s*$', np.nan, regex=True)

    # write data to csv
    df_team.to_csv('C:/Users/whisk/OneDrive/Documents/Bristol/Economics/Year 4/Data Science/slblundell.github.io/nba_project/data/team_per_game_2023.csv')

# %%
def player_scrape():

    url_player = 'https://www.basketball-reference.com/leagues/NBA_2023_per_game.html'
    url_player_adv = 'https://www.basketball-reference.com/leagues/NBA_2023_advanced.html'
    url_player_salary = 'https://hoopshype.com/salaries/players/'

    # PLAYER STATS

    per_game = requests.get(url_player)
    adv = requests.get(url_player_adv)

    # create BeautifulSoup object
    soup = BeautifulSoup(per_game.content, 'html.parser')

    # locate correct table
    table = soup.find("table", class_="sortable stats_table")
    rows = table.findAll(lambda tag: tag.name=='tr')

    # create DataFrame
    df = pd.read_html(str(table))[0]

    # clean DataFrame
    df = df.drop(index=30)
    df = df.drop(columns=["G","Rk", "GS"])
    df = df.reset_index(drop=True)

    # create BeautifulSoup object
    soup = BeautifulSoup(adv.content, 'html.parser')

    # add advanced stats to DataFrame
    table = soup.find("table", class_="sortable stats_table") 
    rows = table.findAll(lambda tag: tag.name=='tr')
    df_adv = pd.read_html(str(table))[0]
    df_adv = df_adv.drop(columns=["Rk", "G", "Tm", "MP", "Pos", "Age", "Unnamed: 19", "Unnamed: 24"])
    df_adv = df_adv.reset_index(drop=True)

    df_player = pd.merge(df, df_adv, on='Player')

    # drop junk rows
    df_player = df_player.drop(df_player[df_player.Player == "Player"].index)

    # reformat accented Player characters
    df_player["Player"] = df_player["Player"].apply(lambda x: unidecode(x))
    df_player['Player'] = df_player['Player'].str.replace('.', '')

    # drop duplicate players (players traded mid-season. NOTE: this approach should be altered if significant 
    # players are traded as the season progresses)
    df_player = df_player.drop_duplicates(subset="Player", keep='first').reset_index(drop=True)

    # PLAYER SALARIES

    salary = requests.get(url_player_salary)

    #create BeautifulSoup object
    soup = BeautifulSoup(salary.content, 'html.parser')
    print(soup.table)

    #locate correct table
    table = soup.find("table", class_="hh-salaries-ranking-table hh-salaries-table-sortable responsive")
    rows = table.findAll(lambda tag: tag.name=='tr')

    #create DataFrame
    df_salary = pd.read_html(str(table))[0]

    # drop junk column
    df_salary = df_salary.drop(columns="Unnamed: 0")

    # convert salaries to int
    for column in df_salary.columns:
        if column != "Player":
            df_salary[column] = df_salary[column].str.replace('[$,]', '').astype(int)

    # correct player names
    df_salary = df_salary.replace({'Player': {'Sviatoslav Mykhailiuk': 'Svi Mykhailiuk', 
    'Scottie Pippen Jr': 'Scotty Pippen Jr', 'Josh Primo': 'Joshua Primo', 'Dennis Schroeder': 'Dennis Schroder', 
    'Ishmael Smith': 'Ish Smith', 'Santiago Aldama': 'Santi Aldama', 'BJ Boston': 'Brandon Boston Jr', 
    'Nicolas Claxton': 'Nic Claxton', "Devonte Graham": "Devonte' Graham", 'Juan Hernangomez': 'Juancho Hernangomez',
    'Herb Jones': 'Herbert Jones', 'KJ Martin': 'Kenyon Martin Jr', 'Patrick Mills': 'Patty Mills', 
    'Ishmail Wainright': 'Ish Wainright'}})

    # merge player dataframes
    df_player_salary = pd.merge(df_player, df_salary, on='Player')
    df_player_salary

    # checking missing rows within between player and salary datasets
    df_player_player_list = df_player["Player"].tolist()
    df_salary_player_list = df_salary["Player"].tolist()

    player_diff_1 = []
    for player in df_player_player_list:
        if player not in df_salary_player_list:
            player_diff_1.append(player)

    player_diff_2 = []
    for player in df_salary_player_list:
        if player not in df_player_player_list:
            player_diff_2.append(player)

    # correcting for differing naming conventions between datasets

    for player in player_diff_2:
        if f"{player} Jr" in player_diff_1:
            df_salary['Player'] = df_salary['Player'].replace([player], f"{player} Jr")
        if f"{player} Sr" in player_diff_1:
            df_salary['Player'] = df_salary['Player'].replace([player], f"{player} Sr")
        if f"{player} III" in player_diff_1:
            df_salary['Player'] = df_salary['Player'].replace([player], f"{player} III")
        if f"{player} IV" in player_diff_1:
            df_salary['Player'] = df_salary['Player'].replace([player], f"{player} IV")

    # merge corrected player dataframes 
    df_player_salary = pd.merge(df_player, df_salary, on='Player')

    df_player_salary = df_player_salary.replace(r'^\s*$', np.nan, regex=True)

    # write data to csv
    df_player_salary.to_csv('C:/Users/whisk/OneDrive/Documents/Bristol/Economics/Year 4/Data Science/slblundell.github.io/nba_project/data/player_per_game_salary_2023.csv')

# %%
if __name__ == '__main__':
    team_scrape()
    player_scrape()


