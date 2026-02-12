from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q
from datetime import date, timedelta
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
    #Import models to avoid circular import
    try:
        from records.models import Patient, MedicalHistory, Diagnosis, Prescription

        #stats for all users
        total_patients = Patient.objects.filter(is_active=True).count()
        context['total_patients'] = total_patients

        #Profile specific context
        if user.user_type == 'DOCTOR':
            context['profile'] = user.doctor_profile

            #Doctor specific stats on dashboard
            context['my_medical_histories'] = MedicalHistory.objects.filter(recorded_by=user).count()
            context['my_diagnoses'] = Diagnosis.objects.filter(diagnosed_by=user).count()
            context['my_prescriptions'] = Prescription.objects.filter(prescribed_by=user).count()

            #recent activity
            context['recent_medical_histories'] = MedicalHistory.objects.filter(
                recorded_by=user
            ).select_related('patient')[:5]# we don't want to show the whole thing, just the last 5 patients attended to

            #active prescriptions
            context['active_prescriptions'] = Prescription.objects.filter(
                prescribed_by = user,
                status = 'ACTIVE'
            ).count()

            template = 'Users/doctor_dashboard.html'

        elif user.user_type == 'NURSE':
            context['profile'] = user.nurse_profile

            #Nurse specific stats in nurses dashboard
            context['recent_patient'] = Patient.objects.filter(is_active=True).count()
            context['active_diagnoses'] = Diagnosis.objects.filter(status='ACTIVE').count()
            context['active_prescriptions'] = Prescription.objects.filter(status='ACTIVE').count()

            template = 'Users/nurse_dashboard.html'

        elif user.user_type == 'ADMIN':
            context['profile'] = user.admin_profile

            #Admin specific stats on admin dashboard
            context['total_doctors'] = User.objects.filter(user_type='DOCTOR', is_active=True).count()
            context['total_nurses'] = User.objects.filter(user_type='NURSE', is_active=True).count()
            context['total_medical_histories'] = MedicalHistory.objects.count()
            context['total_diagnoses'] = Diagnosis.objects.count()
            context['total_prescriptons'] = Prescription.objects.count()

            #Newly created patients
            context['recent_patients'] = Patients.objects.filter(
                created_by=user
            ).order_by('-created_at'[:5])

            template = 'Users/admin_dashboard.html'
        
        else:
            template = 'Users/dashboard.html'

    except ImportError: #If records app is yet to be migrated, revert to using the basic template
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
    
    return render(request, template, context)


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
            messages.success(request, f'Welcome back, {user.get_full_name() or user.username}!')
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
