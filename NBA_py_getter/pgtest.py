import os
import psycopg2
import subprocess

# fetch the postgresql db connection details using a bash command
bash_command = "heroku pg:credentials:url DATABASE -a nba-scores-daily"
localhost_commad = "dbname=newton user=newton host=/tmp/"
bash_call = subprocess.check_output(bash_command.split(), universal_newlines=True).split("\n")

# split up the bash command output into meaningful psycopg2 params
full_connection_url = bash_call[-2]
info_string = bash_call[2][4:-1]

# establish connection to the db

conn = psycopg2.connect(info_string)

#conn = psycopg2.connect(localhost_commad)

# open a cursor to perform db operations
db_cursor = conn.cursor()

# use cursor to execute SQL commands on the db
#db_cursor.execute("CREATE TABLE test1 (id serial PRIMARY KEY, num integer, data varchar);")
db_cursor.execute("INSERT INTO test1 (num, data) VALUES (%s, %s)", (100, "this is a test1"))
db_cursor.execute("SELECT * FROM test1;")


#db_cursor.execute("SELECT * FROM cities;")

# get the results from the cursor
print(db_cursor.fetchone())

# commit the changes made by the cursor to the remote db
conn.commit()

# close cursor
db_cursor.close()

# close connection
conn.close()
