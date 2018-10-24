import logging


# helper functions for NBA_py_getter


# decorators


def basic_log_decorator(func):
    def wrapper(*args, **kwargs):
        try:
            logging.info(func.__name__ + " - START")
            output = func(*args, **kwargs)
            logging.info(func.__name__ + " - END")
            return output
        except Exception:
            logging.exception("Bumped into trouble in " + func.__name__)
    return wrapper


def get_row_set_decorator(func):
    logging.debug("Getting results set from " + func.__name__)

    def wrapper(*args, **kwargs):
        input = func(*args, **kwargs)
        output = []

        for i in input:
            output.append(i['rowSet'])
        return output[0]
    return wrapper


def get_result_sets_decorator(func):
    logging.debug("Getting row set from " + func.__name__)

    def wrapper(*args, **kwargs):
        output = func(*args, **kwargs)
        return output['resultSets']
    return wrapper


@basic_log_decorator
def parse_argv(argv_list):
    """
    Count optional positional params for the script and parse them to modify
    the runtime behavior of main using the flags in main.
    :param argv_list: argv list imported from sys
    :return: [first_run, no_mongo, no_postgre, run_date]
    """
    first_run = False
    no_mongo = False
    no_postgre = False
    run_date = None
    is_season_run = False
    season_run_season = None

    output = [first_run, no_mongo, no_postgre, run_date, is_season_run, season_run_season]
    counter = 1
    while counter <= len(output):
        output[counter - 1] = argv_list[counter]
        counter = counter + 1
    print(output)
    return output


@basic_log_decorator
def log_dump(log_container, timestamp, mongo_instance):
    """
    Dumps the logs collected in the log_container list locally and adds them
    to the mongo_instance database.

    :param log_container: list for collecting log entries
    :param timestamp: datetime.datetime.timestamp or whatever you prefer
    :param mongo_instance: mongo db collection path for storing logs
    :return: No return value
    """

    # define database entry using the Logger's stream handler
    db_entry = {"name": "log_" + str(timestamp),
                "output": log_container.getvalue()}

    # add log output to database
    mongo_instance.insert_one(db_entry)


# has 'x' checks


@basic_log_decorator
def has_games(scoreboard_json):
    """
    Checks if there were any matches played on a given date. Use this as the
    condition before running the data getters to avoid empty data dumps.

    :param scoreboard_json: Scoreboard JSON dump
    :return: Boolean - True if there were any matches
    """

    if scoreboard_json is not None and scoreboard_json["resultSets"][6]["rowSet"] is not []:
        logging.debug("Game availability check - END")
        return True


# data getters


def get_data_headers(data):
    """
    Fetches the list of headers for a given rowSet in nba_py.
    :param data: the nba_py module for on the level 1 step above 'rowSet'
    :return: list of headers for the data set
    """
    logging.debug("Fetching headers for data set - START")
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
    logging.debug("Fetching Scoreboard - START")
    try:
        scoreboard_json = scoreboard_instance(month=date.month, day=date.day, year=date.year).json
        logging.debug("Fetching Scoreboard - DONE")
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
    logging.debug("Fetching series standings - START")
    try:
        series_standings = scoreboard_json["resultSets"][2]["rowSet"]
        logging.debug("Fetching series standings - DONE")
        return series_standings
    except Exception:
        logging.exception("Bumped into an error while getting series standings")


def get_last_meeting(scoreboard_json):
    """
    :param scoreboard_json: nba_py Scoreboard JSON dump
    :return: last meeting data for a given game
    """
    logging.debug("Fetching last meetings - START")
    try:
        last_meeting = scoreboard_json["resultSets"][3]["rowSet"]
        logging.debug("Fetching series standings - DONE")
        return last_meeting
    except Exception:
        logging.exception("Bumped into an error while getting last meetings")


def get_conference_standings(scoreboard_json):
    """
    :param scoreboard_json: nba_py Scoreboard JSON dump
    :return: a dict containing west and east conference data for a given date
    """
    logging.debug("Fetching last meetings - END")
    try:
        east_standings = scoreboard_json["resultSets"][4]["rowSet"]
        west_standings = scoreboard_json["resultSets"][5]["rowSet"]
        daily_standings = {"east": east_standings, "west": west_standings}
        logging.debug("Fetching series standings - DONE")
        return daily_standings
    except Exception:
        logging.exception("Bumped into an error while getting conference standings")


@get_row_set_decorator
@get_result_sets_decorator
def get_team_game_logs(team_id, season, nba_py_module):
    """
    Returns a season's worth of game logs for a single NBA team.
    :param team_id: NBA teams id
    :param season: season identifier in the format "YYYY-YY", e.g. '2017-18'
    :param nba_py_module: TeamGameLogs class from the teams module of nba_py
    :return: teamgamelog dict with all the logs for games in the season
    """
    try:
        logging.debug("Trying to get team game log.")
        output_json = nba_py_module(team_id, season).json
        logging.debug("Got team game log. Returning output.")
        return output_json
    except Exception:
        logging.exception("Bumped into exception while getting game log")



def get_season_nba_game_logs(team_list, season, nba_py_module):
    """
    Getter function for fetching the game logs for multiple NBA teams.
    :param team_list: list of nba teams with their ids
    :param season: identifier for the season for which to fetch logs, format: 'YYYY-YY', e.g. '2017-18'
    :param nba_py_module: TeamGameLogs class from teams module in nba_py
    :return: list of dict objects containing game logs for each team
    """
    logging.debug("Getting NBA game logs (multiple teams) - END")
    output = []
    try:
        for t in team_list:
            output.append(get_team_game_logs(t['_id'], season, nba_py_module))
        logging.debug("Getting NBA game logs (multiple teams) - END")
    except Exception:
        logging.exception("Bumped into a problem when getting NBA game logs (multiple teams)")
    return output


@basic_log_decorator
def get_season_run(season, mongo_collection, nba_py_module):
    # imports
    from constants import nba_teams
    from pprint import pprint

    nba_py_mod = nba_py_module

    # get the team_logs

    games = get_season_nba_game_logs(nba_teams, season, nba_py_mod.TeamGameLogs)
    pprint(games)


# data manipulation funcs


def line_score_formatter(raw_data):
    """
    Note: makes use of the scoreboard_line_score_headers constant.
    :param raw_data: line score export list of lists
    :return: formatted data tuple: (pymongo_data, postgresql_data)
    """
    # prepare data schemas
    logging.debug("Formatting the line score data - START")
    # the dict is used as a template for the home/away dicts for mongodb
    mongo_template = {'game_date_est': None,
                      'game_sequence': None,
                      'game_id': None,
                      'team_id': None,
                      'away_or_home': None,
                      'data': None
                      }

    # MongoDB
    try:
        logging.debug("Formatting line score for mongo - START")
        # make copies of the mongodb dict template
        away_team_scoreboard = []
        home_team_scoreboard = []

        # split the home and away team's data from raw_data, keeping the sequence of entries
        away = raw_data[::2]
        home = raw_data[1::2]

        for team in away:
            temp_dict = mongo_template.copy()
            temp_dict["game_date_est"] = team[0]
            temp_dict["game_sequence"] = team[1]
            temp_dict["game_id"] = team[2]
            temp_dict["team_id"] = team[3]
            temp_dict["away_or_home"] = "away"
            temp_dict["data"] = team[4::]
            away_team_scoreboard.append(temp_dict)

        for team in home:
            temp_dict = mongo_template.copy()
            temp_dict["game_date_est"] = team[0]
            temp_dict["game_sequence"] = team[1]
            temp_dict["game_id"] = team[2]
            temp_dict["team_id"] = team[3]
            temp_dict["away_or_home"] = "home"
            temp_dict["data"] = team
            home_team_scoreboard.append(temp_dict)

        # list of dicts in [all-away-teams, all-home-teams] order. Split in 2 by len and zip for pairings
        scoreboard_final_mongodb_flat = away_team_scoreboard + home_team_scoreboard

    except Exception:
        logging.exception("Bumped into an error while formatting line score for mongo")

    """
    # create a list [to keep order] of dict objects for every away team
    for team in away:
        temp_dict = {}
        zipped_data = zip(scoreboard_line_score_headers_lower, team)  # use headers from constants
        for zed in zipped_data:
            temp_dict[zed[0]] = zed[1]  # use the zipped header, datum pairs as key: value
        away_team_scoreboard.append(temp_dict)

    # create a list [to keep order] of dict objects for every home team
    for team in home:
        temp_dict = {}
        zipped_data = zip(scoreboard_line_score_headers_lower, team)  # use headers from constants
        for zed in zipped_data:
            temp_dict[zed[0]] = zed[1]  # use the zipped header, datum pairs as key: value
        home_team_scoreboard.append(temp_dict)

    # create a master dict for both away and home teams' dicts
    scoreboard_final_mongodb = {"away": away_team_scoreboard,
                                "home": home_team_scoreboard}

    """

    # PostgreSQL
    try:
        logging.debug("Formatting line score for PostgreSQL - START")
        scoreboard_final_postgresql = []
        # zip the inner lists of raw_data by 2 for away-home team pairs for every game
        for l in zip(away, home):
            line = l[0] + l[1]
            # validate: each of the elements in the tuple is from the same game sequence
            if line[1] == line[29]:  # 1 and 29 are game sequence id's in the zipped list
                scoreboard_final_postgresql.append(line)
            else:
                logging.error("Bumped into an error: cannot align game sequence")
                return ReferenceError

    except Exception:
        logging.exception("Bumped into an error while formatting line score for PostgreSQL")

    # pack results into output tuple and return
    try:
        output = (scoreboard_final_mongodb_flat, scoreboard_final_postgresql)
    except ReferenceError or ValueError or UnboundLocalError:
        logging.exception("Bumped into an error while packing the formatting results for line score"
                          "")
    logging.debug("Formatting the line score data - END")
    return output


def format_team_list(team_list):
    """

    :param team_list:
    :return:
    """
    formatted_list = []

    for row in team_list:
        new_dict = {"team_id": row[1],
                    "team_abbreviation": row[4]}
        formatted_list.append(new_dict)
    return formatted_list


# dispatch funcs


def mongo_dispatcher(data, db_enpoint):
    pass


def postgresql_dispatcher(data, db_enpoint):
    sql_data_schema = "(id serial PRIMARY KEY, " \
                     "away_game_date_est date, " \
                     "away_game_sequence integer, " \
                     "away_game_id integer, team_id integer, " \
                     "away_team_abbreviation varchar(3)," \
                     "away_team_city_name varchar," \
                     "away_team_wins_losses varchar(6)," \
                     "away_pts_qtr1 integer ," \
                     "away_pts_qtr2 integer, " \
                     "away_pts_qtr3 integer," \
                     "away_pts_qtr4 integer, " \
                     "away_pts_ot1 integer, " \
                     "away_pts_ot2 integer," \
                     "away_pts_ot3 integer," \
                     "away_pts_ot4 integer," \
                     "away_pts_ot5 integer," \
                     "away_pts_ot6 integer," \
                     "away_pts_ot7 integer," \
                     "away_pts_ot8 integer," \
                     "away_pts_ot9 integer," \
                     "away_pts_ot10 integer," \
                     "away_pts integer," \
                     "away_fg_pct double precision," \
                     "away_ft_pct double precision," \
                     "away_fg3_pct double precision," \
                     "away_assists integer," \
                     "away_rebounds integer," \
                     "away_turnovers integer," \
                     "home_game_date_est date, " \
                     "home_game_sequence integer, " \
                     "home_game_id integer, team_id integer, " \
                     "home_team_abbreviation varchar(3)," \
                     "home_team_city_name varchar," \
                     "home_team_wins_losses varchar(6)," \
                     "home_pts_qtr1 integer ," \
                     "home_pts_qtr2 integer, " \
                     "home_pts_qtr3 integer," \
                     "home_pts_qtr4 integer, " \
                     "home_pts_ot1 integer, " \
                     "home_pts_ot2 integer," \
                     "home_pts_ot3 integer," \
                     "home_pts_ot4 integer," \
                     "home_pts_ot5 integer," \
                     "home_pts_ot6 integer," \
                     "home_pts_ot7 integer," \
                     "home_pts_ot8 integer," \
                     "home_pts_ot9 integer," \
                     "home_pts_ot10 integer," \
                     "home_pts integer," \
                     "home_fg_pct double precision," \
                     "home_ft_pct double precision," \
                     "home_fg3_pct double precision," \
                     "home_assists integer," \
                     "home_rebounds integer," \
                     "home_turnovers integer);"
    pass


def seed_teams(mongo_collcection, team_data):
    """
    :param mongo_collcection: mongo collection to seed with data
    :param team_data: data iterable to be inserted
    :return: result of a insert_many() func on the mongo_collection
    """

    # add a 'games' key to the team_data dicts with an empty array container
    for td in team_data:
        td['games'] = []

    logging.info("Seeding mongo collection with constants team data - START")
    try:
        mongo_collcection.insert_many(team_data)
    except Exception:
        logging.exception("Bumped into an error while seeding mono collection with team data")
        return False

    logging.info("Seeding mongo collection with constants team data - END")
    return True


def add_games_from_line_score(mongo_collection, line_score_data):
    """

    :param mongo_collection: the games db array in a collection
    :param line_score_data: line score data formatted for mongo insertion
    :return: True on insertion success
    """
    logging.info("Adding games from line score to teams - START")
    logging.debug("Making (team_id, game_id) tuples - START")
    # make a list of team_id x game_id tuples

    team_id_to_game_id = []

    try:
        for ls in line_score_data:
            team_id_to_game_id.append((ls["team_id"], ls["game_id"]))
    except Exception:
        logging.exception("Bumped into an error while getting team_id x game_id tuples.")
        return False

    # loop over the team_id x game_id tuple and update relevant mongo db entries
    try:
        for tp in team_id_to_game_id:
            # check if the game id wasn't already inserted
            if mongo_collection.find({'_id': tp[0], 'games' : tp[1]}).count() >= 1:
                logging.debug("Game already present in the output mongo db array. Passing.")
                pass
            else:
                # insert game into teams for the correct team
                mongo_collection.update_one({"_id" : tp[0]}, {'$push' : {'games' : tp[1]}})
    except Exception:
        logging.exception("Bumped into an error while getting team_id x game_id tuples.")
        return False

    logging.info("Adding games from line score to teams - END")
    return True


# validators


def mongo_collection_validator (mongo_collection, template_data,
                               mongo_param_to_validate,
                               template_param_to_validate,
                               count_validation,
                               item_validation):
    """
    Performs either one or two validation actions depending on the flags
    passed in the params:
    (1) when count_validation is True, it counts the number of items in
    the mongo_collection and compares to the number of items in the
    template_data structure.
    (2) when item validation is True, it performs the comparison_func
    on each item from both mongo_collection and template_data. (2) will
    only run if (1) returns True.

    :param mongo_collection: mongo_db collection
    :param template_data: data structure to be compared
    :param mongo_param_to_validate: string mongo param to use in the item check
    :param template_param_to_validate: string template param to use in the item check
    :param count_validation: boolean flag
    :param item_validation: boolean flag
    :return: boolean flag
    """
    logging.info("Validating mongo data - START")
    count_flag = False
    item_flag = False

    # count validation
    if count_validation:
        if mongo_collection.count_documents({}) == len(template_data):
            count_flag = True
            logging.debug("Validating mongo data - count validation passed.")
        else:
            logging.warning("Validating mongo data - count validation failed! - END")
            return False


    # item validation
    for i in template_data:
        # cross-check each document in mongo collection against template data, by provided params
        if mongo_collection.find_one({mongo_param_to_validate: i[template_param_to_validate]}) is None:
            print("Here:", mongo_collection.find_one({mongo_param_to_validate: i[template_param_to_validate]}))
            item_flag = False
            logging.warning("Validating mongo data - item validation failed! - END")
            return False
        else:
            logging.debug("Validating mongo data - item validation passed.")
            pass

    item_flag = True
    logging.info("Validating mongo data - all validations passed - END.")
    return count_flag and item_flag

