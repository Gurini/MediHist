from django.urls import path
from . import views

app_name = 'records'

urlpatterns = [
    # Patient URLs
    path('patients/', views.patient_list, name='patient_list'),
    path('patients/create/', views.patient_create, name='patient_create'),
    path('patients/<str:patient_id>/', views.patient_detail, name='patient_detail'),
    
    # Medical History URLs
    path('patients/<str:patient_id>/medical-history/create/', views.medical_history_create, name='medical_history_create'),
    
    # Diagnosis URLs
    path('patients/<str:patient_id>/diagnosis/create/', views.diagnosis_create, name='diagnosis_create'),
    
    # Prescription URLs
    path('patients/<str:patient_id>/prescription/create/', views.prescription_create, name='prescription_create'),
    
    # Search
    path('search/', views.search_patients, name='search_patients'),
]