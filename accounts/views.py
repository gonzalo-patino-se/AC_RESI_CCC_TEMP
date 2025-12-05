from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout as auth_logout, authenticate, login
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.urls import reverse

@login_required(login_url='login')
def home(request):
    return render(request, "home.html")

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Auto-login user after registration
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    
    return render(request, 'registration/register.html', {'form': form})

def logout_view(request):
    auth_logout(request)
    response = redirect("login")
    response.delete_cookie("sessionid")
    return response
