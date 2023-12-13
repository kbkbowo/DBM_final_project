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

def validate_org_owner(data):
    user_id = data['user_id']
    org_id = data['org_id']
    conn, cur = get_db()
    sql = f"""
    SELECT COUNT(*)
    FROM BUILD AS b
    WHERE b.Org_ID = '{org_id}' AND b.Founder_ID = '{user_id}';
    """
    cur.execute(sql)
    result = cur.fetchone()
    return result[0] == 1

def get_org_info(org_id):
    conn, cur = get_db()
    sql = f"""
    SELECT o.Org_ID, o.Org_name, o.Org_address, o.Org_phone_number, o.Org_founded_date
    FROM ORGANIZATION AS o
    WHERE o.Org_ID = '{org_id}';
    """
    cur.execute(sql)
    result = cur.fetchone()
    return result

def get_org_founders(org_id):
    conn, cur = get_db()
    sql = f"""
    SELECT u.User_ID, u.User_name, u.User_email, u.User_phone_number, u.User_level
    FROM USER_ AS u
        JOIN BUILD AS b ON u.User_ID = b.Founder_ID
    WHERE b.Org_ID = '{org_id}';
    """
    cur.execute(sql)
    result = cur.fetchall()
    return result




    

    




    
    


