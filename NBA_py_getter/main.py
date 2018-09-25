

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
import json
import logging
import pprint
from logging import config as log_config
from datetime import datetime
from pathlib import Path
from nba_py import constants, game, player, team, Scoreboard
from constants import log, logger_root_config
from helpers import *


def main():
    ### set up the Mongo client ###

    mongo_client = pymongo.mongo_client.MongoClient()

    ### set up pathlib instance for local log file manipulations ###

    path = Path('.')/'logs'
    path.mkdir(parents=True, exist_ok=True)

    ### set up and configure root logger here ###

    log_config.dictConfig(logger_root_config)
    logger = logging.getLogger(__name__)  # name the logger with the module name

    ### create the db and collections
    ### 'lazy' creation will create with first insert ###

    teams = mongo_client.nba.teams
    games = mongo_client.nba.games
    logs = mongo_client.nba.logs

    ### call data getters to fetch data from nba.com ###
    date = datetime(2018, 2, 25)  # dev only

    # fetch the Scorebaord json dump
    scoreboard_json = Scoreboard(month=date.month, day=date.day, year=date.year).json

    # check if there are games available
    if has_games(date, scoreboard_json):
        line_score = get_line_score(date, scoreboard_json)  # prime source for the web page and game db
        series_standings = get_series_standings(date, scoreboard_json)  # link to the game db?
        last_meeting = get_last_meeting()  # link to the game db
        standings = get_conference_standings()  # only useful for the web page

        row_set = (scoreboard_json["resultSets"][1]["rowSet"])
        # this is essentialy the daily scores layout, though it might make more sense to put it in the SQL db
        for a, h in zip(row_set[::2], row_set[1::2]):
            print(a[4], a[21], " : ", h[4], h[21])

    # modify the data if needed

    # upload the data to the mongo databases

    # dump the logs into the mongo database and local catalog
    #log_dump(log, datetime.today(), logs)


    #TODO: decide on the data model that I want to use: what to keep and in what form

if __name__ == "__main__":
    main()
