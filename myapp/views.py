from django.shortcuts import render, HttpResponse, redirect
from .forms import LoginForm, SignupForm, QueryUsersForm, ManageUserForm

class User:
    def __init__(self, user_id, user_name, user_phone, user_email, user_level):
        self.user_id = user_id
        self.user_name = user_name
        self.user_phone = user_phone
        self.user_email = user_email
        self.user_level = user_level

def parse_user_datas(user_datas):
    users = []
    for row in user_datas:
        users.append(User(*row))
    return users

def _get_form(request, formcls, prefix):
    data = request.POST if prefix in request.POST else None
    return formcls(data, prefix=prefix)

# Create your views here.
def login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            request.session['user_data'] = form.user_data
            return redirect(request.session.get('last_page', 'home'))
        else:
            return render(request, 'login.html', {'form': form, 'status': 'Invalid username or password.'})   
    return render(request, 'login.html', {'form': LoginForm()})

def home(request):
    # redirect to login page if not logged in
    if request.session.get('user_data') is None:
        request.session['last_page'] = 'home'
        return redirect('login')
    
    if request.method == 'POST':
        if "redirect_manage_users" in request.POST:
            request.session['last_page'] = 'home'
            return redirect('manage_users')
        
    return render(request, 'home.html', {'user_id':request.session['user_data'][0], 'user_name': request.session['user_data'][1], 'user_level': request.session['user_data'][4]})

def logout(request):
    request.session.flush()
    return redirect('login')

def profile(request):
    # redirect to login page if not logged in
    if request.session.get('user_data') is None:
        request.session['last_page'] = 'profile'
        return redirect('login')

    ctx_dict = {
        "user_id": request.session['user_data'][0],
        "user_name": request.session['user_data'][1],
        "user_phone": request.session['user_data'][2],
        "user_email": request.session['user_data'][3],
    }
        
    return render(request, 'profile.html', ctx_dict)

def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            request.session['user_data'] = form.user_data
            return redirect(request.session.get('last_page', 'home'))
        else:
            return render(request, 'signup.html', {'form': form, 'status': 'Invalid inputs.'})
    return render(request, 'signup.html', {'form': SignupForm()})

def manage_users(request):
    # redirect to login page if not logged in
    if request.session.get('user_data') is None:
        request.session['last_page'] = 'manage_users'
        return redirect('login')
    if request.session['user_data'][4] != 'Admin':
        return redirect('home')

    if request.method == 'POST':
        if request.session['last_page'] == 'manage_users':
            form = _get_form(request, QueryUsersForm, 'Search') 
            if form.is_valid():
                request.session['last_form'] = form.cleaned_data
            else:
                # recover the last form
                form = QueryUsersForm(None, initial=request.session['last_form'], prefix='Search')
                form.cleaned_data = request.session['last_form']

            form.execute_action()
            users = parse_user_datas(form.user_data)

            action_form = _get_form(request, ManageUserForm, 'Confirm_action')
            if action_form.is_valid():
                request.session['last_action_form'] = action_form.cleaned_data
                action_form.execute_action(request.session['selected_user']) # perform the action
                form.execute_action() # refresh the user list
                users = parse_user_datas(form.user_data)
            else:
                last_action = request.session.get('last_action_form')
                if last_action is not None:
                    action_form = ManageUserForm(None, initial=last_action, prefix='Confirm_action')
                    action_form.cleaned_data = last_action
                else:
                    action_form = ManageUserForm(prefix='Confirm_action')

            ctx_dict = {
                "form": form,
                "users": users,
                "len_users": len(users),
            }

            if (len(users) == 1) and (users[0].user_id != request.session['user_data'][0]):
                ctx_dict["action_form"] = action_form
                request.session['selected_user'] = users[0].user_id
                
            return render(request, 'manage_users.html', ctx_dict)        
    request.session['last_page'] = 'manage_users'
    return render(request, 'manage_users.html', {'form': QueryUsersForm(prefix='Search')})