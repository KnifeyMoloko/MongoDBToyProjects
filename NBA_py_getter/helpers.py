import logging


#### helper functions for NBA_py_getter

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


### has 'x' checks

def has_games(scoreboard_json):
    """
    Checks if there were any matches played on a given date. Use this as the
    condition before running the data getters to avoid empty data dumps.

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


### data getters

def get_data_headers(data):
    """
    Fetches the list of headers for a given rowSet in nba_py.
    :param data: the nba_py module for on the level 1 step above 'rowSet'
    :return: list of headers for the data set
    """
    logging.debug("Fetching headers for data set - START.")
    try:
        headers_list = data["headers"]
        return headers_list
    except Exception:
        logging.exception("Bumped into an error while fetching headers for data set")


def get_scoreboard(date, scoreboard_instance):
    """
    :param scoreboard_instance: nba_py Scoreboard instance
    :param date: datetime.datetime object as the date we query for
    :return: nba_py Scoreboard object
    """
    logging.debug("Fetching Scoreboard - START.")
    try:
        scoreboard_json = scoreboard_instance(month=date.month, day=date.day, year=date.year).json
        logging.debug("Fetching Scoreboard - DONE.")
        return scoreboard_json
    except Exception:
        logging.exception("Bumped into an error while fetching Scoreboard")



def get_line_score(scoreboard_json):
    """
    :param scoreboard_json: nba_py Scoreboard JSON dump
    :return: the LineScore key values from the JSON dump
    """
    logging.debug("Fetching line score - START.")
    try:
        scores = scoreboard_json["resultSets"][1]["rowSet"]
        logging.debug("Fetching line score - DONE.")
        return scores
    except Exception:
        logging.exception("Bumped into an error while getting line score")


def get_series_standings(scoreboard_json):
    """
    :param scoreboard_json: nba_py Scoreboard JSON dump
    :return: series standings for a given game
    """
    logging.debug("Fetching series standings - START.")
    try:
        series_standings = scoreboard_json["resultSets"][2]["rowSet"]
        logging.debug("Fetching series standings - DONE.")
        return series_standings
    except Exception:
        logging.exception("Bumped into an error while getting series standings")


def get_last_meeting(scoreboard_json):
    """
    :param scoreboard_json: nba_py Scoreboard JSON dump
    :return: last meeting data for a given game
    """
    logging.debug("Fetching last meetings - START.")
    try:
        last_meeting = scoreboard_json["resultSets"][3]["rowSet"]
        logging.debug("Fetching series standings - DONE.")
        return last_meeting
    except Exception:
        logging.exception("Bumped into an error while getting last meetings")


def get_conference_standings(scoreboard_json):
    """
    :param scoreboard_json: nba_py Scoreboard JSON dump
    :return: a dict containing west and east conference data for a given date
    """
    logging.debug("Fetching last meetings - START.")
    try:
        east_standings = scoreboard_json["resultSets"][4]["rowSet"]
        west_standings = scoreboard_json["resultSets"][5]["rowSet"]
        daily_standings = {"east": east_standings, "west": west_standings}
        logging.debug("Fetching series standings - DONE.")
        return daily_standings
    except Exception:
        logging.exception("Bumped into an error while getting conference standings")


### data manipulation funcs

def upload_headers(nba_py_package, indices_to_process):
    """
    Recipe:
        upload_headers(scoreboard["resultSets"], range(0, len(scoreboard["resultSets"])))
    :param nba_py_package:
    :param indices_to_process:
    :return:
    """
    package = nba_py_package
    ind = indices_to_process
    for i in ind:
        print(nba_py_package[i]["name"])
        print(nba_py_package[i]["headers"])


def line_score_formatter(raw_data):
    output = {'game_date_est': None,
              'game_sequence': None,
              'game_id': None,
              'team_id': None,
              'team_abbreviation': None,
              'team_city_name': None,
              'team_wins_losses': None,
              'pts_qtr1': None,
              'pts_qtr2': None,
              'pts_qtr3': None,
              'pts_qtr4': None,
              'pts_ot1': None,
              'pts_ot2': None,
              'pts_ot3': None,
              'pts_ot4': None,
              'pts_ot5': None,
              'pts_ot6': None,
              'pts_ot7': None,
              'pts_ot8': None,
              'pts_ot9': None,
              'pts_ot10': None,
              'pts': None,
              'fg_pct': None,
              'ft_pct': None,
              'fg3_pct': None,
              'assists': None,
              'rebounds': None,
              'turnovers': None}
    return raw_data