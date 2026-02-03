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
    last_name = models.Charfield(max_length=100)
    date_of_birth = models.DateField()
    gender = models.Charfield(max_length=1, choices=GENDER_CHOICES)
    blood_group = models.Charfield(max_length=3, choices=BLOOD_GROUP_CHOICES, blank=True)


    #Contact Info
    phone_regex = RegexValidators(
        regex = r'^\+?1?\d{9,15}$',
        message = "Phone number must be entered in the format: '+123456'. Up to 15 digits allowed"
    
    )
    phone_number = models.CharField(validators=[phone_regex], max_length=17)
    email = models.EmalField(blank=True)
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
    patiendt_id = models.CharField(max_length=20, unique=True, editable=False)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='patient_created')
    created_at = models.DateTimeField(auto_add_now=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)


    class Meta:
        verbose_name = 'Patient'
        verbose_name_plural = 'Patients'
        ordering = ['created_at']

    def __str__(self):
        return f"{self.patient_id} - {self.get_full_name()}"

    def get_full_name(self):
        return f"{self.first_name} - {self.last_name()}"

    def get_age(self):
        from datetime import date
        today = date.today()
        return today.year - self.date_of_birth - (
            (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
        )

    def save(self, *args, **kwargs):
        #Generate patient ID
        if not self.patient_id:
            #Get last patients ID and increment it
            last_patient = Patient.objects.all().order_by('id').last()
            if last_patient:
                last_id = int(last_patient.patient_id.split('-')[1])
                new_id = last_id + 1
            else:
                new_id = 1
            self.patient_id = f'PT-{new_id:06d}'
        super().save(*args, **kwargs)



class MedicalHistory(models.Model):
    #Medical history for patients
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='medical_histories')
    date = models.DateField()
    chief_complaint = models.TextField(help_text="Main reaso for visit")
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
        ordering = ['-date', 'created_at']


    def __str__(self):
        return f{"self.patient.get_full_name() - self.date"}

    
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
    SEVERIT_CHOICES = (
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

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='diagnosis')
    medical_history = models.ForeignKey(MedicalHistory, on_delete=models.CASCADE, related_name="")