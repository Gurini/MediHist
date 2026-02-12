from django.contrib import admin
from .models import Patient, MedicalHistory, Diagnosis, Prescription

# Register your models here.
class MedicalHistoryInline(admin.TabularInline):
    model = MedicalHistory
    extra = 0
    fields = ['date', 'chief_complaint', 'recorded_by']
    readonly_fields = ['recorded_by']
    can_delete = False

class DiagnosisInline(admin.TabularInline):
    model = Diagnosis
    extra = 0
    fields = ['diagnosis_date', 'condtion', 'severity', 'diagnosed_by']
    readonly_fields = ['diagnosed_by']
    can_delete = False

class PrescriptionInline(admin.TabularInline):
    model = Prescription
    extra = 0
    fields = ['prescription_date', 'medication', 'frequency', 'status', 'dosage', 'prescribed_by']
    readonly_fields = ['prescribed_by']
    can_delete = False

@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ['patient_id', 'full_name_display', 'date_of_birth', 'gender', 'blood_group', 'phone_number', 'is_active', 'created_at']
    list_filter = ['gender', 'blood_group', 'is_active', 'created_at']
    search_fields = ['patient_id', 'first_name', 'last_name', 'phone_number', 'email']
    readonly_fields = ['patient_id', 'created_by', 'created_at', 'updated_at']

    fieldsets = (
        ('Basic Information', {
            'fields': ('patient_id', 'first_name', 'last_name', 'date_of_birth', 'gender', 'blood_group')
        }),
        ('Contact Information', {
            'fields': ('phone_number', 'email', 'address')
        }),
        ('Emergency Contact', {
            'fields': ('emergency_contact_name', 'emergency_contact_phone', 'emergency_contact_relation')
        }),
        ('Medical Information', {
            'fields': ('allergies', 'chronic_conditions')
        }),
        ('System Information', {
            'fields': ('is_active', 'created_by', 'created_at', 'updated_at'),
            'classes': ('collapse')
        }),
    )

    def full_name_display(self, obj):
        return obj.get_full_name()
    full_name_display.short_description = 'Name'

    def save_model(self, request, obj, form, change):
        #Set recorded_by to current user if not set
        if not obj.pk:
            obj.recorded_by = request.user
        super().save_model(request, obj, form, change)

@admin.register(Diagnosis)
class DiagnosisAdmin(admin.ModelAdmin):
    list_display = ['patient', 'condition', 'diagnosis_date', 'severity', 'status', 'diagnosed_by', 'created_at']
    list_filter = ['severity', 'status', 'diagnosis_date', 'created_at']
    search_fields = ['patient__patient_id', 'patient__first_name', 'patient__last_name', 'condition', 'icd_code']
    readonly_fields = ['diagnosed_by', 'created_at', 'updated_at']

    fieldsets = (
        ('Patient & Date', {
            'fields': ('patient', 'medical_history', 'diagnosis_date')
        }),
        ('Diagnosis Details', {
            'fields': ('condition', 'icd_code', 'severity', 'status')
        }),
        ('Clinical Information', {
            'fields': ('description', 'symptoms', 'test_results')
        }),
        ('Treatment & Follow-up', {
            'fields': ('treatment_plan', 'follow_up_date', 'notes')
        }),
        ('System Information', {
            'fields': ('diagnosed_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        #Setting it to diagnosed by current user, if it is not set
        if not obj.pk:
            obj.diagnosed_by = request.user
        super().save_model(request, obj, form, change)

admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = ['patient', 'medication_name', 'dosage', 'frequency', 'prescription_date', 'status', 'prescribe_by', 'created_at']
    list_filter = ['status', 'frequency', 'prescription_date', 'created_at']
    search_fields = ['patient__patient_id', 'patient__first_name', 'patient__last_name', 'medication_name']
    readonly_fields = ['prescribed_by', 'created_by', 'updated_by']

    fieldset = (
        ('Patient & Diagnosis', {
            'fields': ('patient', 'diagnosis', 'prescription_date')
        }),
        ('Medication Details', {
            'fields': ('medication_name', 'dosage', 'frequency', 'route')
        }),
        ('Duration & Quantity', {
            'fields': ('duration', 'start_date', 'end_date', 'quantity', 'refills')
        }),
        ('Instructions', {
            'fields': ('instructions', 'special_instructions')
        }),
        ('Status & Notes', {
            'fields': ('status', 'notes')
        }),
        ('System Information', {
            'fields': ('prescribed_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def save_model(self, request, obj, form, change):
        #Set prescribed_by to current user if it is not already set
        if not obj.pk:
            obj.prescribed_by = request.user
        super().save_model(request, obj, form, change)