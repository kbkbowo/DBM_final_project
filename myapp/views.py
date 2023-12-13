from django.shortcuts import render, HttpResponse, redirect
from .forms import LoginForm, SignupForm, QueryUsersForm, ManageUserForm, BuildOrgForm, ManageFounderForm
from .db_utils import get_owned_orgs, validate_org_owner, get_org_info, get_org_founders 

class User:
    def __init__(self, user_id, user_name, user_email, user_phone, user_level):
        self.dict = {
            "user_id": user_id,
            "user_name": user_name,
            "user_email": user_email,
            "user_phone": user_phone,
            "user_level": user_level,
        }
        ### set attributes
        for k, v in self.dict.items():
            setattr(self, k, v)

class Org:
    def __init__(self, org_id, org_name, org_address, org_phone, org_founded_date):
        self.dict = {
            "org_id": org_id,
            "org_name": org_name,
            "org_address": org_address,
            "org_phone": org_phone,
            "org_founded_date": org_founded_date,
        }
        ### set attributes
        for k, v in self.dict.items():
            setattr(self, k, v)
    

def parse_data(cls, data):
    return [cls(*row) for row in data]

def _get_form(request, formcls, prefix):
    data = request.POST if prefix in request.POST else None
    return formcls(data, prefix=prefix)



# Create your views here.
def login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            if form.execute_action():
                request.session['user_data'] = form.user_data
                return redirect(request.session.get('last_page', 'home'))
        
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

def edit_profile(request):
    # redirect to login page if not logged in
    if request.session.get('user_data') is None:
        request.session['last_page'] = 'edit_profile'
        return redirect('login')

    # get the form with current user data
    user_dict = {
        "username": request.session['user_data'][1],
        "phone": request.session['user_data'][2],
        "email": request.session['user_data'][3],
    }
    
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            success = form.update_user_data(user_id=request.session['user_data'][0])
            if success: 
                request.session['user_data'][:4] = form.user_data
                request.session.modified = True
            else:
                return render(request, 'edit_profile.html', {'form': form, 'status': 'Invalid inputs.'})
            return redirect('profile')
        else:
            print(form.errors)
    
    form = SignupForm(initial=user_dict)
    form.cleaned_data = user_dict
    return render(request, 'edit_profile.html', {'form': form})

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
            users = parse_data(User, form.user_data)

            action_form = _get_form(request, ManageUserForm, 'Confirm_action')
            if action_form.is_valid():
                request.session['last_action_form'] = action_form.cleaned_data
                action_form.execute_action(request.session['selected_user']) # perform the action
                form.execute_action() # refresh the user list
                users = parse_data(User, form.user_data)
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

def org_home(request):
    if request.session.get('user_data') is None:
        request.session['last_page'] = 'org_home'
        return redirect('login')
    
    owned_orgs = parse_data(Org, get_owned_orgs(User(*request.session['user_data']).dict))
    ctx_dict = {
        "user_id": request.session['user_data'][0],
        "user_name": request.session['user_data'][1],
        "user_level": request.session['user_data'][4],
        "owned_orgs": owned_orgs,
    }
    return render(request, 'org_home.html', ctx_dict)   

def org_build(request):
    if request.session.get('user_data') is None:
        request.session['last_page'] = 'org_build'
        return redirect('login')

    if request.method == 'POST':
        form = BuildOrgForm(request.POST)
        if form.is_valid():
            user_id = request.session['user_data'][0]
            form.execute_action(user_id=user_id)
            return redirect('org_home')
        else:
            return render(request, 'org_build.html', {'form': form, 'status': 'Invalid inputs.'})
        
    return render(request, 'org_build.html', {'form': BuildOrgForm()})

def org_page(request, org_id=-1):
    if org_id == -1:
        return redirect('org_home')
    
    org_info = Org(*get_org_info(org_id)).dict
    org_founders = parse_data(User, get_org_founders(org_id))

    ctx_dict = {
        "org_info": org_info,
        "org_founders": org_founders,
    }

    return render(request, 'org_page.html', ctx_dict)

def org_edit_info(request, org_id=-1):
    if request.session.get('user_data') is None:
        request.session['last_page'] = 'org_edit'
        return redirect('login')
    # validate user's ownership of the org
    ownership = validate_org_owner({'user_id': request.session['user_data'][0], 'org_id': org_id})
    if not ownership:
        return redirect('org_home')
    
    org_info = Org(*get_org_info(org_id)).dict
    if request.method == 'POST':
        form = BuildOrgForm(request.POST)
        if form.is_valid():
            user_id = request.session['user_data'][0]
            form.update_org_data(org_id=org_id)
            return redirect('org_home')
        else:
            return render(request, 'org_edit_info.html', {'form': form, 'status': 'Invalid inputs.'})
        
    form = BuildOrgForm(initial=org_info)
    form.cleaned_data = org_info
    return render(request, 'org_edit_info.html', {'form': form})

def org_edit_founder(request, org_id=-1):
    if request.session.get('user_data') is None:
        request.session['last_page'] = 'org_add_founder'
        return redirect('login')
    # validate user's ownership of the org
    if request.session.get('ownership') is None:
        request.session['ownership'] = []
    
    if org_id not in request.session['ownership']:
        ownership = validate_org_owner({'user_id': request.session['user_data'][0], 'org_id': org_id})
        if not ownership:
            return redirect('org_home')
        else: 
            request.session['ownership'].append(org_id)
            request.session.modified = True
    
    print("founders:", get_org_founders(org_id))
    selected_self = False
    
    if request.method == 'POST':
        form = ManageFounderForm(request.POST)
        if form.is_valid():
            if "Search" in request.POST:
                form.query_search()
                if form.selected_user[0] == request.session['user_data'][0]:
                    selected_self = True
            elif "Confirm_action" in request.POST:
                form.query_search()
                if form.selected_user[0] != request.session['user_data'][0]:
                    form.execute_action(org_id=org_id)
                else:
                    selected_self = True
                
            users = parse_data(User, form.user_data)
            ctx_dict = {
                "form": form,
                "users": users,
                "len_users": len(users),
                "org_founders": parse_data(User, get_org_founders(org_id)),
                "selected_self": selected_self,
            }
            return render(request, 'org_edit_founder.html', ctx_dict)
    
    ctx_dict = {
        "form": QueryUsersForm(),
        "org_founders": parse_data(User, get_org_founders(org_id)),
        "selected_self": selected_self,
    }
    return render(request, 'org_edit_founder.html', ctx_dict)


