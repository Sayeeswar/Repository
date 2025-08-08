from django.urls import path
from . import views

urlpatterns = [
    path('books/', views.book_list, name='book_list'),
    path('books/table/', views.book_table, name='book_table'),
    path('books/search/', views.book_search, name='book_search'),
    path('books/filter/', views.filter_by_author, name='filter_by_author'),
    path('visit-stats/', views.visit_stats, name='visit_stats'),
    path('hospital/', views.hospitalFilter, name='hospital_filter'),  # this is the filter view
    path('hospitalsb/<str:hospital_code>/', views.hospital_profile, name='hospital_profile'),
    path('hospital-report/', views.hospital_report, name='hospital_report'),
    path('hospitals/', views.hospital_overview, name='hospital'),

  # updated here
]
