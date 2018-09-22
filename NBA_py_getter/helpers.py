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


def has_games(date, scoreboard):
    """
    Checks if there were any matches played on a given date. Use this as the
    condition before running the data getters to avoid empty data dumps.

    :param date: datetime.datetime object
    :param pygame_scoreboard: provide the Scoreboard import for the check
    :return: Boolean - True if there were any matches
    """
    logging.info("Game availability check started.")
    try:
        games = scoreboard(month=date.month, day=date.day, year=date.year).available()
        logging.info("Game availability check ended.")
        avialability = not(games == [])
        return avialability
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


def get_line_score(date, scoreboard):
    """

    :param date:
    :param scoreboard:
    :return:
    """
    """Get Data Frame of games for today (dates set for dev and debug.
    Args:
        date : datetime object for the day we want games from
    Return:
        games : Data Frame object of games played at a given day
    """
    scores = scoreboard(month=date.month, day=date.day, year=date.year)
    """
    line_score = scores.line_score()
    visiting_side_score = line_score.iloc[::2, [1, 5, 21]]  # visiting side
    home_side_score = line_score.iloc[1::2, [1, 5, 21]]  # home side
    merged = visiting_side_score.merge(home_side_score, on="GAME_SEQUENCE")
    """
    return scores.line_score()
