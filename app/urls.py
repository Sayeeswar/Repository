from django.urls import path
from . import views

urlpatterns = [
   
    path('visit-stats/', views.visit_stats, name='visit_stats'),
    path('hospital/', views.hospitalFilter, name='hospital_filter'),  # this is the filter view
    path('hospitalsb/<str:hospital_code>/', views.hospital_profile, name='hospital_profile'),
    path('hospital-report/', views.hospital_report, name='hospital_report'),
    path('hospitals/', views.hospital_overview, name='hospital'),
    path('department/', views.hospitaloverview, name='department_filter'),
    path('surgeries/', views.Surgeries, name='surgeries'),

  # updated here
]
