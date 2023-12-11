from django import forms
from .db_utils import get_db

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
    user_name = forms.CharField(required=False)
    phone = forms.CharField(required=False)
    email = forms.CharField(required=False)
    level = forms.CharField(required=False)

    def is_valid(self):
        valid = super(QueryUsersForm, self).is_valid()
        if not valid:
            return False
        conn, cur = get_db()
        user_name = self.cleaned_data['user_name']
        phone = self.cleaned_data['phone']
        email = self.cleaned_data['email']
        level = self.cleaned_data['level']
        sql = f"""
        SELECT *
        FROM USER_ AS u
        WHERE u.User_name LIKE '%{user_name}%' AND u.User_phone_number LIKE '%{phone}%' AND u.User_email LIKE '%{email}%' AND u.User_level LIKE '%{level}%';
        """
        # check if exists
        cur.execute(sql)
        result = cur.fetchall()
        self.user_data = result
        return True
        