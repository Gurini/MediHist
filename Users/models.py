from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator

# Create your models here.
class User(AbstractUser):
    #Different Users
    USER_TYPE_CHOICES = (
        ('ADMIN', 'Admin'),
        ('DOCTOR', 'Doctor'),
        ('NURSE', 'Nurse'),
        ('LAB', 'Lab Personnel')
    )

    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES)
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 11 digits allowed."
    )
    phone_number = models.CharField(validators=[phone_regex], max_length=13, blank=True)
    email = models.CharField(max_length=50, blank=True) 
    date_of_birth = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return f"{self.username} ({self.get_user_type_display()})"
    
    def save(self, *args, **kwargs):
        #To override save to create corresponding profile based user type
        is_new = self.pk is None
        super().save(*args, **kwargs)

        #Create profile if user is saved
        if is_new:
            if self.user_type == 'DOCTOR':
                DoctorProfile.objects.get_or_create(user=self)
            elif self.user_type == 'NURSE':
                NurseProfile.objects.get_or_create(user=self)
            elif self.user_type == 'ADMIN':
                AdminProfile.objects.get_or_create(user=self)
            elif self.user_type == 'LAB':
                LabProfile.objects.get_or_create(user=self)

class DoctorProfile(models.Model):
    #Profile model for Doctors
    SPECIALIZATION_CHOICES = (
        ('GENERAL', 'General Practice'),
        ('PEDIATRICS', 'Pediatrics'),
        ('ORTHOPEDICS', 'Orthopedics'),
        ('DERMATOLOGY', 'Dermatology'),
        ('PSYCHIATRY', 'Psychiatry'),
        ('CARDIOLOGY', 'Cardiology'),
        ('NEUOROLOGY', 'Neurology'),
        ('RADIOLOGY', 'Radiology'),
        ('SURGERY','Surgery'),
        #mORE TO BE ADDED
        ('OTHER', 'Other'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='doctor_profile')
    license_number = models.CharField(max_length=50, unique=True)
    specialization = models.CharField(max_length=50, choices=SPECIALIZATION_CHOICES)
    years_of_experience = models.PositiveIntegerField(default=0)
    hospital_affiliation = models.CharField(max_length=200, blank=True)
    is_available = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Doctor Profile'
        verbose_name_plural = 'Doctor Profiles'
    
    def __str__(self):
        return f"Dr. {self.user.get_full_name()} - {self.get_specialization_display()}"

class NurseProfile(models.Model):
    #Info specific to Nurses
    SPECIALIZATION_CHOICES = (
        ('GENERAL', 'General Nursing'),
        ('PEDIATRIC', 'Pediatric Nursing'),
        ('EMERGENCY', 'Emergency Nursing'),
        ('ICU', 'Intensive Care'),
        ('SURGICAL', 'Surgical Nursing'),
        ('ONCOLOGY', 'Oncology Nursing'),
        ('GERIATRIC', 'Geriatric Nursing'),
        ('PSYCHIATRIC','Psychiatric Nursing'),
        ('OTHER', 'Other'),       
    )


    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='nurse_profile')
    license_number = models.CharField(max_length=50, unique=True)
    specialization = models.CharField(max_length=50, choices=SPECIALIZATION_CHOICES)
    years_of_experience = models.PositiveIntegerField(default=0)
    hospital_affiliation = models.CharField(max_length=200, blank=True)
    is_available = models.BooleanField(default=True)
    shift_time = models.CharField(
        max_length=20,
        choices=(
            ('MORNING', 'Morning'),
            ('AFTERNOON', 'Afternoon'),
            ('NIGHT', 'Night'),
            ('ROTATING', 'Rotating'),
        ),
        default = 'ROTATING'
    )
    is_available = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Nurse Profile'
        verbose_name_plural = 'Nurse Profiles'

    
    def __str__(self):
        return f"Nurse {self.user.get_full_name()} - {self.get_specialization_display()}"


class AdminProfile(models.Model):
    #Profile for the adminisrator, i dedided to keep this simple (way too simple)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='admin_profile')
    department = models.CharField(max_length=100, blank=True)
    role_description = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Admin Profile'
        verbose_name_plural = 'Admin Profiles'


    def __str__(self):
        return f"Admin: {self.user.get_full_name()}"


class LabProfile(models.Model):
    #Profile for lab users

    LAB_DEPARTMENT_CHOICES = (
        ('HEMATOLOGY', 'Hematology'),
        ('MICROBIOLOGY', 'Microbiology'),
        ('PATHOLOGY', 'Pathology'),
        ('RADIOLOGY', 'Radiology & Imaging'),
        ('OTHER', 'Other'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='lab_profile')
    employee_id = models.CharField(max_length=50, unique=True, blank=True, default='')
    lab_department = models.CharField(max_length=50, choices=LAB_DEPARTMENT_CHOICES, blank=True, default='OTHER')     
    qualification = modelsCharField(max_length=100, blank=True, default='')
    years_of_experience = models.PositiveIntegerField(default=0)
    is_available = models.BooleanField(default='True')

    class Meta:
        verbose_name = 'LAb Profile'
        verbose_name_plural = 'LAb Profiles'

    def __str__(self):
        return f"Lab: {self.user.get_full_name()} - {self.get_lab_department_display()}"
        
    