from django.shortcuts import render, HttpResponse, redirect
from .forms import LoginForm, SignupForm, QueryUsersForm, ManageUserForm, BuildOrgForm, ManageFounderForm, JoinOrgForm, CreateEventForm, BrowseEventForm, ReportAnimalForm
from .db_utils import *

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

class Event:
    # e.Event_ID, e.Event_date, e.Event_name, e.Capacity, e.Event_location, e.Event_description, e.Start_time, e.End_time
    def __init__(self, event_id, event_date, event_name, capacity, event_location, event_description, start_time, end_time, num_attendees=None):
        self.dict = {
            "event_id": event_id,
            "event_date": event_date,
            "event_name": event_name,
            "capacity": capacity,
            "event_location": event_location,
            "event_description": event_description,
            "start_time": start_time,
            "end_time": end_time,
            "num_attendees": num_attendees,
        }
        ### set attributes
        for k, v in self.dict.items():
            setattr(self, k, v)

# e.Event_ID, e.Event_date, e.Event_name, e.Capacity, (e.Capacity - COUNT(a.User_ID)) As Vacancy, e.Event_location, e.Event_description, e.Start_time, e.End_time, o.Org_ID, o.Org_name
class BrowsedEvent:
    def __init__(self, event_id, event_date, event_name, capacity, vacancy, event_location, event_description, start_time, end_time, org_id, org_name):
        self.dict = {
            "event_id": event_id,
            "event_date": event_date,
            "event_name": event_name,
            "capacity": capacity,
            "vacancy": vacancy,
            "event_location": event_location,
            "event_description": event_description,
            "start_time": start_time,
            "end_time": end_time,
            "org_id": org_id,
            "org_name": org_name,
        }
        ### set attributes
        for k, v in self.dict.items():
            setattr(self, k, v)

# SELECT a.Animal_ID, a.Animal_type, a.Animal_name, a.Animal_status, a.Reported_date, a.Reported_reason, a.Reported_location, a.Shelter_date, a.Adopt_user_ID, a.Report_user_ID
class Animal:
    def __init__(self, animal_id, animal_type, animal_name, animal_status, reported_date, reported_reason, reported_location, shelter_date, adopt_user_id, report_user_id):
        self.dict = {
            "animal_id": animal_id,
            "animal_type": animal_type,
            "animal_name": animal_name,
            "animal_status": animal_status,
            "reported_date": reported_date,
            "reported_reason": reported_reason,
            "reported_location": reported_location,
            "shelter_date": shelter_date,
            "adopt_user_id": adopt_user_id,
            "report_user_id": report_user_id,
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
    attending_orgs = parse_data(Org, get_attending_orgs(request.session['user_data'][0]))
    ctx_dict = {
        "user_id": request.session['user_data'][0],
        "user_name": request.session['user_data'][1],
        "user_level": request.session['user_data'][4],
        "owned_orgs": owned_orgs,
        "attending_orgs": attending_orgs,
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
    attended_orgs = parse_data(Org, get_attending_orgs(request.session['user_data'][0]))
    if org_id in [org.org_id for org in attended_orgs]:
        attending = True
    else:
        attending = False

    ctx_dict = {
        "org_info": org_info,
        "org_founders": org_founders,
        "attending": attending,
    }

    return render(request, 'org_page.html', ctx_dict)

def org_edit_info(request, org_id=-1):
    if request.session.get('user_data') is None:
        request.session['last_page'] = 'org_edit'
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
                form.query_search(org_id=org_id)
                if form.selected_user[0] == request.session['user_data'][0]:
                    selected_self = True
            elif "Confirm_action" in request.POST:
                form.query_search(org_id=org_id)
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

def org_delete(request, org_id=-1):
    if request.session.get('user_data') is None:
        request.session['last_page'] = 'org_delete'
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

    if request.method == 'POST':
        if "Delete" in request.POST:
            delete_org(org_id)
            return redirect('org_home')
    
    org_info = Org(*get_org_info(org_id)).dict
    return render(request, 'org_delete.html', {"org_info": org_info})

def org_leave(request, org_id=-1):
    if request.session.get('user_data') is None:
        request.session['last_page'] = 'org_leave'
        return redirect('login')
    
    founders = get_org_founders(org_id)
    # stop the last founder from leaving
    if len(founders) == 1 and founders[0][0] == request.session['user_data'][0]:
        last_founder = True
    else:
        last_founder = False
    
    if request.method == 'POST':
        if "Leave" in request.POST:
            user_id = request.session['user_data'][0]
            leave_org(user_id, org_id)
            return redirect('org_home')
    
    org_info = Org(*get_org_info(org_id)).dict
    return render(request, 'org_leave.html', {"org_info": org_info, "last_founder": last_founder})

def org_browse(request):
    if request.session.get('user_data') is None:
        request.session['last_page'] = 'org_join'
        return redirect('login')
    
    if request.method == 'POST':
        form = JoinOrgForm(request.POST)
        if form.is_valid():
            if "Search" in request.POST:
                form.query_search()
                orgs = parse_data(Org, form.org_data)
            elif "Confirm_action" in request.POST:
                form.query_search()
                form.execute_action()
                orgs = parse_data(Org, form.org_data)
            else:
                orgs = []

            ctx_dict = {
                "form": form,
                "orgs": orgs if orgs else None,
                "len_orgs": len(orgs),
                "attending_orgs": parse_data(Org, get_attending_orgs(request.session['user_data'][0])),
            }
            return render(request, 'org_browse.html', ctx_dict)

        
    attending_orgs = parse_data(Org, get_attending_orgs(request.session['user_data'][0]))
    ctx_dict = {
        "form": QueryUsersForm(),
        "attending_orgs": attending_orgs,
    }
    return render(request, 'org_browse.html', ctx_dict)

def org_join(request, org_id=-1):
    if request.session.get('user_data') is None:
        request.session['last_page'] = 'org_join'
        return redirect('login')
        
    attending_orgs = parse_data(Org, get_attending_orgs(request.session['user_data'][0]))
    if org_id in [org.org_id for org in attending_orgs]:
        status = "You are already in this organization."
    else:
        user_id = request.session['user_data'][0]
        try: 
            join_org(user_id, org_id)
            status = "Successfully joined this organization."
        except:
            status = "Failed to join this organization. An user can only join each organization once per day."
        

    return render(request, 'org_join.html', {"status": status})
    
def org_event_panel(request, org_id=-1):
    if request.session.get('user_data') is None:
        request.session['last_page'] = 'event_panel'
        return redirect('login')

    # check if the user is the member of the org
    if org_id not in [org.org_id for org in parse_data(Org, get_attending_orgs(request.session['user_data'][0]))]:
        return redirect('org_home')

    ctx_dict = {
        "org_info": Org(*get_org_info(org_id)).dict,
        "org_events": parse_data(Event, get_org_events(org_id)),
    }
    return render(request, 'org_event_panel.html', ctx_dict)

def org_create_event(request, org_id=-1):
    if request.session.get('user_data') is None:
        request.session['last_page'] = 'event_create'
        return redirect('login')

    # check if the user is the member of the org
    if org_id not in [org.org_id for org in parse_data(Org, get_attending_orgs(request.session['user_data'][0]))]:
        return redirect('org_home')

    if request.method == 'POST':
        form = CreateEventForm(request.POST)
        if form.is_valid():
            result = form.execute_action(org_id=org_id)
            print(result)
            return redirect('org_home')
        else:
            return render(request, 'org_create_event.html', {'form': form, 'status': 'Invalid inputs.'})
        
    return render(request, 'org_create_event.html', {'form': BuildOrgForm()})

def org_delete_event(request, org_id, event_id):
    if request.session.get('user_data') is None:
        request.session['last_page'] = 'event_modify'
        return redirect('login')
    
    # check if the user is the member of the org
    if org_id not in [org.org_id for org in parse_data(Org, get_attending_orgs(request.session['user_data'][0]))]:
        return redirect('org_home')
    
    if request.method == 'POST':
        if "Delete" in request.POST:
            delete_event(event_id)
            return redirect('org_event_panel', org_id=org_id)
        
    event_info = Event(*get_event_info(event_id)).dict
    return render(request, 'org_delete_event.html', {"event_info": event_info})

def org_animal_panel(request, org_id=-1):
    if request.session.get('user_data') is None:
        request.session['last_page'] = 'animal_panel'
        return redirect('login')

    # check if the user is the member of the org
    if org_id not in [org.org_id for org in parse_data(Org, get_attending_orgs(request.session['user_data'][0]))]:
        return redirect('org_home')

    ctx_dict = {
        "org_info": Org(*get_org_info(org_id)).dict,
        "unsheltered_animals": parse_data(Animal, get_unsheltered_animals()),
        "org_animals": parse_data(Animal, get_org_animals(org_id)),
    }
    return render(request, 'org_animal_panel.html', ctx_dict)

def org_shelter_animal(request, org_id, animal_id):
    if request.session.get('user_data') is None:
        request.session['last_page'] = 'animal_shelter'
        return redirect('login')
    
    # check if the user is the member of the org
    if org_id not in [org.org_id for org in parse_data(Org, get_attending_orgs(request.session['user_data'][0]))]:
        return redirect('org_home')

    animal_info = Animal(*get_animal_info(animal_id)).dict

    if request.method == 'POST':
        success = shelter_animal(org_id, animal_id)
        if success:
            return render(request, 'org_shelter_animal.html', {'animal_info': animal_info, 'status': 'Successfully sheltered this animal.'})
        else:
            return render(request, 'org_shelter_animal.html', {'animal_info': animal_info, 'status': 'Failed to shelter this animal. This animal might have been sheltered by another organization sheltered.'})

    return render(request, 'org_shelter_animal.html', {'animal_info': animal_info})

def event(request):
    if request.session.get('user_data') is None:
        request.session['last_page'] = 'events'
        return redirect('login')
    
    user_id = request.session['user_data'][0]
    ctx_dict = {
        "events": parse_data(Event, get_user_events(user_id)),
    }
    return render(request, 'event.html', ctx_dict)

def event_browse(request):
    if request.session.get('user_data') is None:
        request.session['last_page'] = 'event_browse'
        return redirect('login')

    if request.method == 'POST':
        form = BrowseEventForm(request.POST)
        if form.is_valid():
            if "Search" in request.POST:
                form.query_search()
                events = parse_data(BrowsedEvent, form.event_data)
            else:
                events = []

            ctx_dict = {
                "form": form,
                "events": events if events else None,
                "len_events": len(events),
                "my_events": parse_data(Event, get_user_events(request.session['user_data'][0])),
            }
            return render(request, 'event_browse.html', ctx_dict)
    
    attending_events = parse_data(Event, get_user_events(request.session['user_data'][0]))
    ctx_dict = {
        "form": BrowseEventForm(),
        "my_events": attending_events,
    }
    return render(request, 'event_browse.html', ctx_dict)

def event_join(request, event_id=-1):
    if request.session.get('user_data') is None:
        request.session['last_page'] = 'event_join'
        return redirect('login')
    
    user_id = request.session['user_data'][0]
    try: 
        join_event(user_id, event_id)
        status = "Successfully joined this event."
    except:
        status = "Failed to join this event. Are you already in this event?."
    
    return render(request, 'event_join.html', {"status": status})

def report_animal(request):
    if request.session.get('user_data') is None:
        request.session['last_page'] = 'report_animal'
        return redirect('login')

    if request.method == 'POST' and "Submit" in request.POST:
            form = ReportAnimalForm(request.POST)
            if form.is_valid():
                user_id = request.session['user_data'][0]
                result = form.execute_action(user_id=user_id)
                return render(request, 'report_animal.html', {'form': form, 'status': 'Successfully reported.'})
            else:
                return render(request, 'report_animal.html', {'form': form, 'status': 'Invalid inputs.'})

    return render(request, 'report_animal.html', {'form': ReportAnimalForm()})