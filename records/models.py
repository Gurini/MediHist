from django.db import models
from django.core.validators import RegexValidator
from Users.models import User


# Create your models here.

class Patient(models.Model):
    #Patient model for storing information
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    )

    BLOOD_GROUP_CHOICES = (
        ('A+', 'A+'),
        ('A-', 'A-'),
        ('B+', 'B+'),
        ('B-', 'B-'),
        ('AB+', 'AB+'),
        ('AB-', 'AB-'),
        ('O+', 'O+'),
        ('O-', 'O-'),
    )

    #pATIENTS Basic Info
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    blood_group = models.CharField(max_length=3, choices=BLOOD_GROUP_CHOICES, blank=True)


    #Contact Info
    phone_regex = RegexValidator(
        regex = r'^\+?1?\d{9,15}$',
        message = "Phone number must be entered in the format: '+123456'. Up to 15 digits allowed"
    
    )
    phone_number = models.CharField(validators=[phone_regex], max_length=17)
    email = models.EmailField(blank=True)
    address = models.TextField()

    #Emergency contact
    emergency_contact_name = models.CharField(max_length=200)
    emergency_contact_phone = models.CharField(validators=[phone_regex], max_length=17)
    emergency_contact_relation = models.CharField(max_length=100
    )

    #Medical Info
    allergies = models.TextField(blank=True, help_text="List any known allergies")
    chronic_conditions = models.TextField(blank=True, help_text="List any chronic conditions")

    #System
    patient_id = models.CharField(max_length=20, unique=True, editable=False)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='patient_created')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)


    class Meta:
        verbose_name = 'Patient'
        verbose_name_plural = 'Patients'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.patient_id} - {self.get_full_name()}"

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    def get_age(self):
        from datetime import date
        today = date.today()
        return today.year - self.date_of_birth.year - (
            (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
        )

    def save(self, *args, **kwargs):
        #Generate patient ID
        if not self.patient_id:
            #Get last patients ID and increment it
            last_patient = Patient.objects.all().order_by('id').last()
            if last_patient and last_patient.patient_id:
                try: #Extract numeric part of patient_id and increment
                    last_id = int(last_patient.patient_id.split('-')[1])
                    new_id = last_id + 1
                except (IndexError, ValueError):
                    #if patient_id format is unexpected, fallback to counting total patients
                    new_id = Patient.objects.count() + 1
            else:
                new_id = 1
            self.patient_id = f'PT-{new_id:06d}'
        super().save(*args, **kwargs)



class MedicalHistory(models.Model):
    #Medical history for patients
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='medical_histories')
    date = models.DateField()
    chief_complaint = models.TextField(help_text="Main reason for visit")
    present_illness = models.TextField(help_text="History of preset illness")
    past_medical_history = models.TextField(blank=True, help_text="Relevant past medical history")
    family_history = models.TextField(blank=True, help_text="Relevant family medical history")
    social_history = models.TextField(blank=True, help_text="Lifestyle factors, occupation, etc.")

    #Physical examination
    temperature = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True, help_text="In Farenheit")
    blood_pressure = models.CharField(max_length=20, blank=True, help_text="e.g., 120/80")
    pulse_rate = models.IntegerField(null=True, blank=True, help_text="Beats per minute")
    respiratory_rate = models.IntegerField(null=True, blank=True, help_text="Breaths per minute")
    weight = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="In kg")
    height = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="In cm")

    #Physical examination
    physical_examination = models.TextField(blank=True, help_text="Physical examination findings")

    #notes
    doctor_notes = models.TextField(blank=True, help_text="Additional notes by the doctor")

    #System
    recorded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='medical_histories_recorded')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Medical History'
        verbose_name_plural = 'Medical Histories'
        ordering = ['-date', '-created_at']


    def __str__(self):
        return f"{self.patient.get_full_name()} - {self.date}"

    
    def get_bmi(self):
        #Attainimg the body's mass index if height and weight are available
        if self.height and self.weight:
            height_m = float(self.height / 100) #coverting cm to meters
            #calculation for BMI
            bmi = float(self.weight) / (height_m ** 2)
            return (bmi, 2)

        return None


class Diagnosis(models.Model):
    #Diagnosis records for patients
    SEVERITY_CHOICES = (
        ('MILD', 'Mild'),
        ('MODERATE', 'Moderate'),
        ('SEVERE', 'Severe'),
        ('CRITICAL', 'Critical'),
    )

    STATUS_CHOICES = (
        ('ACTIVE', 'Active'),
        ('RESOLVED', 'Resolved'),
        ('CHRONIC', 'Chronic'),
        ('UNDER_OBSERVATION', 'Under Observation'),
    )

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='diagnoses')
    medical_history = models.ForeignKey(MedicalHistory, on_delete=models.CASCADE, related_name='diagnoses', null=True, blank=True)

    diagnosis_date = models.DateField()
    condition = models.CharField(max_length=200, help_text="Name of the condition/disease")
    icd_code = models.CharField(max_length=20, blank=True, help_text="ICD-10 code")
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, default='MODERATE')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ACTIVE')

    description = models.TextField(help_text="Detailed description of diagnosis")
    symptoms = models.TextField(blank=True, help_text="List of symptoms")
    test_results = models.TextField(blank=True, help_text="Relevant test results")

    treatment_plan = models.TextField(blank=True, help_text="Recommended treatment plan")
    follow_up_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)

    #System
    diagnosed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="diagnoses_made")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    class Meta:
        verbose_name = 'Diagnosis'
        verbose_name_plural = 'Diagnoses'
        ordering = ['-diagnosis_date', '-created_at']
        
    def __str__(self):
        return f"{self.patient.get_full_name()} - {self.condition} ({self.diagnosis_date})"


class Prescription(models.Model):
    #Prescription record for patients
    DOSAGE_FREQUENCY_CHOICES = (
        ('ONCE_DAILY', 'Once Daily'),
        ('TWICE_DAILY', 'Twice Daily'),
        ('THREE_TIMES_DAILY', 'Three Times Daily'),
        ('FOUR_TIMES_DAILY', 'Four Times Daily'),
        ('EVERY_4_HOURS', 'Every 4 Hours'),
        ('EVERY_6_HOURS', 'Every 6 Hours'),
        ('EVERY_8_HOURS', 'Every 8 Hours'),
        ('EVERY_12_HOURS', 'Every 12 Hours'),
        ('AS_NEEDED', 'As Needed'),
        ('WEEKLY', 'Weekly'),
        ('MONTHLY', 'Monthly'),
    )

    STATUS_CHOICES = (
        ('ACTIVE', 'Active'),
        ('COMPLETED', 'Completed'),
        ('DISCONTINUED', 'Discontinued'),
        ('ON_HOLD', 'On Hold'),
    )

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='prescriptions')
    diagnosis = models.ForeignKey(Diagnosis, on_delete=models.SET_NULL, null=True, blank=True, related_name='prescriptions')

    #Prescription
    prescription_date = models.DateField()
    medication_name = models.CharField(max_length=200)
    dosage = models.CharField(max_length=100, help_text="e.g., 500mg, 10ml")
    frequency = models.CharField(max_length=30, choices=DOSAGE_FREQUENCY_CHOICES)
    route = models.CharField(max_length=50, help_text="e.g., Oral, Intravenous, Topical")

    duration = models.CharField(max_length=100, help_text="e.g., 7 days, 2 weeks, 1 month")
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)

    quantity = models.CharField(max_length=50, blank=True, help_text="Total quantity to be dispensed")
    refills = models.IntegerField(default=0, help_text="Number of refills allowed")

    #Additional instruction
    instructions = models.TextField(help_text="Detailed instructions for patient")
    special_instructions = models.TextField(blank=True ,help_text="Any special instructions or warnings")

    #status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ACTIVE')
    notes = models.TextField(blank=True)

    prescribed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='prescriptions_made')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    class Meta:
        verbose_name = 'Prescription'
        verbose_name_plural = 'Prescriptions'
        ordering = ['-prescription_date', '-created_at']

    def __str_(self):
        return f"{self.patient.get_full_name()} - {self.medication_name} ({self.prescription_date})"
    
    def is_expired(self):
        #check if prescripion has expired
        if self.end_date:
            from datetime import date
            return date.today > self.end_date
        return False


def lab_result_file_path(instance, filename):
    #Genreating upload path for lab result files
    return f'lab_results/{instance.lab_result.lab_test.patient.patient_id/{filename}}'


def validate_file_size(value):
    #validate that file is under 12mb
    limit = 12 * 1024 * 1024 #12mb in bytes
    if value.size > limit:
        from dango.core.exceptions import ValidationError
        raise ValidationError(f'File size must be under 12MB. Your file is {value.size / (1024*1024):.1f}MB.')


class LabTest(models.Model):
    #Labb test order - created by doctor & goes into a general queue for lab personnel to pick up
    CATEGORY_CHOICES = (
        ('BLOOD', 'Blood'),
        ('IMAGING', 'Imaging (X-Ray, CT, MRI, Ultrasound)'),
        ('URINE', 'Urine Test'),
        ('CARDIAC', 'Cardiac (ECG, Echo)'),
        ('MICROBIOLOGY', 'Microbiology'),
        ('PATHOLOGY','Pathology'),
        ('OTHER', 'Other / Custom')
    )

    STATUS_CHOICES = (
        ('ORDERED', 'Ordered'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('REVIEWED', 'Reviewed by Doctor'),
        ('CANCELLED', 'Cancelled'),
    )

    URGENCY_CHOICES = (
        ('ROUTINE', 'Routine'),
        ('URGENT', 'Urgent'),
        ('STAT', 'STAT (Immediate)'),
    )

    #critical info
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='lab_tests')
    diagnosis = models.ForeignKey(Diagnosis, on_delete=models.SET_NULL, null=True, blank=True, related_name='lab_tests')
    test_name = models.CharField(max_length=200)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    urgency = models.CharField(max_length=10, choices=URGENCY_CHOICES, default='ROUTINE')
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='ORDERED')

    #Instruction or note from ordering doctor
    instructions = models.TextField(blank=True, help_text="Instruction for the lab personnel")
    notes = models.TextField(blank=True)

    #Who picked it up from queue
    assigned_to = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        help_text="Lab Personnel who picked up this test"
    )
    assigned_at = models.DateTimeField(null=True, blank=True)

    #System Fields
    ordered_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='lab_tests_ordered')
    ordered_date = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Lab Test'
        verbose_name_plural = 'Lab Tests'
        ordering = ['-ordered_date']

    def __str__(self):
        return f"{self.patient.get_full_name()} - {self.test_name} ({self.get_status_display()})"

    def is_in_queue(self):
        #checks if test is in the general queue
        return self.status == 'ORDERED' and self.assigned_to is None

    def get_urgency_color(self):
        colors = {'ROUTINE': 'green', 'URGENT': 'orange', 'STAT': 'red'}
        return colors.get(self.urgency, 'grey')

    def get_status_color(self):
        colors = {
            'ORDERED': '#f39c12',
            'IN_PROGRESS': '#3498db',
            'COMPLETED': '#27ae60',
            'REVIEWED': '#8e44ad',
            'CANCELLED': '#e74c3c'
        }
        return colors.get(self.status, '#95a5a6')


class LabResult(models.Model):
    #Lab result created by lab result after completing the test
    lab_test = models.OneToOneField(LabTest, on_delete=models.CASCADE, related_name='result')

    #Result data
    result_date = models.DateField()
    result_summary = models.TextField(help_text="Summary of text results")
    lab_notes = models.TextField(blank=True, help_text="Lab Personnel observations and technical notes")

    #scan_notes
    scan_notes = models.TextField(blank=True, help_text='Specific notes for imaging/scans (body part, technique, contrast used, etc.)')
    is_abnormal = models.BooleanField(default=False, help_text='Flag f results are abnormal')
    interpretation = models.TextField(blank=True, help_text="Doctor's interprettation and clinical notes")
    interpretated_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='lab_results_interpreted'
    )
    interpreted_at = models.DateTimeField(null=True, blank=True)

    # system fields
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='lab_results_uploaded')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Lab Result'
        verbose_name_plural = 'Lab Results'
        ordering = ['-result_date']

    def __str__(self):
        abnormal = '⚠️ ABNORMAL' if self.is_abnormal else ''
        return f"{self.lab_test.test_name} - {self.result_date}{abnormal}"


class LabResultFile(models.Model):
    #Files from lab result uploaded by lab personnel
    FILE_TYPE_CHOICES = (
        ('PDF', 'PDF Report'),
        ('IMAGE', 'Image (JPG, PNG)'),
        ('scan', 'Medical Scan (DICOM / High-res image)'),
        ('OTHER', 'Other'),
    )

    lab_result = models.ForeignKey(LabResult, on_delete=models.CASCADE, related_name='files')
    file = models.FileField(upload_to=lab_result_file_path, validators=[validate_file_size])
    file_type = models.CharField(max_length=10, choices=FILE_TYPE_CHOICES)
    file_name = models.CharField(max_length=250, blank=True, help_text='Descriptive file for the file')
    description = models.CharField(max_length=500, blank=True, help_text='Brief description for this file')

    #Lab personnel note specific t a file
    file_notes = models.TextField(blank=True, help_text='Specific observation or notes about this file/scan')

    #system fields
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='lab_files_uploaded')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Lab Result File'
        verbose_name_plural = 'Lab Result Files'
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"{self.file_name or self.file.name} - ({self.get_file_type_display()})"

    def get_file_size_mb(self):
        #to get file size in mb
        try:
            return round(self.file.size / (1024 * 1024), 2)
        except Exception:
            return 0