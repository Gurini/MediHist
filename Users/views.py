from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import User, DoctorProfile, NurseProfile, AdminProfile

# Create your views here.
def home(request):
    #Home page
    return render(request, 'Users/home.html')


@login_required
def dashboard(request):
    #Dashboard displays different content based on user
    user = request.user
    context = {
        'user': user,
    }

    #Profile specific context
    if user.user_type == 'DOCTOR':
        context['profile'] = user.doctor_profile
        template = 'Users/doctor_dashboard.html'
    elif user.user_type == 'NURSE':
        context['profile'] = user.nurse_profile
        template = 'Users/nurse_dashboard.html'
    elif user.user_type == 'ADMIN':
        context['profile'] = user.admin_profile
        template = 'Users/admin_dashboard.html'
    else:
        template = 'Users/dashboard.html'


@login_required
def profile_view(request):
    #User profile
    user = request.user
    context = {'user': user}

    if user.user_type == 'DOCTOR':
        context['profile'] = user.doctor_profile
    elif user.user_type == 'NURSE':
        context['profile'] = user.nurse_profile
    elif user.user_type == 'ADMIN':
        context['profile'] = user.admin_profile

    return render(request, 'Users/profile.html', context)


def user_login(request):
    #login view
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            message.success(request, f'Welcome back, {user.get_full_name() or user.username}!')
            return redirect('dashboard')
        else:
            messsages.error(request, 'Invalid username or password')
    
    return render(request, 'Users/login.html')


@login_required
def user_logout(request):
    #logout view
    logout(request)
    messages.success(request, 'You have been logged out successfully')
    return redirect('login')
