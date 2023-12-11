import psycopg2
import yaml
import pandas as pd

def get_db(config="configs/db_aws.yaml"):
    # Read config file
    with open(config, "r") as f:
        config = yaml.load(f, Loader=yaml.FullLoader)

    # Connect to an existing database
    conn = psycopg2.connect(host=config["ip"], dbname=config["name"], user=config["user"], password=config["pw"], port=5432)

    # Open a cursor to perform database operations
    cur = conn.cursor()

    return conn, cur

def validate_pw(form, username, pw):
    conn, cur = get_db()
    sql = f"""
    SELECT *
    FROM USER_ AS u
    WHERE u.User_email = '{username}' AND u.User_ID = '{pw}';
    """
    # check if exists   
    cur.execute(sql)
    result = cur.fetchall()
    if len(result) == 0:
        return False
    else:
        return True



    
    


