

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
import logging
from sys import argv
from logging import config as log_config
from dateutil import parser
from datetime import datetime
from pathlib import Path
from nba_py import constants, team, Scoreboard
from config import log, logger_root_config, nba_teams, runtime_timestamp, mongodb_path
from helpers import *
from subprocess import Popen, TimeoutExpired


def main():
    # get environment variables if any
    parsed_argv = parse_argv(argv)

    # set runtime flags
    logging.info("Setting runtime flags - START")
    first_run = bool(parsed_argv[0])
    no_mongo = bool(parsed_argv[1])
    no_postgre = bool(parsed_argv[2])
    run_date = parsed_argv[3]
    is_season_run = bool(parsed_argv[4])
    season_run_season = parsed_argv[5]
    email = bool(parsed_argv[6])
    user = parsed_argv[7]
    passwrd = parsed_argv[8]

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


    # start the mongod process with the dbpath specified in config.py
    Popen('mongod --dbpath ' + mongodb_path, shell=True)
    #TODO: capture the Popen output into the log file, think about error handling here

    # set up the Mongo client
    mongo_client = pymongo.mongo_client.MongoClient()

    # set up pathlib instance for local log file manipulations

    path = Path('.')/'logs'
    path.mkdir(parents=True, exist_ok=True)

    #set up and configure root logger here

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
        # getting around the return of a func being a tuple
        s_run = get_season_run(season_run_season, season_run_db, team)[0]
        mongo_dispatcher(data=s_run, db_enpoint=season_run_db)
        return 0  # return, in order to exit the script

    if teams.find_one({}) is None:
        if first_run is True:
            seed_teams(teams, nba_teams)
            return 0  # end the run
        else:
            print(first_run is True)
            raise LookupError
    elif mongo_collection_validator(teams, nba_teams, "_id", "_id",  True, True):
        pass
    else:
        raise LookupError


    # call data getters to fetch data from nba.com

    date = run_date
    logging.info("Run date is: " + str(run_date))

    # fetch the Scoreboard json dump
    try:
        scoreboard = get_scoreboard(date, Scoreboard)
    finally:
        # dump the logs into the mongo database and local catalog
        from config import log
        log_dump(log, datetime.today(), logs)
        send_logs_to_email(log.getvalue(), user, passwrd)


if __name__ == "__main__":
    main()
