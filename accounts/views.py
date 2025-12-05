
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout as auth_logout
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.urls import reverse

@login_required(login_url='login')
def home(request):
    # Django automatically redirects to login if session expired
    return render(request, "home.html")

def logout(request):
    auth_logout(request)
    response = redirect("login")
    response.delete_cookie("sessionid")  # Force delete session cookie
    return response
