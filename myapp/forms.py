from django import forms
from .db_utils import get_db
import pandas.io.sql as sqlio
import time
import json

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

    def execute_action(self):
        conn, cur = get_db()
        username = self.cleaned_data['username']
        phone = self.cleaned_data['phone']
        email = self.cleaned_data['email']
        try: 
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
            conn.commit()
            self.user_data = [next_id, username, phone, email, 'User']
            return True
        except Exception as e:
            print(e)
            conn.rollback()
            return False

    def update_user_data(self, user_id):
        conn, cur = get_db()
        username = self.cleaned_data['username']
        phone = self.cleaned_data['phone']
        email = self.cleaned_data['email']
        try:
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
            conn.commit()
            self.user_data = [user_id, username, phone, email]

            return True
        except Exception as e:
            print(e)
            conn.rollback()
            return False
        
class QueryUsersForm(forms.Form):
    user_id = forms.CharField(required=False)
    user_name = forms.CharField(required=False)
    phone = forms.CharField(required=False)
    email = forms.CharField(required=False)
    # options {Any, User, Admin}
    level = forms.ChoiceField(choices=[('', 'Any'), ('User', 'User'), ('Admin', 'Admin')], required=False)

    def execute_action(self):
        conn, cur = get_db()
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
        # check if exists
        cur.execute(sql)
        result = cur.fetchall()
        self.user_data = result
        return True
        
class ManageUserForm(forms.Form):
    action_choices = forms.ChoiceField(choices=[('promote', 'Promote (Make Admin)'), ('demote', 'Demote (Make User)'), ('delete', 'Delete Account')], required=False)

    def execute_action(self, user_id):
        conn, cur = get_db()
        action = self.cleaned_data['action_choices']
        print(action)

        try:
            if action == 'promote':
                sql = f"""
                UPDATE USER_
                SET User_level = 'Admin'
                WHERE User_ID = '{user_id}';
                """
                cur.execute(sql)
                conn.commit()
                return True
            elif action == 'demote':
                sql = f"""
                UPDATE USER_
                SET User_level = 'User'
                WHERE User_ID = '{user_id}';
                """
                cur.execute(sql)
                conn.commit()
                return True
            elif action == 'delete':
                sql = f"""
                DELETE FROM USER_
                WHERE User_ID = '{user_id}';
                """
                cur.execute(sql)
                conn.commit()
                return True
        except Exception as e:
            print(e)
            conn.rollback()
            return False

class BuildOrgForm(forms.Form):
    org_name = forms.CharField(required=True)
    org_address = forms.CharField(required=True)
    org_phone = forms.CharField(required=True)

    def execute_action(self, user_id):
        conn, cur = get_db()
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
        conn.commit()
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
    
    def execute_action(self, org_id):
        conn, cur = get_db()
        action = self.cleaned_data['action']
        assert action != ''
        user_id = self.selected_user[0]
        try:
            if action == 'add':
                sql = f"""
                INSERT INTO BUILD (Org_ID, Founder_ID)
                VALUES ('{org_id}', '{user_id}');
                """
                cur.execute(sql)
                conn.commit()
                return True
            elif action == 'remove':
                sql = f"""
                DELETE FROM BUILD
                WHERE Org_ID = '{org_id}' AND Founder_ID = '{user_id}';
                """
                cur.execute(sql)
                conn.commit()
                return True
        except Exception as e:
            print(e)
            conn.rollback()
            return False
 
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
    
    def execute_action(self, org_id):
        conn, cur = get_db()
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
        print(next_id)
        print(org_id)
        conn.commit()
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

    def execute_action(self, user_id):
        conn, cur = get_db()
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
        conn.commit()
        return True

class OrgVisitForm(forms.Form):
    visit_date = forms.DateField()

    def execute_action(self, user_id, org_id):
        conn, cur = get_db()
        try: 
            visit_date = self.cleaned_data['visit_date']
            # Insert the visit
            sql = f"""
            INSERT INTO VISIT (Org_ID, User_ID, Visit_date, Status)
            VALUES ('{org_id}', '{user_id}', '{visit_date}', 'Pending');
            """
            cur.execute(sql)
            conn.commit()
            return True
        except Exception as e:
            print(e)
            conn.rollback()
            return False

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

