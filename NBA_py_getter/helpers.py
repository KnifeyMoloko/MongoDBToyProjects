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

    logging.debug("Log dump - START")

    # define database entry using the Logger's stream handler
    db_entry = {"name": "log_" + str(timestamp),
                "output": log_container.getvalue().format()}
    # add log output to database
    try:
        mongo_instance.insert_one(db_entry)
        logging.debug("Log dump - END")
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
    logging.debug("Game availability check - START")
    try:
        if scoreboard_json["resultSets"][6]["rowSet"] is not []:
            logging.debug("Game availability check - END")
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
    logging.debug("Fetching last meetings - START")
    try:
        east_standings = scoreboard_json["resultSets"][4]["rowSet"]
        west_standings = scoreboard_json["resultSets"][5]["rowSet"]
        daily_standings = {"east": east_standings, "west": west_standings}
        logging.debug("Fetching series standings - DONE")
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

    logging.info("Adding games from line score to teams - START")
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

