import psycopg2
import yaml
import pandas as pd
import json

def get_db(config="configs/db_aws.yaml"):
    # Read config file
    with open(config, "r") as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
    # Connect to an existing database
    conn = psycopg2.connect(host=config["ip"], dbname=config["name"], user=config["user"], password=config["pw"], port=5432)
    # Open a cursor to perform database operations
    cur = conn.cursor()

    return conn, cur

conn, cur = get_db()

def get_owned_orgs(data):
    user_id = data['user_id']
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
    sql = f"""
    SELECT COUNT(*)
    FROM BUILD AS b
    WHERE b.Org_ID = '{org_id}' AND b.Founder_ID = '{user_id}';
    """
    cur.execute(sql)
    result = cur.fetchone()
    return result[0] == 1

def get_org_info(org_id):
    sql = f"""
    SELECT o.Org_ID, o.Org_name, o.Org_address, o.Org_phone_number, o.Org_founded_date
    FROM ORGANIZATION AS o
    WHERE o.Org_ID = '{org_id}';
    """
    cur.execute(sql)
    result = cur.fetchone()
    return result

def get_org_founders(org_id):
    sql = f"""
    SELECT u.User_ID, u.User_name, u.User_email, u.User_phone_number, u.User_level
    FROM USER_ AS u
        JOIN BUILD AS b ON u.User_ID = b.Founder_ID
    WHERE b.Org_ID = '{org_id}';
    """
    cur.execute(sql)
    result = cur.fetchall()
    return result

def delete_org(org_id):
    sql = f"""
    DELETE FROM ORGANIZATION
    WHERE Org_ID = '{org_id}';
    """
    cur.execute(sql)
    conn.commit()
    return True

def get_attending_orgs(user_id):
    sql = f"""
    SELECT o.Org_ID, o.Org_name, o.Org_address, o.Org_phone_number, o.Org_founded_date
    FROM ORGANIZATION AS o
        JOIN JOIN_ AS j ON o.Org_ID = j.Org_ID
    WHERE j.User_ID = '{user_id}'
        AND j.Quit_date IS NULL;
    """
    cur.execute(sql)
    result = cur.fetchall()
    return result

def leave_org(user_id, org_id):
    sql = f"""
    UPDATE JOIN_
    SET Quit_date = CURRENT_DATE
    WHERE Org_ID = '{org_id}' AND User_ID = '{user_id}';
    """
    cur.execute(sql)
    conn.commit()
    return True

def join_org(user_id, org_id):
    sql = f"""
    INSERT INTO JOIN_
    VALUES ('{user_id}', '{org_id}', CURRENT_DATE, NULL);
    """
    cur.execute(sql)
    conn.commit()
    return True

def get_org_events(org_id):
    # sql = f"""
    # SELECT e.Event_ID, e.Event_date, e.Event_name, e.Capacity, e.Event_location, e.Event_description, e.Start_time, e.End_time
    # FROM EVENT AS e
    #     JOIN HOLD AS h ON e.Event_ID = h.Event_ID
    # WHERE h.Org_ID = '{org_id}'
    # ORDER BY e.Event_date DESC;
    # """
    # additionally, get the number of attendees for each event
    sql = f"""
    SELECT e.Event_ID, e.Event_date, e.Event_name, e.Capacity, e.Event_location, e.Event_description, e.Start_time, e.End_time, COUNT(a.User_ID) AS Attendees
    FROM EVENT AS e
        JOIN HOLD AS h ON e.Event_ID = h.Event_ID
        LEFT JOIN ATTEND AS a ON e.Event_ID = a.Event_ID
    WHERE h.Org_ID = '{org_id}'
    GROUP BY e.Event_ID
    ORDER BY e.Event_date DESC;
    """

    cur.execute(sql)
    result = cur.fetchall()
    return result

def get_event_info(event_id):
    sql = f"""
    SELECT e.Event_ID, e.Event_date, e.Event_name, e.Capacity, e.Event_location, e.Event_description, e.Start_time, e.End_time
    FROM EVENT AS e
    WHERE e.Event_ID = '{event_id}';
    """
    cur.execute(sql)
    result = cur.fetchone()
    return result

def delete_event(event_id):
    sql = f"""
    DELETE FROM EVENT
    WHERE Event_ID = '{event_id}';
    """
    cur.execute(sql)
    conn.commit()
    return True

def get_user_events(user_id):
    sql = f"""
    SELECT e.Event_ID, e.Event_date, e.Event_name, e.Capacity, e.Event_location, e.Event_description, e.Start_time, e.End_time
    FROM EVENT AS e
        JOIN ATTEND AS a ON e.Event_ID = a.Event_ID
    WHERE a.User_ID = '{user_id}'
    ORDER BY e.Event_date DESC;
    """
    cur.execute(sql)
    result = cur.fetchall()
    return result

def join_event(user_id, event_id):
    ### need to be careful about the capacity
    conn, cur = get_db()
    sql = f"""
    SELECT * FROM ATTEND FOR UPDATE;

    INSERT INTO ATTEND
    VALUES ('{user_id}', '{event_id}');
    """
    cur.execute(sql)
    # make sure the event is not full
    sql = f"""
    SELECT COUNT(*)
    FROM ATTEND
    WHERE Event_ID = '{event_id}';
    """
    cur.execute(sql)
    count = cur.fetchone()
    sql = f"""
    SELECT Capacity
    FROM EVENT
    WHERE Event_ID = '{event_id}';
    """
    cur.execute(sql)
    capacity = cur.fetchone()
    if count[0] > capacity[0]:
        conn.rollback()
        return False
    else:
        conn.commit()
        return True

def get_org_animals(org_id):
    sql = f"""
    SELECT a.Animal_ID, a.Animal_type, a.Animal_name, a.Animal_status, a.Reported_date, a.Reported_reason, a.Reported_location, a.Shelter_date, a.Adopt_user_ID, a.Report_user_ID
    FROM ANIMAL AS a
    WHERE a.Org_ID = '{org_id}'
    ORDER BY a.Shelter_date DESC;
    """
    cur.execute(sql)
    result = cur.fetchall()
    return result

def get_unsheltered_animals():
    sql = f"""
    SELECT a.Animal_ID, a.Animal_type, a.Animal_name, a.Animal_status, a.Reported_date, a.Reported_reason, a.Reported_location, a.Shelter_date, a.Adopt_user_ID, a.Report_user_ID
    FROM ANIMAL AS a
    WHERE a.Org_ID IS NULL
    ORDER BY a.Reported_date;
    """
    cur.execute(sql)
    result = cur.fetchall()
    return result

def shelter_animal(org_id, animal_id):
    try:
        sql = f"""
        UPDATE ANIMAL
        SET Org_ID = '{org_id}', Shelter_date = CURRENT_DATE
        WHERE Animal_ID = '{animal_id}';
        """
        cur.execute(sql)
        conn.commit()
        return True
    except:
        conn.rollback()
        return False

def get_animal_info(animal_id):
    sql = f"""
    SELECT a.Animal_ID, a.Animal_type, a.Animal_name, a.Animal_status, a.Reported_date, a.Reported_reason, a.Reported_location, a.Shelter_date, a.Adopt_user_ID, a.Report_user_ID
    FROM ANIMAL AS a
    WHERE a.Animal_ID = '{animal_id}';
    """
    cur.execute(sql)
    result = cur.fetchone()
    return result

