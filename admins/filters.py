import django_filters
from django_filters.filters import OrderingFilter
from .models import HospitalDoctors
from doctor.models import speciality_choice
from patient.models import Appointment
class DoctorFilter(django_filters.FilterSet):
    
    doctor_id__user__first_name = django_filters.CharFilter(label='Doctor Name', lookup_expr='icontains', label_suffix="")
    doctor_id__doctor_speciality = django_filters.ChoiceFilter(label='Type', choices=speciality_choice, empty_label='Any', label_suffix="")
    
    
    o = OrderingFilter(
        fields=(
            ('doctor_id__user__first_name', 'first name'),
        ),
        empty_label='Default',
        label_suffix="",
    )
    class Meta:
        model = HospitalDoctors
        fields = ['doctor_id__user__first_name', 'doctor_id__doctor_speciality']
    
    @property
    def qs(self):
        parent = super().qs
        return parent.filter(hospital_id__user=self.request.user.id, status='approved')


class DoctorApplicationsFilter(django_filters.FilterSet):
    
    doctor_id__user__first_name = django_filters.CharFilter(label='Doctor Name', lookup_expr='icontains', label_suffix="")
    doctor_id__doctor_speciality = django_filters.ChoiceFilter(label='Type', choices=speciality_choice, empty_label='Any', label_suffix="")
    
    
    o = OrderingFilter(
        fields=(
            ('doctor_id__user__first_name', 'first name'),
        ),
        empty_label='Default',
        label_suffix="",
    )
    class Meta:
        model = HospitalDoctors
        fields = ['doctor_id__user__first_name', 'doctor_id__doctor_speciality']
    
    def qs(self):
        parent = super().qs
        return parent.filter(hospital_id__user=self.request.user.id, status='applied')

class HospitalAppointmentFilter(django_filters.FilterSet):
    hospital__hospital_id__hospital_name = django_filters.CharFilter(label='Hospital Name', lookup_expr='icontains', label_suffix="")
    date = django_filters.DateFilter(label="Date", label_suffix="")
    hospital__hospital_id__hospital_address = django_filters.CharFilter(label='Location', lookup_expr='icontains', label_suffix="")
    o = OrderingFilter(
        fields=(
            ('hospital__doctor_id__user', 'Hospital name'),
        ),
        empty_label='Default',
        label_suffix="",
    )

    class Meta:
        model = Appointment
        fields = ['date', 'hospital__doctor_id__user']
    
    
    def qs(self):
        parent = super().qs
        return parent.filter(hospital__hospital_id__user = self.request.user, status = True)
