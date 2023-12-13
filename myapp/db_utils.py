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

def get_owned_orgs(data):
    user_id = data['user_id']
    conn, cur = get_db()
    sql = f"""
    SELECT o.Org_ID, o.Org_name, o.Org_address, o.Org_phone_number, o.Org_founded_date
    FROM ORGANIZATION AS o
        JOIN BUILD AS b ON o.Org_ID = b.Org_ID
    WHERE b.Founder_ID = '{user_id}';
    """
    cur.execute(sql)
    result = cur.fetchall()
    return result




    

    




    
    


