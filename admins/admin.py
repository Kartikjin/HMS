from django.contrib import admin

from .models import AdminAdditional, HospitalDoctors
# Register your models here.
admin.site.register(AdminAdditional)

admin.site.register(HospitalDoctors)
