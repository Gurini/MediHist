from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count
from django.core.paginator import Paginator
from .models import Patient, MedicalHistory, Diagnosis, Prescription
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
    patients_list = Patient.objects.filter(is_active=True)

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
    paginator = Paginator(patients_list, 20) #20 patients per page
    page_number = request = request.GET.get('page')
    patients = paginator.get_page(page_number)

    context = {
        'patients': patients,
        'query': query,
        'total_patients': Patient.objects.filter(is_active=True).count(),
    }
    return render(request, 'records/patient_list.html', context)


@login_required
@medical_staff_required
def patient_detail(request, patient_id):
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

    return render(request, 'records/patient.html')

@login_required
@doctor_or_admin_required
def medical_history_create(request, patient_id):
    #Create medical history record for a patient(doctors and admin only)
    patient = get_object_or_404(Patient, patient_id=patient_id)

    if request.method == 'POST':
        try:
            medical_history = MedicalHistory.objects.create(
                patient=patient,
                date=request.POST.get('date'),
                chief_complaint=request.POST.get('chief_complaint'),
                present_illness=request.POST.get('present_illness'),
                past_medical_history=request.POST.get('past_medical_history', ''),
                family_history=request.POST.get('family_history', ''),
                social_history=request.POST.get('social_history', ''),
                temperature=request.POST.get('temperature') or None,
                blood_pressure=request.POST.get('blood_pressure', ''),
                pulse_rate=request.POST.get('pulse_rate') or None,
                respiratory_rate=request.POST.get('respiratory_rate') or None,
                weight=request.POST.get('weight') or None,
                height=request.POST.get('height') or None,
                physical_examination=request.POST.get('physical_examination', ''),
                doctor_notes=request.POST.get('doctor_notes', ''),
                recorded_by=request.user
            )
            messages.success(request, 'Medical history record created successfully!')
            return redirect('patient_detail', patient_id=patient.patient_id)
        except Exception as e:
            messages.error(request, f'Error creating medical history: {str(e)}')

    context = {
        'patient': patient,
    }
    return render(request, 'records/medical_history_create.html', context)


@login_required
@doctor_or_admin_required
def diagnosis_create(request, patient_id):
    #Create a diagnosis(doctors and admin, but strictly reserved for doctors)
    patient = get_object_or_404(Patient, patient_id=patient_id)
    medical_histories = patient.medical_histories.all()

    if request.method == 'POST':
        try:
            medical_history_id = request.POST.get('medical_history')
            medical_history = None
            if medical_history_id:
                medical_history = MedicalHistory.objects.get(id=medical_history_id)

            diagnois = Diagnosis.objects.create(
                patient=patient,
                medical_history = medical_history,
                diagnosis_date = request.POST.get('diagnosis_date'),
                condition = request.POST.get('condition'),
                icd_code = request.POST.get('icd_code', ''),
                severity = request.POST.get('severity'),
                status = request.POST.get('status'),
                description = request.POST.get('descrption'),
                symptoms = request.POST.get('symptoms', ''),
                test_results = request.POST.get('test_results', ''),
                treatment_plan = request.POST.get('treatment_plan', ''),
                follow_up_date = request.POST.get('follow_up_date') or None,
                notes = request.POST.get('notes', ''),
                diagnosed_by = request.user
            )
            messsages.success(request, 'Diagnosis created successfully!')
            return redirect('patient_detail', patient_id=patient.patient_id)
        except Exception as e:
            messages.error(request, f'Error creating diagnosis: {str(e)}')

    context = {
        'patient': patient,
        'medical_histories': medical_histories,
    }
    return render(request, 'records/diagnosis_create.html', context)


@login_required
@doctor_or_admin_required
def prescription_create(request, patient_id):
    #Create anew presxriptio, works for admins as well as doctors(but going forward will be reserved for doctors only)
    patient = get_object_or_404(Patient, patient_id=patient_id)
    diagnoses = patient.diagnoses.filter(status__in=['ACTIVE', 'CHRONIC']) #Only active and chronic diagnoses should be available for prescription creation
    
    if request.method == 'POST':
        try:
            diagnosis_id = request.POST.get('diagnosis')
            diagnosis = None
            if diagnosis_id:
                diagnosis = Diagnosis.objects.get(id=diagnosis_id)

            prescription = Prescription.objects.create(
                patient = patient,
                diagnosis = diagnosis,
                prescription_date = request.POST.get('prescription_date'),
                medication_name = request.POST.get('medication_name'),
                dosage = request.POST.get('dosage'),
                frequency = request.POST.get('frequency'),
                route = request.POST.get('route'),
                duration = request.POST.get('duration'),
                start_date = request.POST.get('start_date') or None,
                end_date = request.POST.get('end_date'),
                quantity = request.POST.get('quantity', ''),
                refills = request.POST.get('refill', 0),
                instructons = request.POST.get('instructions'),
                special_instructions = request.POST.get('special_instructions'),
                status = request.POST.get('status'),
                notes = request.POST.get('notes', ''),
                prescribed_by = request.user
            )
            messages.success(request, 'Prescription created succressfully!')
            return redirect('records:patient_detail', patient_id=patient.patient_id)
        except Exception as e:
            messages.error(request, f'Error creating prescription: {str(e)}')
    
    context = {
        'patient': patient,
        'diagnoses': diagnoses,
    }
    return render(request, 'records/prescription_create.html', context)


@login_required
@medical_staff_required
def search_patients(request):
    #Patients search
    query = request.GET.get('q', '')
    results = []

    if query:
        results = Patient.objects.filter(
            Q(patient_id__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(phone_number__icontains=query) |
            Q(email__icontains=query)
        ).filter(is_active=True)[:15] #returns 15 results on searches 
        
    context = {
        'query': query,
        'results': results,
    }

    return render(request, 'records/search_results.html', context)