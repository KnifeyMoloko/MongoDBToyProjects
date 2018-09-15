

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
    output = log_container.getvalue().format()

    # define database entry
    db_entry = {"name": "log_" + str(timestamp),
                "output": output}
    # add log output to database
    mongo_instance.insert_one(db_entry)
