from django.shortcuts import render, HttpResponse, redirect
from .forms import LoginForm, SignupForm, QueryUsersForm

class User:
    def __init__(self, user_id, user_name, user_phone, user_email, user_level):
        self.user_id = user_id
        self.user_name = user_name
        self.user_phone = user_phone
        self.user_email = user_email
        self.user_level = user_level

# Create your views here.
def login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            request.session['user_data'] = form.user_data
            if request.session['user_data'][4] == 'Admin':
                return redirect(request.session.get('last_page', 'admin_home'))
            else:
                return redirect(request.session.get('last_page', 'home'))
        else:
            return render(request, 'login.html', {'form': form, 'status': 'Invalid username or password.'})   
    return render(request, 'login.html', {'form': LoginForm()})

def home(request):
    # redirect to login page if not logged in
    if request.session.get('user_data') is None:
        request.session['last_page'] = 'home'
        return redirect('login')
        
    return render(request, 'home.html', {'user_id':request.session['user_data'][0], 'user_name': request.session['user_data'][1]})  

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

def admin_home(request):
    # redirect to login page if not logged in
    if request.session.get('user_data') is None:
        request.session['last_page'] = 'admin_home'
        return redirect('login')
    if request.session['user_data'][4] != 'Admin':
        return redirect('home')
    return render(request, 'admin_home.html', {'user_id':request.session['user_data'][0], 'user_name': request.session['user_data'][1]})

def manage_users(request):
    # redirect to login page if not logged in
    if request.session.get('user_data') is None:
        request.session['last_page'] = 'manage_users'
        return redirect('login')
    if request.session['user_data'][4] != 'Admin':
        return redirect('home')

    if request.method == 'POST':
        form = QueryUsersForm(request.POST)
        if form.is_valid():
            users = []
            result = form.user_data
            for row in result:
                users.append(User(*row))

            return render(request, 'manage_users.html', {'form': form, 'users': users})


    return render(request, 'manage_users.html', {'form': QueryUsersForm()})