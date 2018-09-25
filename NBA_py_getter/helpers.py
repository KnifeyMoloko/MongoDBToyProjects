import logging


# helper functions for NBA_py_getter
def log_dump(log_container, timestamp, mongo_instance):
    """
    Dumps the logs collected in the log_container list locally and adds them
    to the mongo_instance database.

    :param log_container: list for collecting log entries
    :param timestamp: datetime.datetime.timestamp or whatever you prefer
    :param mongo_instance: mongo db collection path for storing logs
    :return: No return value
    """
    # log start
    logging.info("Log dump started.")

    # define database entry using the Logger's stream handler
    db_entry = {"name": "log_" + str(timestamp),
                "output": log_container.getvalue().format()}
    # add log output to database
    try:
        mongo_instance.insert_one(db_entry)
    except Exception:
        #TODO: Maybe create a list of mongodb erros to check here?
        logging.exception("Bumped into an error while dumping log!")


def has_games(date, scoreboard_json):
    """
    Checks if there were any matches played on a given date. Use this as the
    condition before running the data getters to avoid empty data dumps.

    :param date: datetime.datetime object
    :param scoreboard_json: Scoreboard JSON dump
    :return: Boolean - True if there were any matches
    """
    logging.info("Game availability check started.")
    try:
        if scoreboard_json["resultSets"][6]["rowSet"] is not []:
            logging.info("Game availability check ended.")
            return True
    except Exception:
        logging.exception("Bumped into an error while checking game "
                          "availability")


def get_games(date, scoreboard):
    """
    :param date: datetime.datetime object for the date of the data
    :param scoreboard: nba_py Scoreboard module
    :return: nba_py Scoreboard instance for the given date
    """
    #TODO: This can be a dispatch function for the Scorebaord-realted data
    games = scoreboard(month=date.month, day=date.day, year=date.year)
    return games


def get_line_score(date, scoreboard_json):
    """
    :param date: datetime.datetime object for the date of the data
    :param scoreboard_json: nba_py Scoreboard JSON dump
    :return: the LineScore key values from the JSON dump
    """
    scores = scoreboard_json["resultSets"][1]["rowSet"]
    return scores

def get_series_standings(date, scoreboard_json):
    """
    :param date: datetime.datetime object for the date of the data
    :param scoreboard_json: nba_py Scoreboard JSON dump
    :return: series standings for a given game
    """
    series_standings = scoreboard_json["resultSets"][2]["rowSet"]
    return series_standings


def get_last_meeting(date, scoreboard_json):
    """
    :param date: datetime.datetime object for the date of the data
    :param scoreboard_json: nba_py Scoreboard JSON dump
    :return: last meeting data for a given game
    """
    last_meeting = scoreboard_json["resultSets"][3]["rowSet"]
    return last_meeting


def get_conference_standings(date, scoreboard_json):
    """
    :param date: datetime.datetime object for the date of the data
    :param scoreboard_json: nba_py Scoreboard JSON dump
    :return: a dict containing west and east conference data for a given date
    """
    east_standings = scoreboard_json["resultSets"][4]["rowSet"]
    west_standings = scoreboard_json["resultSets"][5]["rowSet"]
    daily_standings = {"east": east_standings, "west": west_standings}
    return daily_standings

