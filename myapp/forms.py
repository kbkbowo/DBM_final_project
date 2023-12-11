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
        print(result)
        if len(result) == 0:
            return False
        else:
            self.user_data = result[0]
            return True
 