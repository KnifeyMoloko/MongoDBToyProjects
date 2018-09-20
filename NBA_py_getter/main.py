

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
import logging
from logging import config as log_config
from datetime import datetime
from pathlib import Path
from nba_py import constants, game, player, team, Scoreboard
from constants import log, logger_root_config
from helpers import log_dump, has_games, get_games, get_line_score


def main():
    # set up the Mongo client

    mongo_client = pymongo.mongo_client.MongoClient()

    # set up pathlib instance for local log file manipulations

    path = Path('.')/'logs'
    path.mkdir(parents=True, exist_ok=True)

    # set up and configure root logger here

    log_config.dictConfig(logger_root_config)
    logger = logging.getLogger(__name__)  # name the logger with the module name

    # create the db and collections; 'lazy' creation will create with first insert

    teams = mongo_client.nba.teams
    games = mongo_client.nba.games
    logs = mongo_client.nba.logs

    # call data getters to fetch data from nba.com
    print(has_games(datetime(2018, 2, 25), Scoreboard))
    print(get_games(datetime(2018, 2, 25), Scoreboard))
    print(get_line_score(datetime(2018, 2, 25), Scoreboard))

    # modify the data if needed

    # upload the data to the mongo database

    # dump the logs into the mongo database and local catalog
    #log_dump(log, datetime.today(), logs)


    #TODO: decide on the data model that I want to use: what to keep and in what form

if __name__ == "__main__":
    main()

