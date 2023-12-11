from django.shortcuts import render, HttpResponse
from .forms import LoginForm

# Create your views here.
def home(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            return HttpResponse(f'Successfully logged in as a {form.user_data[4]}, {form.user_data[1]}!')
        else:
            return render(request, 'login.html', {'form': form, 'status': 'Invalid username or password.'})   
    return render(request, 'login.html', {'form': LoginForm()})