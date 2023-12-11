import psycopg2

db_ip = "database-1.ci4rlgsoozib.ap-southeast-2.rds.amazonaws.com"
pw = "owokbc0416"

# Connect to an existing database
conn = psycopg2.connect(host=db_ip, dbname="dbm_final", user="kbkbowo", password=pw, port=5432)

# Open a cursor to perform database operations
cur = conn.cursor()

# Create DB