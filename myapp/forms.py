from django import forms
from .db_utils import get_db
import time

password = "0000" # dummy, just for testing

class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

    def is_valid(self):
        valid = super(LoginForm, self).is_valid()
        if not valid:
            return False
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

    def is_valid(self):
        valid = super(SignupForm, self).is_valid()
        if not valid:
            return False
        conn, cur = get_db()
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

        if len(result) == 0:
            # Get the next user id
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
        

"""
    CREATE TABLE ORGANIZATION (
        Org_ID VARCHAR(20) PRIMARY KEY,
        Org_name VARCHAR(50) NOT NULL,
        Org_address VARCHAR(100) NOT NULL,
        Org_phone_number CHAR(16) NOT NULL,
        Org_founded_date DATE NOT NULL
    );"""

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
