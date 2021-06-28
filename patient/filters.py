import django_filters
from admins.models import HospitalDoctors
from doctor.models import speciality_choice
from .models import Appointment
# from django_filters.filters import OrderingFilter

class DoctorFilter(django_filters.FilterSet):
    hospital_id__hospital_name = django_filters.CharFilter(label='Hospital Name', lookup_expr='icontains', label_suffix="")
    hospital_id__hospital_address = django_filters.CharFilter(label='Location', lookup_expr='icontains', label_suffix="")
    doctor_id__user__first_name = django_filters.CharFilter(label='Doctor Name', lookup_expr='icontains', label_suffix="")
    doctor_id__doctor_speciality = django_filters.ChoiceFilter(label='Type', choices=speciality_choice, label_suffix='', empty_label='All')
    class Meta:
        model = HospitalDoctors
        fields = ['hospital_id__hospital_name', 'hospital_id__hospital_address', 'doctor_id__doctor_speciality', 'doctor_id__user__first_name']
    
    
    def qs(self):
        parent = super().qs
        return parent.filter(status='approved')

class AppointmentFilter(django_filters.FilterSet):
    hospital__doctor_id__user__first_name = django_filters.CharFilter(label='Doctor Name', lookup_expr='icontains', label_suffix="")
    hospital__hospital_id__hospital_name = django_filters.CharFilter(label='Hospital Name', lookup_expr='icontains', label_suffix="")
    
    date = django_filters.DateFilter(label="Date", label_suffix="")
    hospital__doctor_id__doctor_speciality = django_filters.ChoiceFilter(label='Type', choices=speciality_choice, label_suffix='', empty_label='All')
    class Meta:
        model = Appointment
        fields = ['date', 'hospital__doctor_id__user__first_name', 'hospital__doctor_id__doctor_speciality', 'hospital__hospital_id__hospital_name']
    
    
    def qs(self):
        parent = super().qs
        return parent.filter(patient__user=self.request.user)
