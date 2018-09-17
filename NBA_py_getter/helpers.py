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
    except Exception as e:
        logging.exception("Bumped into an error while dumping log!\n%s", e)


def has_games(date, pygame_scoreboard):
    """
    Checks if there were any matches played on a given date. Use this as the
    condition before running the data getters to avoid empty data dumps.

    :param date: datetime.datetime object
    :param pygame_scoreboard: provide a Scoreboard class instance for the check
    :return: Boolean - True if there were any matches
    """
    logging.info("Game availability check started.")
    try:
        games = pygame_scoreboard(month=date.month, day=date.day, year=date.year)\
            .available()\
            .empty
        logging.info("Game availability check ended.")
        return not games
    except Exception as e:
        logging.exception("Bumped into an error while checking game "
                          "availability\n%s", e)
