from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.models import Q, Count
from django.core.paginator import Paginator
from .models import Patient, MeedicalHistory, Diagnosis, Prescription
from .decorators import (
    admin_required, doctor_required, doctor_or_admin_required,
    medical_staff_required, can_edit_records, can_create_patients,
)

# Create your views here.


@login_required
@medical_staff_required
def patient_list(request):
    #Patients search functionality
    query = request.GET.get('q', '')
    patients_list = Patients.object.filter(is_active=True)

    #Search func proper
    if query:
        patients_list = patients_list.filter(
            Q(patient_id__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(phone_number__icontains=query) |
            Q(email__icontains=query) 
        )
    
    #Pagination
    paginator = Paginator(patients_list=20) #20 patients per page
    page_number = request = request.GET.get('page')
    patients = paginator.get_page(page_number)

    context = {
        'patients': patients,
        'query': query,
        'total_patients': Patients.object.filter(is_active=True).count(),
    }
    return render(request, 'records/patient_list.html', context)


@login_required
@medical_staff_required
def patient_detiail(request, patient_id):
    #Detailed patient info and medical records
    patient = get_object_or_404(Patient, patient_id=patient_id)

    #Getting all related records
    medical_histories = patient.medical_histories.all()
    diagnoses = patient.diagnoses.all()
    prescriptions = patient.prescriptions.all()

    #Checking if user can edit
    can_edit = can_edit_records(request.user)

    context = {
        'patient': patient,
        'medical_histories': medical_histories,
        'diagnoses': diagnoses,
        'prescriptions': prescriptions,
        'can_edit': can_edit,
    }
    return render(request, 'records/patient_detail.html', context)

@login_required
@admin_required
def patient_create(request):
    #Create new patient
    if request.method == 'POST':
        try:
            patient = Patient.objects.create(
                first_name = request.POST.get('first_name'),
                last_name = request.POST.get('last_name'),
                date_of_birth = request.POST.get('date_of_birth'),
                gender = request.POST.get('gender'),
                blood_group = request.POST.get('blood_group', ''),
                phone_number = request.POST.get('phone_number'),
                email = request.POST.get('email'),
                address = request.POST.get('address'),
                emergency_contact_name = request.POST.get('emergency_contact_name'),
                emergency_contact_phone = request.POST.get('emergency_contact_phone'),
                emergency_contac_relation = request.POST.get('emergency_contact_relation'),
                allergies = request.POST.get('allergies', ''),
                chronic_conditions = request.POST.get('chronic_conditions', ''),
                created_by = request.user
            )
            messages.success(request, f'Patient {patient.get_full_name()} ceated successfully! Patient ID: {patient.patient_id}')
            return redirect('patient_detail', patient_id=patient.patient_id)
        except Exception as e:
            messages.error(request, f'Error creating patient: {str(e)}')

    return render(request, 'records/patient')

@login_required
@doctor_or_admin_required
def medical_history_create(request, patient_id):
    #Create medical history record for a patient(doctors and admin only)
    patient = get_object_or_404(Patient, patient_id=patient_id)

    if request.method == 'POST':
        try:
            medical_history = MedicalHstory.objects.create(
                patient = patient,
                date = request.POST.get('date'),
                chief_complaint = request.POST.get('chief_complaint'),
                present_illness = request.POST.get('present_illness'),
                past_medical_history = request.POST.get('past_medical_history', ''),
                family_history = request.POST.get('family_history'), '',
                social_history = request.POST.get('social_history', ''),
                temperature = request.POST.get('temperature') or None,
                blood_pressure = request.POST.get('blood_pressure', ''),
                pulse_rate = request.POST.get('pulse_rate') or None,
                respiratory_rate = request.POST.get('respiratory_rate') or None,
                weight = request.POST.get('weight') or None,
                height = request.POST.get('heigth') or None,
                physical_examination_request = request.POST.get('physical_examination', ''),
                doctor_notes = request.POST.get('doctor_notes', '')
            )
            messages.success(request, 'Medical history record created successfully!')
            return redirect('patient_detail', patient_id=patient.patient_id)
        except Exception as e:
            messages.error(request, f'Error creating medical history': {str(e)})

    context = {
        'patient': patient,
    }
    return render(request, 'records/medical_history_create.html', context)
    