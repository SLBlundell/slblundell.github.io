# %%
from flask import Flask
from flask_restful import Resource, Api, reqparse
import pandas as pd
import ast
from difflib import SequenceMatcher
from current_season_scraper import team_scrape, player_scrape

def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

app = Flask(__name__)
api = Api(app)

# /player
player_path = 'C:/Users/whisk/OneDrive/Documents/Bristol/Economics/Year 4/Data Science/slblundell.github.io/nba_project/data/player_per_game_salary_2023.csv'
# /team
team_path = 'C:/Users/whisk/OneDrive/Documents/Bristol/Economics/Year 4/Data Science/slblundell.github.io/nba_project/data/team_per_game_2023.csv'

class Player(Resource):
    def get(self):
        data = pd.read_csv(player_path).drop(columns='Unnamed: 0')
        data = data.to_dict()
        return {'data': data}, 200


class Team(Resource):
    def get(self):
        data = pd.read_csv(team_path).drop(columns='Unnamed: 0')
        data = data.to_dict()
        return {'data': data}, 200


class Scrapers(Resource):
    def get(self):
        return current_season_scraper.player_scrape, current_season_scraper.team_scrape


api.add_resource(Player, '/player')
api.add_resource(Team, '/team')
api.add_resource(Scrapers, '/scrapers')

if __name__ == '__main__':
    app.run()

