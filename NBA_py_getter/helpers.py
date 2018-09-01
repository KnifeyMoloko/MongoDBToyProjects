

# helper functions for NBA_py_getter

def check_db(name, mongo_client):
    if name in mongo_client.list_database_names():
        print("\n\tHelpers: check_db: "
              "Db name recognized. Continuing with the collection check \n")
        return True
    else:
        print("\n\tHelpers: check_db: "
              "No database named 'NBA_Data_Warehouse' found. Trying to create one.\n")
        return False


def create_db(name, mongo_client):
    print("\n\tHelpers: create_db: Attempting to create 'NBA_Data_Warehouse; db.\n")
    mongo_client.get_database(name)
    print(mongo_client.list_database_names())