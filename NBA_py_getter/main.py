

"""This small script is basically a scratch  draft for creating a data
workflow using nba_py. The goal is to retrieve a subset of the NBA
statistical data available and put it in a mongoDB database for further
use.
Optional goal: reformat the data to make it more suitable for analysis
or posting to webpage.

Author: Maciej Cisowski (KnifeyMoloko)
Date: 08.17.2018 13:19"""

#imports
import pymongo
import pandas
from os.path import basename
from inspect import stack
from datetime import datetime
from pathlib import Path
from nba_py import constants, game, player, team, Scoreboard
from constants import db_name, season, log
from helpers import add_log_entry, log_dump

# set up the Mongo client

mongo_client = pymongo.mongo_client.MongoClient()

# set up pathlib instance for local file manipulations

path = Path('.') # current dir path

# create the db and collections; 'lazy' creation will create with first insert

teams = mongo_client.nba.teams
games = mongo_client.nba.games
logs = mongo_client.nba.logs

# call data getters to fetch data from nba.com

# modify the data if needed

# upload the data to the mongo database

# data getters

# dump the logs into the mongo database and local catalog
log_dump(log, path, datetime.today(), logs)


def get_games(date=None):
    """Gets a pandas Data Frame object with the data for games played on
    a given day.

    Args:
        date : datetime object, defaults to datetime.datetime.now()
    Return : Data Frame object with game data.
    """

    if date is None:
        #TODO: Resolve the timing issue - some games may slip between the days depending on the time the script is run
        date = datetime(2018, 2, 20)

    games = Scoreboard(month=date.month, day=date.day, year=date.year)
    #TODO: empty-or-not logic here
    print(games.available().empty)
    print(games.available())


    #TODO: decide on the data model that I want to use: what to keep and in what form


    #for row in games.available().itertuples():
    #    print(game.Boxscore(row[1]).player_stats())

def get_line_score(date=None):
    """Get Data Frame of games for today (dates set for dev and debug.
    Args:
        date : datetime object for the day we want games from
    Return:
        games : Data Frame object of games played at a given day
    """
    scores = Scoreboard(month=date.month, day=date.day, year=date.year)
    line_score = scores.line_score()
    visiting_side_score = line_score.iloc[::2, [1, 5, 21]]  # visiting side
    home_side_score = line_score.iloc[1::2, [1, 5, 21]]  # home side
    merged = visiting_side_score.merge(home_side_score, on="GAME_SEQUENCE")
    return merged


if __name__ == "__main__":
    get_games()

