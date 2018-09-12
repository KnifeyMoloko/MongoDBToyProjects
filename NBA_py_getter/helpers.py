

# helper functions for NBA_py_getter
def add_log_entry(timestamp, event, stack_instance=stack(), log_entry, log_container):
    """
    Adds an entry to the log database and saves a log entry to
    the local log file. Logs are timestamped and in JSON format.

    :param timestamp: datetime.datetime timestamp
    :param event: string describing the type of event
    :param stack_instance: inspect.stack instance, defaults to a call to stack()
    :param log_entry: string for the custom log entry text
    :param log_container: list for the logs raised while running
    :return: No return value
    """

    # create new log entry
    new_entry = {"timestamp": timestamp,
                 "event": event,
                 "module": stack_instance[0][1],
                 "function": stack_instance[0][3],
                 "line" : stack_instance[0][2],
                 "context" : stack_instance[0][4],
                 "log_entry": log_entry}

    # append new entry to the log container
    log_container.append(new_entry)


def log_dump(log_container, pathlib_instance, timestamp, mongo_instance):
    """
    Dumps the logs collected in the log_container list locally and adds them
    to the mongo_instance database.

    :param log_container: list for collecting log entries
    :param pathlib_instance: pathlib path for local log storage
    :param timestamp: datetime.datetime.timestamp or whatever you prefer
    :param mongo_instance: mongo db collection path for storing logs
    :return: No return value
    """
    # define local logs path
    log_dir = pathlib_instance / 'logs'
    # attempt to create log dir if not yet created
    log_dir.mkdir(parents=True, exist_ok=True)
    # define log file path
    file_path = log_dir.joinpath('log_' + str(timestamp))

    # create write output line by line from the log entries
    output = ""
    for i in log_container:
        output += str(i) + "\n"

    # write log output to local file
    file_path.write_text(output)

    # define database entry
    db_entry = {"name": "log_" + str(timestamp),
                "output": output}
    # add log output to database
    mongo_instance.insert_one(db_entry)
