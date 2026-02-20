from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from django.core.paignator import Paginator
from .models import Patient, Diagnosis, LabTest, LabResult, LabResultFile
from .decorators import (
    admin_required, doctor_or_admin_required, all_staff_required,
    lab_or_doctor_or_admin_required  
)

#LAb tests specific views

@login_required
@all_staff_required
def lab_test_list(request):
    #List all lab tests with filters(can be accessed by all staff)
    #Meanwhile lab personnel see queue and their assigned tests

    status_filter = request.GET.get('status', '')
    categoty_filter = request.GET.get('category', '')
    uery = request.GET.get('Q', '')
    show_queue = request.GET.get('Q', '')

    tests = LabTest.objects.select_related('patient', 'ordered_by', 'assigned_to').all()

    #LAb personnel defaults to show queue and tests
    if request.user.user_type == 'LAB' and not status_filter and not show_queue == 'false':
        if show_queue == 'mine':
            tests = tests.filter(assigned_to=request.user)
        else:
            #Default (show queue and assigned list)
            test = tests.filter(
                Q(assigned_to=request.user) | Q(assigned_to__isnull=True, status='ORDERED')
            )

        if status_filter:
            tests = tests.filter(status=status_filter)
        if category_filter:
            tests = tests.filter(category=category_filter)
        if query:
            tests = tests.filter(
                Q(patient__first_name__icontains=query) |
                Q(patient__last_name__icontains=query) |
                Q(patient__patient_id__icontains=query) |
                Q(test_name__icontains=query) 
            )

        paginator = Paginator(tests, 20)
        page_number = request.GET.get('page')
        tests_page = pagiantor.get.get_page(page_number)

        #Queue count om lab personnel dashboard
        queue_count = LabTest.objects.filter(status='ORDERED', assigned_to__isnull=True).count()

        context = {
            'tests': tests_page,
            'status_filter': status_filter,
            'category_filter': category_filter,
            'query': query,
            'queue_count': queue_count,
            'status_choices': LabTest.STATUS_CHOICES,
            'category_choices': LabTest.CATEGORY_CHOICES,
        }
        return render(request, 'records/lab_test_list.html', context)