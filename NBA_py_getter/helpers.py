

# helper functions for NBA_py_getter
def add_log_entry(timestamp, header, module, func, log_entry, log_container):
    """Adds an entry to the log database and saves a log entry to
    the local log file. Logs are timestamped and in JSON format."""

    # create new log entry
    new_entry = {"timestamp": timestamp,
                 "header": header,
                 "module": module,
                 "function": func,
                 "log_entry": log_entry}

    # append new entry to the log container
    log_container.append(new_entry)


def log_dump(log_container, pathlib_instance, timestamp, mongo_instance):
    # define local logs path
    log_dir = pathlib_instance / 'logs'
    # attempt to create log dir if not yet created
    log_dir.mkdir(parents=True, exist_ok=True)
    # define log file path
    file_path = log_dir.joinpath('log_'+ str(timestamp))

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
