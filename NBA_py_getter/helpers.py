import logging
import functools
import psycopg2
import subprocess


# helper functions for NBA_py_getter


# base decorators


def basic_debug_printer(func):
    @functools.wraps(func)

    def wrapper(*args, **kwargs):
        from pprint import pprint
        to_print = func(*args, **kwargs)
        pprint(to_print)
        return to_print
    return wrapper


def basic_log(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            logging.info(func.__name__ + " - START")
            output = func(*args, **kwargs)
            logging.info(func.__name__ + " - END")
            return output
        except Exception:
            logging.exception("Bumped into trouble in " + func.__name__)
            return 1
    return wrapper


def get_row_set(func):

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logging.debug("Getting results set from " + func.__name__)
        input = func(*args, **kwargs)
        output = []

        for i in input:
            output.append(i['rowSet'])
        return output
    return wrapper


def get_result_sets(func):

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logging.debug("Getting row set from " + func.__name__)
        output = func(*args, **kwargs)
        return output['resultSets']
    return wrapper


def get_headers(func):

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logging.debug("Getting headers for data from " + func.__name__)
        input = func(*args, **kwargs)
        output = []

        for i in input:
            output.append(i['headers'])
        return output
    return wrapper

# email sender



# validators

@basic_log
def season_game_logs_validator(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):

        # input
        logging.debug('Getting validation input from func:' + func.__name__)
        input_data = func(*args, **kwargs)

        # size validation - compare the size of template and data
        logging.debug('Comparing template size to input size')
        assert len(input_data[1]) == len(input_data[0]), "Size mismatch in assertion!"

        # structure/content validation
        logging.debug('Comparing input structure/content to template structure/content')
        fetched_teams_ids = [i[0][0] for i in input_data[0]]
        template_ids = [j['_id'] for j in input_data[1]]
        assert fetched_teams_ids == template_ids, "Structure/content mismatch in assertion!"

        # if both assertions return True, return the game logs data
        logging.info("Season log data validations passed. Data looks good.")
        return input_data[0]
    return wrapper


@basic_log
def mongo_collection_validator(mongo_collection, template_data,
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


@basic_log
def scoreboard_validator(func):
    """

    :param func:
    :return:
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # import date template
        from data_templates import scoreboard_headers as template

        # get data from func
        logging.debug('Getting validation input from func')
        data = func(*args, **kwargs)

        # size validation - compare the size of template and data
        logging.debug('Comparing template size to input size')
        assert(len(data) == len(template)), "Size mismatch in assertion!"

        # structure/content validation - check if elements are not empty lists (no games) or a None
        logging.debug('Comparing input structure/content to template structure/content')
        for i in data:
            for j in i:
                assert(j is not [] and j is not None), "Structure / content mismatch in assertion for" + str(j)

        # if both assertions return True, return the game logs data
        logging.info("Scoreboard data validations passed. Data looks good.")
        return data
    return wrapper


# dispatch funcs

@basic_log
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


@basic_log
def postgresql_dispatcher_local(func):
    """
    This function takes a previous function that returns the postgresql data
    (along with the mongodb data) and dispatches the postgresql portion of
    the data to a postgresql db defined in the config.py file. The required
    config data is: postgresql_username, postgresql_dbname,
    postgresql_host_type as well as a list of table names equal in length
    to the data being processed (i.e. 6 packets of data that need to be
    dispatched to 6 tables in the db) - the tables are defined in config
    as local_postgresql_db. The function also requires that the column names
    (values) for each table be defined in the data_templates.py file.
    This function works as a decorator for the download - validate - format -
    dispatch process.
    The return of this function is the same as it's input (both db's data),
    the function's value being in it's side effects.

    :param func: the function returned by the postgresql_validator function
    or the get_line_score function
    :return: same return as the func input: a tuple (mongodb_data,
    postgresql_data) with preformatted data for both db's dispatchers
    """
    # data dependecies imports
    from config import postgresql_username, postgresql_dbname, \
        postgresql_host_type, local_postgresql_db
    from data_templates import postgresql_line_score_values, \
        postgresql_series_standing_values, \
        postgresql_last_meeting_values,\
        east_conference_standings_by_day_values, \
        west_conference_standings_by_day_values

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # get data from the input function
        data = func(*args, **kwargs)

        # pack data templates into a list for iteration
        values = [postgresql_line_score_values,
                  postgresql_series_standing_values,
                  postgresql_last_meeting_values,
                  east_conference_standings_by_day_values,
                  west_conference_standings_by_day_values]

        # check if the number of data objects is the same as the number of db endpoints
        assert len(local_postgresql_db) == len(data[1]), "Size mismatch between local db endpoints and data points"
        logging.debug("Passed size assertion between postgresql data and local db table count.")

        # create the config string for the psycopg2 connection
        pg_command = "dbname={} user={} host={}"\
            .format(postgresql_dbname, postgresql_username, postgresql_host_type)

        # create psycopg2 connection
        logging.info("Creating pscyopg2 db connection...")
        conn = psycopg2.connect(pg_command)

        # create db cursor
        cursor = conn.cursor()

        # for each table zip it's column names (values) with the relevant data
        zipped = zip(values, data[1])

        # create a counter var, since it's more readable than another for loop
        counter = 0

        logging.debug("Looping over the postgresql data zipped with values. Creating SQL.")
        for z in zipped:
            # assign table name
            dbname = local_postgresql_db[counter]
            counter += 1

            for i in range(0, len(z[1])):
                # z[0] for values in the zipped var,
                # cast z[1][i] as string and slice to remove list brackets

                # create SQL command
                db_command = "INSERT INTO {db} {fields} VALUES ({val});"\
                    .format(db=dbname, fields=z[0], val=str(z[1][i])[1:-1])

                # execute prepared SQL command
                cursor.execute(db_command)

        # commit all of the inserts to db, close cursor and db connection
        logging.info("Committing inserts to local db...")
        conn.commit()
        cursor.close()
        conn.close()
        logging.info("Committing inserts to local db DONE. Closed connection.")

        return data
    return wrapper


def postgresql_dispatcher_remote(func):
    """
    This function takes a previous function that returns the postgresql data
    (along with the mongodb data) and dispatches the postgresql portion of
    the data to a remote postgresql db defined in the config.py file.
    The required config data is: remote_postgresql_db (names), equal in
    length to the data being processed (i.e. 6 packets of data that need to be
    dispatched to 6 tables in the db) - the tables are defined in config
    as remote_postgresql_db. The function also requires that the column names
    (values) for each table be defined in the data_templates.py file.
    This function works as a decorator for the download - validate - format -
    dispatch process.
    The return of this function is the same as it's input (both db's data),
    the function's value being in it's side effects.

    :param func: the function returned by the postgresql_validator function
    or the get_line_score function
    :return: same return as the func input: a tuple (mongodb_data,
    postgresql_data) with preformatted data for both db's dispatchers
    """
    # data dependecies imports
    from config import remote_postgresql_db
    from data_templates import postgresql_line_score_values, \
        postgresql_series_standing_values, \
        postgresql_last_meeting_values,\
        east_conference_standings_by_day_values, \
        west_conference_standings_by_day_values

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # get data from the input function
        data = func(*args, **kwargs)

        # pack data templates into a list for iteration
        values = [postgresql_line_score_values,
                  postgresql_series_standing_values,
                  postgresql_last_meeting_values,
                  east_conference_standings_by_day_values,
                  west_conference_standings_by_day_values]

        # check if the number of data objects is the same as the number of db endpoints
        assert len(remote_postgresql_db) == len(data[1]), "Size mismatch between local db endpoints and data points"
        logging.debug("Passed size assertion between postgresql data and local db table count.")

        # fetch the postgresql db connection details using a bash command
        bash_command = "heroku pg:credentials:url DATABASE -a nba-scores-daily"
        bash_call = subprocess.check_output(bash_command.split(), universal_newlines=True).split("\n")

        # split up the bash command output into meaningful psycopg2 params
        full_connection_url = bash_call[-2]
        logging.debug("Remote postgresql db connection url: {}".format(full_connection_url))
        info_string = bash_call[2][4:-1]

        # establish connection to the db
        conn = psycopg2.connect(info_string)

        # open a cursor to perform db operations
        db_cursor = conn.cursor()

        # for each table zip it's column names (values) with the relevant data
        zipped = zip(values, data[1])

        # create a counter var, since it's more readable than another for loop
        counter = 0

        logging.debug("Looping over the postgresql data zipped with values. Creating SQL for remote db.")
        for z in zipped:
            # assign table name
            dbname = remote_postgresql_db[counter]
            counter += 1

            for i in range(0, len(z[1])):
                # z[0] for values in the zipped var,
                # cast z[1][i] as string and slice to remove list brackets

                # create SQL command
                db_command = "INSERT INTO {db} {fields} VALUES ({val});"\
                    .format(db=dbname, fields=z[0], val=str(z[1][i])[1:-1])

                # execute prepared SQL command
                db_cursor.execute(db_command)

        # commit all of the inserts to db, close cursor and db connection
        logging.info("Committing inserts to remote db...")
        conn.commit()
        db_cursor.close()
        conn.close()
        logging.info("Committing inserts to remote db DONE. Closed connection.")

        return data
    return wrapper


@basic_log
def mongo_dispatcher(data, db_enpoint):
    """

    :param data:
    :param db_enpoint:
    :return:
    """
    assert type(data) is list, "Type assertion failed! Argument is not a list!"
    if len(data) == 0:
        logging.info("Data list for mnogo dispatcher was empty. Returning.")
        return
    elif len(data) == 1:
        logging.debug("Data list for mnogo dispatcher was a singleton. Dispatching one.")
        db_enpoint.insert_one(data[0])
    else:
        #TODO: How to structure the mongodb data dumps best?
        for e in data:
            print(e, "\n")


@basic_log
def postgresql_validator(func):
    """
    Decorator function to validate the output of a data getter vs. PostgreSQL requirements.

    :param func: function that needs to return a data set for a PostgreSQL dump
    :return: same as param if the data passes all validations
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # input data and template imports
        logging.debug("Importing postgresql_line_score_values for validations")
        from data_templates import postgresql_line_score_values as values
        from data_templates import scoreboard_series_standing_template
        from data_templates import last_meeting_template
        from data_templates import east_conf_standings_by_day_template
        from data_templates import west_conf_standings_by_day_template
        data = func(*args, **kwargs)

        # assertions

        # assert if the data provided is a list
        logging.debug("Validating postgresql dump data type")
        assert type(data[1]) is list, "Type assertion failed for PostgreSQL dispatcher data"

        # assert if the provided data list is not empty
        logging.debug("Validating postgresql dump data size")
        assert len(data[1]) != 0, "Zero-length assertion failed for PostgreSQL dispatcher data"

        # assert the equal length of template value tuple and values list for line score
        logging.debug("Validating line score data type")

        assert type(data[1][0][0]) is list, "Type assertion failed for line score"
        logging.debug("Validating line score data size vs. template")
        assert len(data[1][0][0]) == len(values.split(',')), "Size assertion failed for line score"
        logging.debug("Line score validations passed. Data looks good")

        # assert that series standings data conforms to the template
        logging.debug("Validating series standings data type")
        assert type(data[1][1][0]) is list, "Type assertion failed for series standings"
        logging.debug("Validate the series standings size is the same as the number of teams in line score")
        assert len(data[1][1]) == len(data[1][0]), "Size assertion failed for series standings vs. line score"
        logging.debug("Validating series standings entry size")
        assert len(data[1][1][0]) == len(scoreboard_series_standing_template), \
            "Size assertion failed for series standings"
        logging.debug("Series standings validations passed. Data looks good")
        
        # assert that last meeting data conforms to the template
        logging.debug("Validating last meeting data type")
        assert type(data[1][2][0]) is list, "Type assertion failed for last meeting"
        logging.debug("Validating size of last meeting matches size of line score")
        assert len(data[1][2]) == len(data[1][0]), "Size assertion failed for last meeting vs line score"
        logging.debug("Validating last meeting size")
        assert (len(data[1][2][0])) == len(last_meeting_template), "Size assertion failed for last meeting"
        logging.debug("Last meeting validations passed. Data looks good")

        # assert east conference standings by day conform to the template
        logging.debug("Validating east conf standings data type")
        assert type(data[1][3]) is list, "Type assertion failed for east conference standings data"
        logging.debug("Validating size of east conference data matches the number of east conference teams in template")
        assert len(data[1][3]) == len(east_conf_standings_by_day_template), "Size assertion failed for east " \
                                                                            "conference standings data"
        logging.debug("Validating size of east conference standings row data")
        assert len(data[1][3][0]) == len(east_conf_standings_by_day_template[0]), "Size assertion failed for east" \
                                                                                  "conference standings row data"
        logging.debug("East conference standings by day data validations passed. Data looks good")        
        
        # assert east conference standings by day conform to the template
        logging.debug("Validating west conf standings data type")
        assert type(data[1][4]) is list, "Type assertion failed for west conference standings data"
        logging.debug("Validating size of west conference data matches the number of west conference teams in template")
        assert len(data[1][4]) == len(west_conf_standings_by_day_template), "Size assertion failed for west " \
                                                                            "conference standings data"
        logging.debug("Validating size of west conference standings row data")
        assert len(data[1][4][0]) == len(west_conf_standings_by_day_template[0]), "Size assertion failed for west" \
                                                                                  "conference standings row data"
        logging.debug("west conference standings by day data validations passed. Data looks good")

        # if all asserts have passed, the data can be reasonably assumed to be valid
        logging.info("PostgreSQL data validations passed. Data looks good")
        return data
    return wrapper

    #TODO: link local sql db with remote (separate python module
    #TODO: test if remote receives data from local db
    pass

# data getters


@basic_log
def parse_argv(argv_list):
    """
    Count optional positional params for the script and parse them to modify
    the runtime behavior of main using the flags in main.
    :param argv_list: argv list imported from sys
    :return: [first_run, no_mongo, no_postgre, run_date, is_season_run, seasons_run_season]
    """
    # assign default values
    first_run = no_mongo = no_postgre = is_season_run = email = False
    run_date = season_run_season = None
    default_s_values = ("False", "None")

    # assign argv values
    output = [first_run, no_mongo, no_postgre, run_date, is_season_run, season_run_season, email]
    counter = 1

    while counter <= len(output) and len(argv_list) > 1:
        print("Argv value compared: {}".format(argv_list[counter]))
        if argv_list[counter] not in default_s_values:
            if argv_list[counter] == "True":
                output[counter - 1] = True   # first argv param is always the python module name!
            else:
                output[counter-1] = argv_list[counter]
        counter = counter + 1
    return output


@basic_log
def get_line_score(func):
    """
    :param scoreboard_json: nba_py Scoreboard JSON dump
    :return: the LineScore key values from the JSON dump
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # get input from func
        input = func(*args, **kwargs)

        # wrap input into a dict
        output_dict = {'game_header': input[0],
                       'line_score': input[1],
                       'series_standings': input[2],
                       'last_meeting': input[3],
                       'east_conf_standings_by_day': input[4],
                       'west_conf_standings_by_day': input[5],
                       'available': input[6]}

        # pack data for mongo
        mongo_out = []

        # pack data for postgre
        away = output_dict['line_score'][::2]
        home = output_dict['line_score'][1::2]
        zipped_line_score = []

        for l in zip(away, home):
            line = l[0] + l[1]
            # validate: each of the elements in the tuple is from the same game sequence
            # 1 and 29 are game sequence id's in the zipped list
            assert line[1] == line[29], "Game id mismatch in assertion"
            zipped_line_score.append(line)

        postgresql_out = [
            zipped_line_score,
            output_dict['series_standings'],
            output_dict['last_meeting'],
            output_dict['east_conf_standings_by_day'],
            output_dict['west_conf_standings_by_day']
        ]

        #TODO: add mongo output

        return mongo_out, postgresql_out
    return wrapper


@postgresql_dispatcher_remote
@postgresql_dispatcher_local
@postgresql_validator
@get_line_score
@scoreboard_validator
@get_row_set
@get_result_sets
@basic_log
def get_scoreboard(date, scoreboard_instance):
    """
    :param scoreboard_instance: nba_py Scoreboard instance
    :param date: datetime.datetime object as the date we query for (-1 to get yesterday scores)
    :return: nba_py Scoreboard object
    """
    scoreboard_json = scoreboard_instance(month=date.month, day=date.day - 1, year=date.year).json
    return scoreboard_json


@get_row_set
@get_result_sets
@basic_log
def get_team_game_logs(team_id, season, nba_py_module):
    """
    Returns a season's worth of game logs for a single NBA team.
    :param team_id: NBA teams id
    :param season: season identifier in the format "YYYY-YY", e.g. '2017-18'
    :param nba_py_module: TeamGameLogs class from the teams module of nba_py
    :return: teamgamelog dict with all the logs for games in the season
    """
    logging.debug("Trying to get team game log for team id:" + str(team_id))
    output_json = nba_py_module(team_id, season).json
    return output_json


@basic_log
def get_season_nba_game_logs(team_list, season, nba_py_module):
    """
    Getter function for fetching the game logs for multiple NBA teams.
    :param team_list: list of nba teams as dicts, with their ids under key: _id
    :param season: identifier for the season for which to fetch logs, format: 'YYYY-YY', e.g. '2017-18'
    :param nba_py_module: TeamGameLogs class from teams module in nba_py
    :return: list of dict objects containing game logs for each team
    """
    output = [get_team_game_logs(t['_id'], season, nba_py_module) for t in team_list]
    return output


@season_game_logs_validator
@basic_log
def get_season_run(season, mongo_collection, nba_py_module):
    # imports
    from config import nba_teams

    nba_py_mod = nba_py_module

    # get the team_logs
    games = get_season_nba_game_logs(nba_teams, season, nba_py_mod.TeamGameLogs)
    return games, nba_teams, mongo_collection


# data manipulation funcs

@basic_log
def seed_teams(mongo_collection, team_data):
    """
    :param mongo_collcection: mongo collection to seed with data
    :param team_data: data iterable to be inserted
    :return: result of a insert_many() func on the mongo_collection
    """
    #TODO: Rethink this. How to link teams and games with most sense?
    # add a 'games' key to the team_data dicts with an empty array container
    for td in team_data:
        td['games'] = []

    mongo_collection.insert_many(team_data)
    return True


def send_logs_to_email(to_send):
    """

    :param to_send:
    :return:
    """
    assert to_send is not None, "The body of the e-mail was set to None"

    # imports

    import smtplib
    from email.mime.text import MIMEText

    # prompt user for address and password
    username = input("Please provide e-mail address to send the e-mail: ")
    password = input("Please provide e-mail password: ")

    # define the e-mail message
    msg = MIMEText(str(to_send), 'plain')
    msg['From'] = username
    msg['To'] = username
    msg['Subject'] = 'NBA_py_getter log'

    # create SMTP session
    s = smtplib.SMTP('smtp.gmail.com', 587)

    # start TLS
    s.starttls()

    # login
    s.login(username, password)

    # send the mail
    s.sendmail(username, username, msg.as_string())

    # terminate session
    s.quit()
