import psycopg2

DB_USER = "mox_rtools"
DB_PASSWORD = "VI7QNfDvJtmnrpQ5"
DB_NAME = "mox_boards"

# Whole application database connection
dbconnection = None


def db_connect():
    "Connect application to database"
    global dbconnection
    dbconnection = psycopg2.connect(
        dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD)
