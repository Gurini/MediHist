from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps


def admin_required(view_func):
    #This decorator checks if user is an admin
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if request.user.user_type != 'ADMIN' and not request.user.is_superuser:
            messages.error(request, 'You do not have permission to access this page')
            return redirect('dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper


def doctor_required(view_func):
    #This dec checks if user is a doctor
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if request.user.user_type != 'DOCTOR' and not request.user.is_superuser:
            messages.error(request, 'Only doctors can access this page.')
            return redirect('dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper


def doctor_or_admin_required(view_func):
    #This dec schecks if user is doctor or admin
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if request.user.user_type not in ['DOCTOR', 'ADMIN'] and not request.user.is_superuser:
            messages.error(request, 'You do not permission to access this page.')
            return redirect('dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper


def medical_staff_required(view_func):
    #This dec checks if user is a medical staff(doctor or nurse)
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if request.user.user_type not in ['DOCTOR', 'NURSE'] and not request.user.is_superuser:
            messages.error(request, 'Only medical staffs can access this page.')
            return redirect('dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper


def can_edit_records(user):
    # Check if user can edit medical records(doctors and admin only)
    return user.user_type in ['DOCTOR', 'ADMIN'] or user.is_superuser


def can_view_records(user):
    # Check if user can edit medical records(free for all)
    return user.user_type in ['DOCTOR', 'ADMIN', 'NURSE'] or user.is_superuser

def can_create_patients(user):
    # Check if user can create medical records(admin only)
    return user.user_type == 'ADMIN' or user.is_superuser