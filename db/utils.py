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

def get_sql(task):
    with open(f"sql_commands.yaml", "r") as f:
        sql = yaml.load(f, Loader=yaml.FullLoader)[task]
    return sql

def create_tables(conn, cur):
    sql_commands = [
    """
    CREATE TABLE USER_ ( 
        User_ID VARCHAR(20) PRIMARY KEY,
        User_name VARCHAR(20) NOT NULL,
        User_phone_number CHAR(16) NOT NULL,
        User_email VARCHAR(40) NOT NULL,
        User_level VARCHAR(10) NOT NULL CHECK (User_level IN ('User', 'Admin'))
    );""",

    """
    CREATE TABLE EVENT (
        Event_ID VARCHAR(20) PRIMARY KEY,
        Event_date DATE,
        Event_name VARCHAR(50) NOT NULL,
        Capacity INT,
        Event_location VARCHAR(100),
        Event_description VARCHAR(200),
        Start_time TIME NOT NULL,
        End_time TIME NOT NULL
    );""",

    """
    CREATE TABLE ORGANIZATION (
        Org_ID VARCHAR(20) PRIMARY KEY,
        Org_name VARCHAR(50) NOT NULL,
        Org_address VARCHAR(100) NOT NULL,
        Org_phone_number CHAR(16) NOT NULL,
        Org_founded_date DATE NOT NULL
    );""",

    """
    CREATE TABLE ATTEND (
        User_ID VARCHAR(20),
        Event_ID VARCHAR(20),
        PRIMARY KEY (User_ID, Event_ID),
        FOREIGN KEY (User_ID) REFERENCES USER_(User_ID) ON DELETE CASCADE ON UPDATE CASCADE,
        FOREIGN KEY (Event_ID) REFERENCES EVENT(Event_ID) ON DELETE CASCADE ON UPDATE CASCADE
    );""",

    """
    CREATE TABLE HOLD (
        Event_ID VARCHAR(20),
        Org_ID VARCHAR(20),
        PRIMARY KEY (Event_ID, Org_ID),
        FOREIGN KEY (Event_ID) REFERENCES EVENT(Event_ID) ON DELETE CASCADE ON UPDATE CASCADE,
        FOREIGN KEY (Org_ID) REFERENCES ORGANIZATION(Org_ID) ON DELETE CASCADE ON UPDATE CASCADE
    );""",

    """
    CREATE TABLE JOIN_ (
        User_ID VARCHAR(20),
        Org_ID VARCHAR(20),
        Join_date DATE,
        Quit_date DATE,
        PRIMARY KEY (User_ID, Org_ID, Join_date),
        FOREIGN KEY (User_ID) REFERENCES USER_(User_ID) ON DELETE CASCADE ON UPDATE CASCADE,
        FOREIGN KEY (Org_ID) REFERENCES ORGANIZATION(Org_ID) ON DELETE CASCADE ON UPDATE CASCADE
    );""",

    """
    CREATE TABLE BUILD (
        Org_ID VARCHAR(20),
        Founder_ID VARCHAR(20),
        PRIMARY KEY (Org_ID, Founder_ID),
        FOREIGN KEY (Org_ID) REFERENCES ORGANIZATION(Org_ID) ON DELETE CASCADE ON UPDATE CASCADE,
        FOREIGN KEY (Founder_ID) REFERENCES USER_(User_ID) ON DELETE CASCADE ON UPDATE CASCADE
    );""",

    """
    CREATE TABLE DONATE (
        User_ID VARCHAR(20),
        Org_ID VARCHAR(20),
        Donate_date DATE NOT NULL,
        D_item_name VARCHAR(20) NOT NULL,
        Donate_amount INT NOT NULL,
        PRIMARY KEY (User_ID, Org_ID, Donate_date),
        FOREIGN KEY (User_ID) REFERENCES USER_(User_ID) ON DELETE CASCADE ON UPDATE CASCADE,
        FOREIGN KEY (Org_ID) REFERENCES ORGANIZATION(Org_ID) ON DELETE CASCADE ON UPDATE CASCADE
    );""",

    """
    CREATE TABLE LEND_SUPPLEMENT (
        Org_ID_out VARCHAR(20),
        Org_ID_in VARCHAR(20),
        Supplement_name VARCHAR(20) NOT NULL,
        Supplement_quantity INT NOT NULL,
        Lend_date DATE,
        Expected_return_date DATE NOT NULL,
        PRIMARY KEY (Org_ID_out, Org_ID_in, Lend_date),
        FOREIGN KEY (Org_ID_out) REFERENCES ORGANIZATION(Org_ID) ON DELETE CASCADE ON UPDATE CASCADE,
        FOREIGN KEY (Org_ID_in) REFERENCES ORGANIZATION(Org_ID) ON DELETE CASCADE ON UPDATE CASCADE
    );""",

    """
    CREATE TABLE ANIMAL (
        Animal_ID VARCHAR(20) PRIMARY KEY,
        Animal_type VARCHAR(20) NOT NULL,
        Animal_name VARCHAR(20) NOT NULL,
        Animal_status VARCHAR(10) NOT NULL CHECK (Animal_status IN ('Adopted', 'Sheltered', 'Released')),
        Reported_date DATE NOT NULL,
        Reported_reason VARCHAR(200) NOT NULL,
        Reported_location VARCHAR(100) NOT NULL,
        Shelter_date DATE,
        Adopt_User_ID VARCHAR(20),
        Report_User_ID VARCHAR(20),
        Org_ID VARCHAR(20) NOT NULL,
        FOREIGN KEY (Adopt_User_ID) REFERENCES USER_(User_ID) ON DELETE CASCADE ON UPDATE CASCADE,
        FOREIGN KEY (Report_User_ID) REFERENCES USER_(User_ID) ON DELETE CASCADE ON UPDATE CASCADE,
        FOREIGN KEY (Org_ID) REFERENCES ORGANIZATION(Org_ID) ON DELETE CASCADE ON UPDATE CASCADE
    );""",

    """
    CREATE TABLE HOSPITAL (
        Hospital_ID VARCHAR(10) PRIMARY KEY,
        Hospital_Name VARCHAR(100) NOT NULL,
        Hospital_Address VARCHAR(100) NOT NULL,
        Hospital_phone_number VARCHAR(16) NOT NULL
    );""",

    """
    CREATE TABLE SENT_TO (
        Animal_ID VARCHAR(10),
        Hospital_ID VARCHAR(10),
        Org_ID VARCHAR(20),
        Sent_date DATE,
        Return_date DATE,
        Sent_reason VARCHAR(200) NOT NULL,
        PRIMARY KEY (Animal_ID, Hospital_ID, Sent_date),
        FOREIGN KEY (Animal_ID) REFERENCES ANIMAL(Animal_ID) ON DELETE CASCADE ON UPDATE CASCADE,
        FOREIGN KEY (Hospital_ID) REFERENCES HOSPITAL(Hospital_ID) ON DELETE CASCADE ON UPDATE CASCADE,
        FOREIGN KEY (Org_ID) REFERENCES ORGANIZATION(Org_ID) ON DELETE CASCADE ON UPDATE CASCADE
    );"""]

    # Execute a command: this creates a new table
    for sql in sql_commands:
        try: 
            cur.execute(sql)
            conn.commit()
        except Exception as e:
            conn.rollback()
            print(e)
            print(f"Failed to execute {sql}, skipping...")

    cur.execute("""
        SELECT pg_tables.tablename
        FROM pg_catalog.pg_tables
        WHERE schemaname != 'pg_catalog' AND 
            schemaname != 'information_schema';
    """
    )
    # Show the tables
    tables = pd.DataFrame(cur.fetchall(), columns=['table_name'])
    print("\ntables\n", tables)

def insert_data_from_xlsx(conn, cur, xlsx_path="../data/data.xlsx"):
    table_names_map = {
        "users": "USER_",
        "events": "EVENT",
        "orgs": "ORGANIZATION",
        "hospitals": "HOSPITAL",
        "animals": "ANIMAL",
        "attends": "ATTEND",
        "holds": "HOLD",
        "joins": "JOIN_",
        "builds": "BUILD",
        "donates": "DONATE",
        "lend_supplements": "LEND_SUPPLEMENT",
        "sent_tos": "SENT_TO"
    }
    df = pd.read_excel(xlsx_path, sheet_name=None)
    
    


