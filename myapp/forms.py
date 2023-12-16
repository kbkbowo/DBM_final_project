from django import forms
from .db_utils import get_db, full_transaction
import pandas.io.sql as sqlio
import time
import json
import dateutil.parser as date_parser

class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

    def execute_action(self):
        conn, cur = get_db()
        username = self.cleaned_data['username']
        password = self.cleaned_data['password']
        sql = f"""
        SELECT *
        FROM USER_ AS u
        WHERE u.User_email = '{username}' AND u.User_ID = '{password}';
        """
        # check if exists
        cur.execute(sql)
        result = cur.fetchall()
        if len(result) == 0:
            return False
        else:
            self.user_data = result[0]
            return True

class SignupForm(forms.Form):
    username = forms.CharField()
    phone = forms.CharField()
    email = forms.CharField()

    @full_transaction
    def execute_action(self):
        _, cur = get_db()
        username = self.cleaned_data['username']
        phone = self.cleaned_data['phone']
        email = self.cleaned_data['email']

        sql = f"""
        SELECT *
        FROM USER_ AS u
        WHERE u.User_email = '{email}';
        """
        # check if exists
        cur.execute(sql)
        result = cur.fetchall()

        assert len(result) == 0 # if exists, raise error

        sql = """
        SELECT User_ID
        FROM USER_
        ORDER BY User_ID::int DESC
        LIMIT 1;
        """
        cur.execute(sql)
        result = cur.fetchall()
        next_id = int(result[0][0]) + 1
        # Insert the user
        sql = f"""
        INSERT INTO USER_ (User_ID, User_name, User_phone_number, User_email, User_level)
        VALUES ('{next_id}', '{username}', '{phone}', '{email}', 'User');
        """
        cur.execute(sql)
        self.user_data = [next_id, username, phone, email, 'User']
        return True

    @full_transaction
    def update_user_data(self, user_id):
        _, cur = get_db()
        username = self.cleaned_data['username']
        phone = self.cleaned_data['phone']
        email = self.cleaned_data['email']
        sql = f"""
        SELECT *
        FROM USER_ AS u
        WHERE u.User_email = '{email}'
            AND u.User_ID != '{user_id}';
        """
        # check if exists
        cur.execute(sql)
        result = cur.fetchall()

        assert len(result) == 0 # if exists, raise error

        sql = f"""
        UPDATE USER_
        SET User_name = '{username}', User_phone_number = '{phone}', User_email = '{email}'
        WHERE User_ID = '{user_id}';
        """
        cur.execute(sql)
        self.user_data = [user_id, username, phone, email]
        return True
        
class QueryUsersForm(forms.Form):
    user_id = forms.CharField(required=False)
    user_name = forms.CharField(required=False)
    phone = forms.CharField(required=False)
    email = forms.CharField(required=False)
    # options {Any, User, Admin}
    level = forms.ChoiceField(choices=[('', 'Any'), ('User', 'User'), ('Admin', 'Admin')], required=False)

    def execute_action(self):
        _, cur = get_db()
        user_id = self.cleaned_data['user_id']
        user_name = self.cleaned_data['user_name']
        phone = self.cleaned_data['phone']
        email = self.cleaned_data['email']
        level = self.cleaned_data['level']
        sql = f"""
        SELECT *
        FROM USER_ AS u
        WHERE u.User_id LIKE '%{user_id}%' 
            AND u.User_name LIKE '%{user_name}%' 
            AND u.User_phone_number LIKE '%{phone}%' 
            AND u.User_email LIKE '%{email}%' 
            AND u.User_level LIKE '%{level}%';
        """
        cur.execute(sql)
        result = cur.fetchall()
        self.user_data = result
        return True

    def execute_action_details(self):
        conn, cur = get_db()
        user_id = self.cleaned_data['user_id']
        user_name = self.cleaned_data['user_name']
        phone = self.cleaned_data['phone']
        email = self.cleaned_data['email']
        level = self.cleaned_data['level']
        # get the count of joined_orgs, founded_orgs, past_events, upcoming_events, reported_animals, adopted_animals, donated_items
        sql = f"""
        WITH SELECTED_USERS AS (
            SELECT u.User_ID, u.User_name, u.User_phone_number, u.User_email, u.User_level
            FROM USER_ AS u
            WHERE u.User_id LIKE '%{user_id}%'
                AND u.User_name LIKE '%{user_name}%'
                AND u.User_phone_number LIKE '%{phone}%'
                AND u.User_email LIKE '%{email}%'
                AND u.User_level LIKE '%{level}%'
        )

        SELECT su.User_ID, su.User_name, su.User_phone_number as User_phone, su.User_email, su.User_level, 
            COUNT(DISTINCT j.Org_ID) AS joined_orgs,
            COUNT(DISTINCT b.Org_ID) AS founded_orgs,
            COUNT(DISTINCT e.Event_ID) AS past_events,
            COUNT(DISTINCT e2.Event_ID) AS upcoming_events,
            COUNT(DISTINCT a.Animal_ID) AS reported_animals,
            COUNT(DISTINCT a2.Animal_ID) AS adopted_animals,
            COUNT(DISTINCT d.Donor_ID) AS donations
        FROM SELECTED_USERS AS su
            LEFT JOIN JOIN_ AS j ON su.User_ID = j.User_ID
            LEFT JOIN BUILD AS b ON su.User_ID = b.Founder_ID
            LEFT JOIN ATTEND AS at ON su.User_ID = at.User_ID
            LEFT JOIN EVENT AS e ON at.Event_ID = e.Event_ID AND e.Event_date < CURRENT_DATE
            LEFT JOIN EVENT AS e2 ON at.Event_ID = e2.Event_ID AND e2.Event_date >= CURRENT_DATE
            LEFT JOIN ANIMAL AS a ON su.User_ID = a.Report_user_id
            LEFT JOIN ANIMAL AS a2 ON su.User_ID = a2.Adopt_user_id
            LEFT JOIN DONATE AS d ON su.User_ID = d.Donor_ID
        GROUP BY su.User_ID, su.User_name, su.User_phone_number, su.User_email, su.User_level;
        """
        db = sqlio.read_sql_query(sql, conn)
        return db.to_records()

# org_id, org_name, org_address, org_phone, org_founded_date, founder_id, founder_name
class ManageOrgsForm(forms.Form):
    org_id = forms.CharField(required=False)
    org_name = forms.CharField(required=False)
    org_address = forms.CharField(required=False)
    org_phone = forms.CharField(required=False)
    org_founded_date_after = forms.DateField(required=False)
    org_founded_date_before = forms.DateField(required=False)
    founder_id = forms.CharField(required=False)
    founder_name = forms.CharField(required=False)
    action = forms.ChoiceField(choices=[('Act0', 'Act0'), ('Act1', 'Act1')], required=False)

    def query_search(self):
        org_id = self.cleaned_data['org_id']
        org_name = self.cleaned_data['org_name']
        org_address = self.cleaned_data['org_address']
        org_phone = self.cleaned_data['org_phone']
        org_founded_date_after = self.cleaned_data['org_founded_date_after']
        org_founded_date_before = self.cleaned_data['org_founded_date_before']
        founder_id = self.cleaned_data['founder_id']
        founder_name = self.cleaned_data['founder_name']
        conn, cur = get_db()
        sql = f"""
        SELECT DISTINCT o.Org_ID::int, o.Org_name, o.Org_address, o.Org_phone_number, o.Org_founded_date
        FROM ORGANIZATION AS o
            JOIN BUILD AS b ON o.Org_ID = b.Org_ID
            JOIN USER_ AS u ON b.Founder_ID = u.User_ID
        WHERE o.Org_ID LIKE '%{org_id}%'
            AND o.Org_name LIKE '%{org_name}%'
            AND o.Org_address LIKE '%{org_address}%'
            AND o.Org_phone_number LIKE '%{org_phone}%'
            AND o.Org_founded_date >= '{org_founded_date_after if org_founded_date_after else '0001-01-01'}'
            AND o.Org_founded_date <= '{org_founded_date_before if org_founded_date_before else '9999-12-31'}'
            AND b.Founder_ID LIKE '%{founder_id}%'
            AND u.User_name LIKE '%{founder_name}%'
        ORDER BY o.Org_ID::int DESC;
        """
        df = sqlio.read_sql_query(sql, conn).to_records()
        self.org_data = df
        return df

    def query_search_detailed(self):
        org_id = self.cleaned_data['org_id']
        org_name = self.cleaned_data['org_name']
        org_address = self.cleaned_data['org_address']
        org_phone = self.cleaned_data['org_phone']
        org_founded_date_after = self.cleaned_data['org_founded_date_after']
        org_founded_date_before = self.cleaned_data['org_founded_date_before']
        founder_id = self.cleaned_data['founder_id']
        founder_name = self.cleaned_data['founder_name']
        conn, cur = get_db()
        ### This is too slow (Exploding the join operations) ###
        # calculate stats. num_founders, num_members, num_past_events, num_upcoming_events, num_sheltered_animals, num_released_animals, num_adopted_animals, num_donations
        # sql = f"""
        # WITH SELECTED_ORGS AS (
        #     SELECT DISTINCT o.Org_ID, o.Org_name, o.Org_address, o.Org_phone_number, o.Org_founded_date
        #     FROM ORGANIZATION AS o
        #         JOIN BUILD AS b ON o.Org_ID = b.Org_ID
        #         JOIN USER_ AS u ON b.Founder_ID = u.User_ID
        #     WHERE o.Org_ID LIKE '%{org_id}%'
        #         AND o.Org_name LIKE '%{org_name}%'
        #         AND o.Org_address LIKE '%{org_address}%'
        #         AND o.Org_phone_number LIKE '%{org_phone}%'
        #         AND o.Org_founded_date >= '{org_founded_date_after if org_founded_date_after else '0001-01-01'}'
        #         AND o.Org_founded_date <= '{org_founded_date_before if org_founded_date_before else '9999-12-31'}'
        #         AND b.Founder_ID LIKE '%{founder_id}%'
        #         AND u.User_name LIKE '%{founder_name}%'
        #     ORDER BY o.Org_ID DESC
        # )
        

        # SELECT so.Org_ID, so.Org_name, so.Org_address, so.Org_phone_number, so.Org_founded_date,
        #     COUNT(DISTINCT b.Founder_ID) AS num_founders,
        #     COUNT(DISTINCT j.User_ID) AS num_members,
        #     COUNT(DISTINCT e.Event_ID) AS num_past_events,
        #     COUNT(DISTINCT e2.Event_ID) AS num_upcoming_events,
        #     COUNT(DISTINCT a.Animal_ID) AS num_sheltered_animals,
        #     COUNT(DISTINCT a2.Animal_ID) AS num_released_animals,
        #     COUNT(DISTINCT a3.Animal_ID) AS num_adopted_animals,
        #     COUNT(DISTINCT d.Donor_ID) AS num_donations
        # FROM SELECTED_ORGS AS so
        #     LEFT JOIN BUILD AS b ON so.Org_ID = b.Org_ID
        #     LEFT JOIN JOIN_ AS j ON so.Org_ID = j.Org_ID
        #     LEFT JOIN HOLD AS h ON so.Org_ID = h.Org_ID
        #     LEFT JOIN EVENT AS e ON h.Event_ID = e.Event_ID AND e.Event_date < CURRENT_DATE
        #     LEFT JOIN EVENT AS e2 ON h.Event_ID = e2.Event_ID AND e2.Event_date >= CURRENT_DATE
        #     LEFT JOIN ANIMAL AS a ON so.Org_ID = a.Org_id AND a.Animal_status = 'Sheltered'
        #     LEFT JOIN ANIMAL AS a2 ON so.Org_ID = a2.Org_id AND a2.Animal_status = 'Released'
        #     LEFT JOIN ANIMAL AS a3 ON so.Org_ID = a3.Org_id AND a3.Animal_status = 'Adopted'
        #     LEFT JOIN DONATE AS d ON so.Org_ID = d.Org_ID
        # GROUP BY so.Org_ID, so.Org_name, so.Org_address, so.Org_phone_number, so.Org_founded_date
        # ORDER BY so.Org_ID::int DESC;
        # """
        sql = f"""
        WITH SELECTED_ORGS AS (
            SELECT DISTINCT o.Org_ID, o.Org_name, o.Org_address, o.Org_phone_number, o.Org_founded_date
            FROM ORGANIZATION AS o
            WHERE o.Org_ID LIKE '%{org_id}%'
                AND o.Org_name LIKE '%{org_name}%'
                AND o.Org_address LIKE '%{org_address}%'
                AND o.Org_phone_number LIKE '%{org_phone}%'
                AND o.Org_founded_date >= '{org_founded_date_after if org_founded_date_after else '0001-01-01'}'
                AND o.Org_founded_date <= '{org_founded_date_before if org_founded_date_before else '9999-12-31'}'
            ORDER BY o.Org_ID DESC
        ), FOUNDERS_COUNT AS (
            SELECT b.Org_ID, COUNT(DISTINCT b.Founder_ID) AS num_founders
            FROM BUILD AS b
            JOIN SELECTED_ORGS AS so ON b.Org_ID = so.Org_ID
            GROUP BY b.Org_ID
        ), MEMBERS_COUNT AS (
            SELECT j.Org_ID, COUNT(DISTINCT j.User_ID) AS num_members
            FROM JOIN_ AS j
            JOIN SELECTED_ORGS AS so ON j.Org_ID = so.Org_ID
            GROUP BY j.Org_ID
        ), PAST_EVENTS_COUNT AS (
            SELECT h.Org_ID, COUNT(DISTINCT e.Event_ID) AS num_past_events
            FROM HOLD AS h
            JOIN EVENT AS e ON h.Event_ID = e.Event_ID AND e.Event_date < CURRENT_DATE
            JOIN SELECTED_ORGS AS so ON h.Org_ID = so.Org_ID
            GROUP BY h.Org_ID
        ), UPCOMING_EVENTS_COUNT AS (
            SELECT h.Org_ID, COUNT(DISTINCT e.Event_ID) AS num_upcoming_events
            FROM HOLD AS h
            JOIN EVENT AS e ON h.Event_ID = e.Event_ID AND e.Event_date >= CURRENT_DATE
            JOIN SELECTED_ORGS AS so ON h.Org_ID = so.Org_ID
            GROUP BY h.Org_ID
        ), SHELTERED_ANIMALS_COUNT AS (
            SELECT a.Org_ID, COUNT(DISTINCT a.Animal_ID) AS num_sheltered_animals
            FROM ANIMAL AS a
            JOIN SELECTED_ORGS AS so ON a.Org_ID = so.Org_ID
            WHERE a.Animal_status = 'Sheltered'
            GROUP BY a.Org_ID
        ), RELEASED_ANIMALS_COUNT AS (
            SELECT a.Org_ID, COUNT(DISTINCT a.Animal_ID) AS num_released_animals
            FROM ANIMAL AS a
            JOIN SELECTED_ORGS AS so ON a.Org_ID = so.Org_ID
            WHERE a.Animal_status = 'Released'
            GROUP BY a.Org_ID
        ), ADOPTED_ANIMALS_COUNT AS (
            SELECT a.Org_ID, COUNT(DISTINCT a.Animal_ID) AS num_adopted_animals
            FROM ANIMAL AS a
            JOIN SELECTED_ORGS AS so ON a.Org_ID = so.Org_ID
            WHERE a.Animal_status = 'Adopted'
            GROUP BY a.Org_ID
        ), DONATIONS_COUNT AS (
            SELECT d.Org_ID, COUNT(DISTINCT d.Donate_ID) AS num_donations
            FROM DONATE AS d
            JOIN SELECTED_ORGS AS so ON d.Org_ID = so.Org_ID
            GROUP BY d.Org_ID
        )

        SELECT 
            so.Org_ID, so.Org_name, so.Org_address, so.Org_phone_number, so.Org_founded_date,
            COALESCE(fc.num_founders, 0) as num_founders,
            COALESCE(mc.num_members, 0) as num_members,
            COALESCE(pec.num_past_events, 0) as num_past_events,
            COALESCE(uec.num_upcoming_events, 0) as num_upcoming_events,
            COALESCE(sac.num_sheltered_animals, 0) as num_sheltered_animals,
            COALESCE(rac.num_released_animals, 0) as num_released_animals,
            COALESCE(aac.num_adopted_animals, 0) as num_adopted_animals,
            COALESCE(dc.num_donations, 0) as num_donations
        FROM SELECTED_ORGS AS so
            LEFT JOIN FOUNDERS_COUNT AS fc ON so.Org_ID = fc.Org_ID
            LEFT JOIN MEMBERS_COUNT AS mc ON so.Org_ID = mc.Org_ID
            LEFT JOIN PAST_EVENTS_COUNT AS pec ON so.Org_ID = pec.Org_ID
            LEFT JOIN UPCOMING_EVENTS_COUNT AS uec ON so.Org_ID = uec.Org_ID
            LEFT JOIN SHELTERED_ANIMALS_COUNT AS sac ON so.Org_ID = sac.Org_ID
            LEFT JOIN RELEASED_ANIMALS_COUNT AS rac ON so.Org_ID = rac.Org_ID
            LEFT JOIN ADOPTED_ANIMALS_COUNT AS aac ON so.Org_ID = aac.Org_ID
            LEFT JOIN DONATIONS_COUNT AS dc ON so.Org_ID = dc.Org_ID
        ORDER BY so.Org_ID::int DESC;
        """
        df = sqlio.read_sql_query(sql, conn).to_records()
        self.org_data = df
        return df
       
class ManageUserForm(forms.Form):
    action_choices = forms.ChoiceField(choices=[('promote', 'Promote (Make Admin)'), ('demote', 'Demote (Make User)'), ('delete', 'Delete Account')], required=False)

    @full_transaction
    def execute_action(self, user_id):
        _, cur = get_db()
        action = self.cleaned_data['action_choices']
        if action == 'promote':
            sql = f"""
            UPDATE USER_
            SET User_level = 'Admin'
            WHERE User_ID = '{user_id}';
            """
            cur.execute(sql)
            return True
        elif action == 'demote':
            sql = f"""
            UPDATE USER_
            SET User_level = 'User'
            WHERE User_ID = '{user_id}';
            """
            cur.execute(sql)
            return True
        elif action == 'delete':
            sql = f"""
            DELETE FROM USER_
            WHERE User_ID = '{user_id}';
            """
            cur.execute(sql)
            return True

class BuildOrgForm(forms.Form):
    org_name = forms.CharField(required=True)
    org_address = forms.CharField(required=True)
    org_phone = forms.CharField(required=True)

    @full_transaction
    def execute_action(self, user_id):
        _, cur = get_db()
        org_name = self.cleaned_data['org_name']
        org_address = self.cleaned_data['org_address']
        org_phone = self.cleaned_data['org_phone']

        # Get the next org id
        sql = """
        SELECT Org_ID
        FROM ORGANIZATION
        ORDER BY Org_ID::int DESC
        LIMIT 1;
        """
        cur.execute(sql)
        result = cur.fetchall()
        next_id = int(result[0][0]) + 1
        # get the founded date
        founded_date = time.strftime('%Y-%m-%d', time.localtime())
        # Insert the org
        sql = f"""
        INSERT INTO ORGANIZATION (Org_ID, Org_name, Org_address, Org_phone_number, Org_founded_date)
        VALUES ('{next_id}', '{org_name}', '{org_address}', '{org_phone}', '{founded_date}');

        INSERT INTO BUILD (Org_ID, Founder_ID)
        VALUES ('{next_id}', '{user_id}');

        INSERT INTO JOIN_ (Org_ID, User_ID, Join_date)
        VALUES ('{next_id}', '{user_id}', '{founded_date}');
        """
        
        cur.execute(sql)
        print(f"successfully created org {org_name}")
        return True

    def update_org_data(self, org_id):
        conn, cur = get_db()
        org_name = self.cleaned_data['org_name']
        org_address = self.cleaned_data['org_address']
        org_phone = self.cleaned_data['org_phone']
        try:
            sql = f"""
            UPDATE ORGANIZATION
            SET Org_name = '{org_name}', Org_address = '{org_address}', Org_phone_number = '{org_phone}'
            WHERE Org_ID = '{org_id}';
            """
            cur.execute(sql)
            conn.commit()
            return True
        except Exception as e:
            print(e)
            conn.rollback()
            return False
        
class ManageFounderForm(forms.Form):
    user_name = forms.CharField(required=False)
    email = forms.CharField(required=False)
    phone = forms.CharField(required=False)
    action = forms.ChoiceField(choices=[('add', 'Add'), ('remove', 'Remove')], required=False)

    def query_search(self, org_id):
        conn, cur = get_db()
        user_name = self.cleaned_data['user_name']
        email = self.cleaned_data['email']
        phone = self.cleaned_data['phone']

        sql = f"""
        SELECT u.User_ID, u.User_name, u.User_email, u.User_phone_number, u.User_level
        FROM USER_ AS u
            JOIN JOIN_ AS j ON u.User_ID = j.User_ID
        WHERE j.Org_ID = '{org_id}'
            AND u.User_name LIKE '%{user_name}%' 
            AND u.User_email LIKE '%{email}%'
            AND u.User_phone_number LIKE '%{phone}%';
        """
        # check if exists
        cur.execute(sql)
        result = cur.fetchall()
        self.user_data = result
        if len(result) == 1:
            self.selected_user = result[0]
        return True
    
    @full_transaction
    def execute_action(self, org_id):
        _, cur = get_db()
        action = self.cleaned_data['action']
        assert action != ''
        user_id = self.selected_user[0]
        if action == 'add':
            sql = f"""
            INSERT INTO BUILD (Org_ID, Founder_ID)
            VALUES ('{org_id}', '{user_id}');
            """
            cur.execute(sql)
            return True
        elif action == 'remove':
            sql = f"""
            DELETE FROM BUILD
            WHERE Org_ID = '{org_id}' AND Founder_ID = '{user_id}';
            """
            cur.execute(sql)
            return True
 
class JoinOrgForm(forms.Form):
    # first ask the user to search for the org and then join
    org_id = forms.CharField(required=False)
    org_name = forms.CharField(required=False)
    org_address = forms.CharField(required=False)
    org_phone = forms.CharField(required=False)
    org_founded_date = forms.CharField(required=False)

    def query_search(self):
        conn, cur = get_db()
        org_id = self.cleaned_data['org_id']
        org_name = self.cleaned_data['org_name']
        org_address = self.cleaned_data['org_address']
        org_phone = self.cleaned_data['org_phone']

        sql = f"""
        SELECT *
        FROM ORGANIZATION AS o
        WHERE o.Org_ID LIKE '%{org_id}%' 
            AND o.Org_name LIKE '%{org_name}%' 
            AND o.Org_address LIKE '%{org_address}%' 
            AND o.Org_phone_number LIKE '%{org_phone}%'
        """
        # check if exists
        cur.execute(sql)
        result = cur.fetchall()
        self.org_data = result
        if len(result) == 1:
            self.selected_org = result[0]
        return True
    
    def execute_action(self, user_id):
        conn, cur = get_db()
        org_id = self.selected_org[0]
        # get the founded date
        join_date = time.strftime('%Y-%m-%d', time.localtime())
        try:
            sql = f"""
            INSERT INTO JOIN_ (Org_ID, User_ID, Join_date)
            VALUES ('{org_id}', '{user_id}', '{join_date}');
            """
            cur.execute(sql)
            conn.commit()
            return True
        except Exception as e:
            print(e)
            conn.rollback()
            return False
        
class CreateEventForm(forms.Form):
    # e.Event_date, e.Event_name, e.Capacity, e.Event_location, e.Event_description, e.Start_time, e.End_time
    event_date = forms.DateField(required=True)
    event_name = forms.CharField(required=True)
    capacity = forms.IntegerField(required=True)
    event_location = forms.CharField(required=True)
    event_description = forms.CharField(required=True)
    start_time = forms.TimeField(required=True)
    end_time = forms.TimeField(required=True)
    
    @full_transaction
    def execute_action(self, org_id):
        _, cur = get_db()
        event_date = self.cleaned_data['event_date']
        event_name = self.cleaned_data['event_name']
        capacity = self.cleaned_data['capacity']
        event_location = self.cleaned_data['event_location']
        event_description = self.cleaned_data['event_description']
        start_time = self.cleaned_data['start_time']
        end_time = self.cleaned_data['end_time']
        # Get the next event id
        sql = """
        SELECT Event_ID
        FROM EVENT
        ORDER BY Event_ID::int DESC
        LIMIT 1;
        """
        cur.execute(sql)
        result = cur.fetchall()
        next_id = int(result[0][0]) + 1
        # Insert the event
        sql = f"""
        INSERT INTO EVENT (Event_ID, Event_date, Event_name, Capacity, Event_location, Event_description, Start_time, End_time)
        VALUES ('{next_id}', '{event_date}', '{event_name}', '{capacity}', '{event_location}', '{event_description}', '{start_time}', '{end_time}');

        INSERT INTO HOLD (Event_ID, Org_ID)
        VALUES ('{next_id}', '{org_id}');
        """
        cur.execute(sql)
        print(f"successfully created event {event_name}")
        return True

class BrowseEventForm(forms.Form):
    event_id = forms.CharField(required=False)
    event_name = forms.CharField(required=False)
    event_location = forms.CharField(required=False)
    event_date_after = forms.DateField(required=False)
    event_date_before = forms.DateField(required=False)
    start_time_after = forms.TimeField(required=False)
    start_time_before = forms.TimeField(required=False)
    end_time_after = forms.TimeField(required=False)
    end_time_before = forms.TimeField(required=False)
    vacancy_min = forms.IntegerField(required=False)
    event_description = forms.CharField(required=False)
    org_id = forms.CharField(required=False)
    org_name = forms.CharField(required=False)

    def query_search(self):
        conn, cur = get_db()
        event_id = self.cleaned_data['event_id']
        event_name = self.cleaned_data['event_name']
        event_location = self.cleaned_data['event_location']
        event_date_after = self.cleaned_data['event_date_after']
        event_date_before = self.cleaned_data['event_date_before']
        start_time_after = self.cleaned_data['start_time_after']
        start_time_before = self.cleaned_data['start_time_before']
        end_time_after = self.cleaned_data['end_time_after']
        end_time_before = self.cleaned_data['end_time_before']
        vacancy_min = self.cleaned_data['vacancy_min']
        event_description = self.cleaned_data['event_description']
        org_id = self.cleaned_data['org_id']
        org_name = self.cleaned_data['org_name']
    
        sql = f"""
        WITH FilteredEvents AS (
            SELECT e.Event_ID
            FROM EVENT AS e
                JOIN HOLD AS h ON e.Event_ID = h.Event_ID
                JOIN ORGANIZATION AS o ON h.Org_ID = o.Org_ID
            WHERE e.Event_ID LIKE '%{event_id}%'
                AND e.Event_name LIKE '%{event_name}%' 
                AND e.Event_location LIKE '%{event_location}%' 
                AND o.Org_ID LIKE '%{org_id}%' 
                AND o.Org_name LIKE '%{org_name}%'
                AND e.Event_description LIKE '%{event_description}%' 
                AND e.Event_date >= '{event_date_after if event_date_after else '0001-01-01'}'
                AND e.Event_date <= '{event_date_before if event_date_before else '9999-12-31'}'
                AND e.Start_time >= '{start_time_after if start_time_after else '00:00:00'}'
                AND e.Start_time <= '{start_time_before if start_time_before else '23:59:59'}'
                AND e.End_time >= '{end_time_after if end_time_after else '00:00:00'}'
                AND e.End_time <= '{end_time_before if end_time_before else '23:59:59'}'
        )
        SELECT e.Event_ID, e.Event_date, e.Event_name, e.Capacity, 
            (e.Capacity - COUNT(a.User_ID)) As Vacancy, 
            e.Event_location, e.Event_description, e.Start_time, e.End_time, 
            o.Org_ID, o.Org_name
        FROM EVENT AS e
            JOIN FilteredEvents fe ON e.Event_ID = fe.Event_ID
            JOIN HOLD AS h ON e.Event_ID = h.Event_ID
            JOIN ORGANIZATION AS o ON h.Org_ID = o.Org_ID
            LEFT JOIN ATTEND AS a ON e.Event_ID = a.Event_ID
        GROUP BY e.Event_ID, e.Event_date, e.Event_name, e.Capacity, e.Event_location, 
                e.Event_description, e.Start_time, e.End_time, o.Org_ID, o.Org_name
        HAVING (e.Capacity - COUNT(a.User_ID)) >= '{vacancy_min if vacancy_min else 0}'
        ORDER BY e.Event_date DESC;
        """
        # check if exists
        cur.execute(sql)
        result = cur.fetchall()
        self.event_data = result
        return True

with open("data/animal_type.json", "r", encoding="utf-8") as f:
    animal_types = json.load(f)
class ReportAnimalForm(forms.Form):
    animal_type = forms.ChoiceField(choices=[(animal_type, animal_type) for animal_type in animal_types])
    animal_name = forms.CharField()
    reported_reason = forms.CharField()
    reported_loacation = forms.CharField()

    @full_transaction
    def execute_action(self, user_id):
        _, cur = get_db()
        animal_type = self.cleaned_data['animal_type']
        animal_name = self.cleaned_data['animal_name']
        reported_reason = self.cleaned_data['reported_reason']
        reported_loacation = self.cleaned_data['reported_loacation']
        # Get the next animal id
        sql = """
        SELECT Animal_ID
        FROM ANIMAL
        ORDER BY Animal_ID::int DESC
        LIMIT 1;
        """
        cur.execute(sql)
        result = cur.fetchall()
        next_id = int(result[0][0]) + 1
        # get the founded date
        reported_date = time.strftime('%Y-%m-%d', time.localtime())
        # Insert the animal
        sql = f"""
        INSERT INTO ANIMAL (Animal_ID, Animal_type, Animal_name, Animal_status, Reported_date, Reported_reason, Reported_location, Report_user_id)
        VALUES ('{next_id}', '{animal_type}', '{animal_name}', 'Reported', '{reported_date}', '{reported_reason}', '{reported_loacation}', '{user_id}');
        """
        cur.execute(sql)
        print(f"successfully created animal {animal_name}")
        return True

class OrgVisitForm(forms.Form):
    visit_date = forms.DateField()

    @full_transaction
    def execute_action(self, user_id, org_id):
        _, cur = get_db()
        visit_date = self.cleaned_data['visit_date']
        # Insert the visit
        sql = f"""
        INSERT INTO VISIT (Org_ID, User_ID, Visit_date, Status)
        VALUES ('{org_id}', '{user_id}', '{visit_date}', 'Pending');
        """
        cur.execute(sql)
        return True

class SelectHospitalForm(forms.Form):
    hospital_id = forms.CharField(required=False)
    hospital_name = forms.CharField(required=False)
    hospital_address = forms.CharField(required=False)
    hospital_phone = forms.CharField(required=False)

    def query_search(self):
        conn, cur = get_db()
        hospital_id = self.cleaned_data['hospital_id']
        hospital_name = self.cleaned_data['hospital_name']
        hospital_address = self.cleaned_data['hospital_address']
        hospital_phone = self.cleaned_data['hospital_phone']

        sql = f"""
        SELECT *
        FROM HOSPITAL AS h
        WHERE h.Hospital_ID LIKE '%{hospital_id}%' 
            AND h.Hospital_Name LIKE '%{hospital_name}%' 
            AND h.Hospital_Address LIKE '%{hospital_address}%' 
            AND h.Hospital_phone_number LIKE '%{hospital_phone}%';
        """
        df = sqlio.read_sql_query(sql, conn)
        return df.to_records()

class AddDonationForm(forms.Form):
    donor_display_name = forms.CharField(required=False)
    donor_id = forms.CharField(required=False)
    item_name = forms.CharField(required=False)
    amount = forms.IntegerField(required=True)

    @full_transaction
    def execute_action(self, org_id):
        _, cur = get_db()
        donor_display_name = f"'{self.cleaned_data['donor_display_name']}'" if self.cleaned_data['donor_display_name'] else "NULL"
        donor_id = f"'{self.cleaned_data['donor_id']}'" if self.cleaned_data['donor_id'] else "NULL"
        item_name = self.cleaned_data['item_name']
        amount = self.cleaned_data['amount']
        # Insert the donation
        sql = f"""
        INSERT INTO DONATE (Donor_ID, Donor_display_name, Org_ID, Donate_date, D_Item_name, Donate_amount)
        VALUES ({donor_id}, {donor_display_name}, '{org_id}', CURRENT_DATE, '{item_name}', '{amount}');
        """
        cur.execute(sql)
        return True
        
class QueryHospitalForm(forms.Form):
    hospital_id = forms.CharField(required=False)
    hospital_name = forms.CharField(required=False)
    hospital_address = forms.CharField(required=False)
    hospital_phone = forms.CharField(required=False)

    def query_search(self):
        conn, cur = get_db()
        hospital_name = self.cleaned_data['hospital_name']
        hospital_address = self.cleaned_data['hospital_address']
        hospital_phone = self.cleaned_data['hospital_phone']
        hospital_id = self.cleaned_data['hospital_id']

        sql = f"""
        SELECT *
        FROM HOSPITAL AS h
        WHERE h.Hospital_Name LIKE '%{hospital_name}%' 
            AND h.Hospital_Address LIKE '%{hospital_address}%' 
            AND h.Hospital_phone_number LIKE '%{hospital_phone}%'
            AND h.Hospital_ID LIKE '%{hospital_id}%'
        ORDER BY h.Hospital_ID::int DESC;
        """
        df = sqlio.read_sql_query(sql, conn)
        return df.to_records()

    def query_search_detailed(self):
        conn, cur = get_db()
        hospital_name = self.cleaned_data['hospital_name']
        hospital_address = self.cleaned_data['hospital_address']
        hospital_phone = self.cleaned_data['hospital_phone']
        hospital_id = self.cleaned_data['hospital_id']

        # calculate stats. num_animal_sent, num_animal_present with SENT_TO table
        sql = f"""
        WITH SELECTED_HOSPITALS AS (
            SELECT h.Hospital_ID, h.Hospital_Name, h.Hospital_Address, h.Hospital_phone_number
            FROM HOSPITAL AS h
            WHERE h.Hospital_Name LIKE '%{hospital_name}%' 
                AND h.Hospital_Address LIKE '%{hospital_address}%' 
                AND h.Hospital_phone_number LIKE '%{hospital_phone}%'
                AND h.Hospital_ID LIKE '%{hospital_id}%'
        ), ANIMAL_SENT_COUNT AS (
            SELECT s.Hospital_ID, COUNT(DISTINCT s.Animal_ID) AS num_animal_sent
            FROM SENT_TO AS s
            JOIN SELECTED_HOSPITALS AS sh ON s.Hospital_ID = sh.Hospital_ID
            GROUP BY s.Hospital_ID
        ), ANIMAL_PRESENT_COUNT AS (
            SELECT s.Hospital_ID, COUNT(DISTINCT s.Animal_ID) AS num_animal_present
            FROM SENT_TO AS s
            JOIN SELECTED_HOSPITALS AS sh ON s.Hospital_ID = sh.Hospital_ID
            WHERE s.Return_date IS NULL
            GROUP BY s.Hospital_ID
        )

        SELECT sh.Hospital_ID, sh.Hospital_Name, sh.Hospital_Address, sh.Hospital_phone_number,
            COALESCE(sc.num_animal_sent, 0) AS num_animal_sent,
            COALESCE(pc.num_animal_present, 0) AS num_animal_present
        FROM SELECTED_HOSPITALS AS sh
            LEFT JOIN ANIMAL_SENT_COUNT AS sc ON sh.Hospital_ID = sc.Hospital_ID
            LEFT JOIN ANIMAL_PRESENT_COUNT AS pc ON sh.Hospital_ID = pc.Hospital_ID
        ORDER BY sh.Hospital_ID::int DESC;
        """
        df = sqlio.read_sql_query(sql, conn)
        return df.to_records()

class AddHospitalForm(forms.Form):
    hospital_name = forms.CharField(required=True)
    hospital_address = forms.CharField(required=True)
    hospital_phone = forms.CharField(required=True)

    @full_transaction
    def execute_action(self):
        _, cur = get_db()
        hospital_name = self.cleaned_data['hospital_name']
        hospital_address = self.cleaned_data['hospital_address']
        hospital_phone = self.cleaned_data['hospital_phone']
        # Get the next hospital id
        sql = """
        SELECT Hospital_ID
        FROM HOSPITAL
        ORDER BY Hospital_ID::int DESC
        LIMIT 1;
        """
        cur.execute(sql)
        result = cur.fetchall()
        next_id = int(result[0][0]) + 1
        # Insert the hospital
        sql = f"""
        INSERT INTO HOSPITAL (Hospital_ID, Hospital_Name, Hospital_Address, Hospital_phone_number)
        VALUES ('{next_id}', '{hospital_name}', '{hospital_address}', '{hospital_phone}');
        """
        cur.execute(sql)
        print(f"successfully created hospital {hospital_name}")
        return True