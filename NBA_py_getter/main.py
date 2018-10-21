

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
from sys import argv
from logging import config as log_config
from dateutil import parser
from datetime import datetime
from pathlib import Path
from nba_py import constants, game, player, team, Scoreboard
from constants import log, logger_root_config, nba_teams, runtime_timestamp
from helpers import *


def main():
    ### get environment variables if any ###
    parsed_argv = parse_argv(argv)

    # set runtime flags
    logging.info("Setting runtime flags - START")
    first_run = bool(parsed_argv[0])
    no_mongo = bool(parsed_argv[1])
    no_postgre = bool(parsed_argv[2])
    run_date = parsed_argv[3]
    is_season_run = bool(parsed_argv[4])
    season_run_season = parsed_argv[5]
    logging.info("Setting runtime flags: ", str(parsed_argv))
    logging.info("Setting runtime flags - END.")

    # set run date

    # run_date will be None if no params are provided or to few are provided at runtime
    if run_date is not None and not is_season_run:
        try:
            run_date = parser.parse(run_date)  # should parse most reasonable date formats
        except Exception:
            logging.exception("Bumped into a problem while parsing run date!")
            raise ValueError
    elif is_season_run:
        run_data = "Season run: ".join(str(season_run_season))
    else:
        # use the date of runtime as run_date
        run_date = runtime_timestamp

    ### set up the Mongo client ###
    #TODO: decidde if the mongo checks should also include the service session and db path
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

    # check if the season run option is
    if is_season_run:
        season_run_db = mongo_client.nba.prev_season
        season_run(season_run_season, season_run_db)
        return 0

    if teams.find_one({}) is None:
        if first_run is True:
            seed_teams(teams, nba_teams)
        else:
            print(first_run is True)
            raise LookupError
    elif mongo_collection_validator(teams, nba_teams, "_id", "_id",  True, True):
        pass
    else:
        raise LookupError

    ### call data getters to fetch data from nba.com ###
    date = run_date
    logging.info("Run date is: " + str(run_date))

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
        #add_games_from_line_score(teams, modded_line_score[0])

        # upload the data to the mongo databases
        mongo_dispatcher(data=None, db_enpoint=None)

        # upload the data to postgresql databases
        postgresql_dispatcher(data=None, db_enpoint=None)

    # dump the logs into the mongo database and local catalog
    log_dump(log, datetime.today(), logs)

    #TODO: decide on the data model that I want to use: what to keep and in what form


if __name__ == "__main__":
    main()
