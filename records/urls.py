from django.urls import path
from . import views
from . import lab_views

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
    
    #LAb teest URLs
    path('lab-tests/', lab_views.lab_test_list, name='lab_test_list'),
    path('patients/<str:patient_id>/lab-test/create/', lab_views.lab_test_create, name='lab_test_create'),
    path('lab-tests/<int:test_id>/', lab_views.lab_test_detail, name='lab_test_detail'),
    path('lab-tests/<int:test_id>/pickup/', lab_views.lab_test_pickup, name='lab_test_pickup'),

    #Lab results URLs
    path('lab-tests/<int:test_id>/results/create', lab_views.lab_result_create, name='lab_result_create'),
    path('lab-tests/<int:test_id>/results/add-file', lab_views.lab_result_add_file, name='lab_result_add_file'),
    path('lab-tests/<int:test_id>/results/interpret', lab_views.lab_result_interpret, name='lab_result_interpret'),
    
    
    # Search
    path('search/', views.search_patients, name='search_patients'),
]