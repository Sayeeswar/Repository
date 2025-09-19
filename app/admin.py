

# Register your models here.
from django.contrib import admin
from .models import HospitalMaster,HospitalVisit

admin.site.register(HospitalMaster)
admin.site.register(HospitalVisit)
