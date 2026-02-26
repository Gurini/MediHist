from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from django.core.paginator import Paginator
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
    category_filter = request.GET.get('category', '')
    query = request.GET.get('Q', '')
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
    tests_page = paginator.get_page(page_number)

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


@login_required
@doctor_or_admin_required
def lab_test_create(request, patient_id):
    #Order a new lab test(for doctors and admin only)
    patient = get_object_or_404(Patient, patient_id=patient_id)
    diagnoses = patient.diagnoses.filter(status__in=['ACTIVE', 'CHRONIC', 'UNDER_OBSERVATION'])

    if request.method == 'POST':
        try:
            diagnosis_id = request.POST.get('diagnosis')
            diagnosis = None
            if diagnosis_id:
                diagnosis = Diagnosis.objects.get(id=diagnosis_id)


            lab_test = LabTest.objects.create(
                patient = patient,
                diagnosis = diagnosis,
                test_name = request.POST.get('test_name'),
                category = request.POST.get('category'),
                urgency = request.POST.get('urgency', 'ROUTINE'),
                instructions = request.POST.get('instructions', ''),
                notes = request.POST.get('notes'),
                ordered_by = request.user,
                status = 'ORDERED'
            )
            messages.success(request, f'Lab test "{lab_test.test_name}" ordered successfully and added to queue.')
            return redirect('records:patient_detail', patient_id=patient.patient_id)
        except Exception as e:
            messages.error(request, f'Error ordering lab test: {str(e)}')

    context = {
        'patient': patient,
        'diagnoses': diagnoses,
        'category_choices': LabTest.CATEGORY_CHOICES,
        'urgency_choices': LabTest.URGENCY_CHOICES,
    }
    return render(request, 'records/lab_test_create.html', context)


@login_required
@all_staff_required
def lab_test_detail(request, test_id):
    #Viewing lab test details and results(files in general)
    lab_test = get_object_or_404(LabTest, id=test_id)
    result = getattr(lab_test, 'result', None)
    files = result.files.all() if result else []

    can_upload = request.user.user_type in ['LAB', 'DOCTOR', 'ADMIN'] or request.user.is_superuser
    can_interpret = request.user.user_type in ['DOCTOR', 'ADMIN'] or request.user.is_superuser
    can_pickup = (
        request.user.user_type == 'LAB' and 
        lab_test.status == 'ORDERED' and 
        lab_test.assigned_to is None
    )
    is_assigned_to_me = lab_test.assigned_to == request.user

    context = {
        'lab_test': lab_test,
        'result': result,
        'files': files,
        'can_upload': can_upload,
        'can_interpret': can_interpret,
        'can_pickup': can_pickup,
        'is_assigned_to_me': is_assigned_to_me,
    }

    return render(request, 'records/lab_test_detail.html', context)


@login_required
def lab_test_pickup(request, test_id):
    #Lab personnel picks up test from general queue
    if request.user.user_type != 'LAB' and not request.user.is_superuser:
        messages.error(request, 'Only lab personnel can pickup tests from the queue')
        return redirect('records:lab_test_list')

    lab_test = get_object_or_404(LabTest, id=test_id)

    if lab_test.assigned_to:
        messages.warning(request, f'This test has already been picked up by {lab_test.assigned_to.get_full_name()}.')
        return redirect('records:lab_test_detail', test_id=test_id)

    if lab_test.status != 'ORDERED':
        messages.warning(request, 'This test is not available for pickup.')
        return redirect('records:lab_test_detail', test_id=test_id)

    lab_test.assigned_to = request.user
    lab_test.assigned_to = timezone.now()
    lab_test.assigned_to = 'IN_PROGRESS'
    lab_test.save()

    messages.success(request, f'You have picked up "{lab_test.test_name}" for {lab_test.patient.get_full_name()}.')
    return redirect('records:lab_test_detail', test_id=test_id)


#Lab result views

@login_required
@lab_or_doctor_or_admin_required
def lab_result_create(request, test_id):
    #Lab personnel uploads files and enters results for lab test
    lab_test = get_object_or_404(LabTest, id=test_id)

    #Only the assigned lab personnel or any lab/doctor/admin can sbmit results
    if hasattr(lab_test, 'result'):
        messages.warning(request, 'Results have already been submitted for this test. You can add me files instead')
        return redirect('records:lab_result_add_file', test_id=test_id)

    if lab_test.status == 'CANCELLED':
        messages.error(request, 'Cannot add results to a cancelled test.')
        return redirect('records:lab_test_detail', test_id=test_id)
    
    if request.method == 'POST':
        try:
            result = LabResult.objects.create(
                lab_test = lab_test,
                result_date = request.POST.get('result_date'),
                result_summary = request.POST.get('result_summary'),
                lab_notes = request.POST.get('lab_notes'),
                scan_notes = request.POST.get('scan_note'),
                uploaded_by = request.user,
            )

            #adling file uploads
            files = request.FILES.getlist('result_files')
            file_types = request.POST.getlist('file_types')
            file_descriptions = request.POST.getlist('file_descriptions')
            file_notes_list = request.POST.getlist('file_notes')


            for i, uploaded_file in enumerate(files):
                LabResultFile.objects.create(
                    lab_result= result,
                    file = uploaded_file,
                    file_type = file_types[i] if i < len(file_types) else 'OTHER',
                    file_name = uploaded_file.name,
                    description = file_descriptions[i] if i < len(file_descriptions) else '',
                    file_notes = file_notes_list[i] if i < len(file_notes_list) else '',
                    uploaded_by = request.user,
                )
            
            #Now update test status to completed
            lab_test.status = 'COMPLETED'
            lab_test.save()

            messages.success(request, 'Lab result submitted successfully. The ordering Doctor has been notified')
            return redirect('records:lab_test_detail', test_id=test_id)
        except Exception as e:
            messages.error(request, f'Error submitting results: {str(e)}')

    context = {
        'lab_test': lab_test,
        'file_type_choices': LabResultFile.FILE_TYPE_CHOICES,
        'is_imaging': lab_test_category == 'IMAGING',
    }
    return render(request, 'records/lab_result_create.html', context)


@login_required
@lab_or_doctor_or_admin_required
def lab_result_add_file(request, test_id):
    #Additional files to an already existent lab result

    lab_test = het_object_or_404(LabTest, id=test_id)
    result = getattr(lab_test, 'result', None)

    if not result:
        messages.error(request, 'No results found. Please submit results first')
        return redirect('records:lab_result_create', test_id=test_id)

    if requestmethod == 'POST':
        try:
            files = request.FILES.getlist('result_files')
            file_types = request.POST.getlist('file_types')
            file_descriptions = request.POST.getlist('file_descriptions')
            file_note_list = request.POST.getlist('file_notes')

            for i, uploaded_file in enumerate(files):
                LabResultFile.objects.create(
                    lab_result = result,
                    file = upload_file,
                    file_type = file_types[i] if i < len(file_types) else 'OTHER',
                    file_name = uploaded_file.name,
                    description = file_descriptions[i] if i < len(file_descriptions) else '',
                    file_notes = file_notes_list[i] if i < len(file_notes_list) else '',
                    uploaded_by = request.user,
                )

            messages.success(request, f'{len(files)} file(s) added successfully.')
            return redirect('records:lab_test_detail', test_id=test_id)
        except Exception as e:
            messages.error(request, f'Error uploading files: {str(e)}')

    context = {
        'lab_test': lab_test,
        'result': result,
        'file_type_choices': LabResultFile.FILE_TYPE_CHOICES,
    }
    return render(request, 'records/lab_result_add_file.html', context)


@login_required
@doctor_or_admin_required
def lab_result_interpret(request, test_id):
    #Doctor adds interpretation and flags abnormal results
    lab_test = get_object_or_404(LabTest, id=test_id)
    result = get_object_or_404(LabResult, lab_test=lab_test)

    if request.method == 'POST':
        try:
            result.is_abnormal = request.POST.get('is_abnormal') == 'on'
            result.interpretation = request.POST.get('interpretation', '')
            result.interpreted_by = request.user
            result.interpreted_at = timezone.now()
            resulu.save()

            #Update the test status now to REVIEWED
            lab_test.status = 'REVIEWED'
            lab_test.save()

            status = '⚠️ ABNORMAL -' if result.is_abnormal else ''
            messages.success(request, f'Results {status}reviewed and saved successfully.')
            return redirect('records:lab_test_detail', test_id=test_id)
        except Exception as e:
            messages.error(request, f'Error saving interpretation: {str(e)}')

        
    context = {
        'lab_test': lab_test,
        'result': result,
    }

    return render(request, 'records/lab_result_interpret.html', context)