from django import forms
from .db_utils import get_db
import time

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

    def query_search(self):
        conn, cur = get_db()
        user_name = self.cleaned_data['user_name']
        email = self.cleaned_data['email']
        phone = self.cleaned_data['phone']

        sql = f"""
        SELECT u.User_ID, u.User_name, u.User_email, u.User_phone_number, u.User_level
        FROM USER_ AS u
        WHERE u.User_name LIKE '%{user_name}%' 
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
 

