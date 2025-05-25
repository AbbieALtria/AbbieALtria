from django.urls import path
from . import views

app_name = 'jobs'

urlpatterns = [
    path('', views.job_list, name='job_list'),
    path('job/<int:job_id>/apply/', views.submit_application, name='submit_application'),
    path('application/thank-you/', views.application_thank_you, name='application_thank_you'),
    path('dashboard/', views.recruiter_dashboard, name='recruiter_dashboard'),
    path('applicant/<int:applicant_id>/', views.applicant_detail, name='applicant_detail'),
]
