import django_filters
from django_filters.filters import OrderingFilter
from admins.models import AdminAdditional, HospitalDoctors, status_choice
from patient.models import Appointment

class HospitalFilter(django_filters.FilterSet):
    
    hospital_name = django_filters.CharFilter(label='Hospital Name', lookup_expr='icontains', label_suffix="")
    hospital_address = django_filters.CharFilter(label='Location', lookup_expr='icontains', label_suffix="")
    
    
    o = OrderingFilter(
        fields=(
            ('hospital_name', 'Hospital name'),
        ),
        empty_label='Default',
        label_suffix="",
    )
    class Meta:
        model = AdminAdditional
        fields = ['hospital_name', 'hospital_address']
    
    
    def qs(self):
        parent = super().qs
        return parent.filter(is_recruiting=True).exclude(id__in=HospitalDoctors.objects.values_list('hospital_id', flat=True).filter(doctor_id__user=self.request.user.id))


class ApplicationFilter(django_filters.FilterSet):

    hospital_id__hospital_name = django_filters.CharFilter(label='Hospital Name', lookup_expr='icontains', label_suffix="")
    hospital_id__hospital_address = django_filters.CharFilter(label='Location', lookup_expr='icontains', label_suffix="")
    status = django_filters.ChoiceFilter(label='Status', choices=status_choice, label_suffix='', empty_label='All')
    class Meta:
        model = HospitalDoctors
        fields = ['hospital_id__hospital_name', 'hospital_id__hospital_address', 'status']
    
    
    def qs(self):
        parent = super().qs
        return parent.filter(doctor_id__user=self.request.user.id)

class DoctorAppointmentFilter(django_filters.FilterSet):
    hospital__hospital_id__hospital_name = django_filters.CharFilter(label='Hospital Name', lookup_expr='icontains', label_suffix="")
    date = django_filters.DateFilter(label="Date", label_suffix="")
    hospital__hospital_id__hospital_address = django_filters.CharFilter(label='Location', lookup_expr='icontains', label_suffix="")
    o = OrderingFilter(
        fields=(
            ('hospital__hospital_id__hospital_name', 'Hospital name'),
        ),
        empty_label='Default',
        label_suffix="",
    )

    class Meta:
        model = Appointment
        fields = ['date', 'hospital__hospital_id__hospital_name', 'hospital__hospital_id__hospital_address']
    
    
    def qs(self):
        parent = super().qs
        return parent.filter(hospital__doctor_id__user=self.request.user)