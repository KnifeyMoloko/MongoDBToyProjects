

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
from pymongo import collection
import json
import logging
import pprint
from logging import config as log_config
from datetime import datetime
from pathlib import Path
from nba_py import constants, game, player, team, Scoreboard
from constants import log, logger_root_config, nba_teams
from helpers import *


def main():
    ### get environment variables if any ###
    first_run = False

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

    ### if there are no teams in the teams database, upload the teams there ###
    # check if document count in nba.teams is smaller than the return for nba_py.team.TeamList
    #team_list = team.TeamList().json['resultSets'][0]["rowSet"]
    # return a list of current NBA teams
    #team_list_filtered = [i for i in team_list if i[4] is not None]

    if teams.find_one({}) is None:
        if first_run is True:
            seed_teams(teams, nba_teams)  # this should ony run on the first run TODO: take a env argv for a first run
        else:
            raise LookupError
    elif mongo_collection_validator(teams, nba_teams, "_id", "_id",  True, True):
        pass
    else:
        raise LookupError

    ### call data getters to fetch data from nba.com ###
    date = datetime(2018, 2, 25)  # dev only

    ### fetch the Scoreboard json dump
    scoreboard = get_scoreboard(date, Scoreboard)


    # check if there are games available
    if has_games(scoreboard):
        line_score = get_line_score(scoreboard)  # prime source for the web page and game db
        series_standings = get_series_standings(scoreboard)  # link to the game db?
        last_meeting = get_last_meeting(scoreboard)  # link to the game db
        standings = get_conference_standings(scoreboard)  # only useful for the web page

        """
        row_set = (scoreboard["resultSets"][1]["rowSet"])
        # this is essentialy the daily scores layout, though it might make more sense to put it in the SQL db
        for a, h in zip(row_set[::2], row_set[1::2]):
            print(a[4], a[21], " : ", h[4], h[21])
        """

        # modify the data if needed
        modded_line_score = line_score_formatter(line_score)  # this is a tuple
        add_games_from_line_score(teams, modded_line_score[0])

        # upload the data to the mongo databases
        mongo_dispatcher(data=None, db_enpoint=None)

        # upload the data to postgresql databases
        postgresql_dispatcher(data=None, db_enpoint=None)

    # dump the logs into the mongo database and local catalog
    log_dump(log, datetime.today(), logs)


    #TODO: decide on the data model that I want to use: what to keep and in what form

if __name__ == "__main__":
    main()
