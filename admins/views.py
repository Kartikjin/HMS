from .models import AdminAdditional, HospitalDoctors
from django.contrib.auth.views import PasswordResetConfirmView
from django.http.response import HttpResponse, HttpResponseRedirect
from django.urls.base import reverse_lazy
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode
from django.views.generic.base import TemplateView
from django.views.generic.edit import UpdateView
from django.views.generic.list import ListView
from django.shortcuts import render
from django.views.generic.base import View
from django.db.models import Sum, Count
from django.core.mail import send_mail

# Custom imports
from HMS import settings
from .forms import AdminAdditionalForm, AdminLoginForm, AdminRegisterForm, DoctorUpdateForm, SetPasswordForm
from core.models import CustomUser
# from .mixins import Is_login
from core.views import RegisterView, LogoutView, LoginView, ChangeView, PasswordChangeView, PasswordResetView
from core.tokens import tokenizer
from patient.models import Appointment
from .models import HospitalDoctors
from .filters import DoctorFilter, DoctorApplicationsFilter, HospitalAppointmentFilter
from django_filters.views import FilterView

# Create your views here.
class Home(View):
    def get(self, request, *args, **kwargs):
        appointments = Appointment.objects.filter(hospital__hospital_id__user=self.request.user, payment_status=True, status=True).order_by('-date')[:5]
        applications = HospitalDoctors.objects.filter(hospital_id__user=self.request.user)[:5]
        t_doctor = HospitalDoctors.objects.filter(hospital_id__user=self.request.user, status='approved').count()
        t_patient = Appointment.objects.filter(hospital__hospital_id__user=self.request.user, payment_status=True, status=True).distinct().count()
        t_revenue = Appointment.objects.filter(hospital__hospital_id__user=self.request.user, payment_status=True, status=True).aggregate(Sum('hospital__doctor_id__doctor_fees'))
        g_doctor = Appointment.objects.values('hospital__doctor_id__user__first_name').annotate(t_count=Count('hospital__doctor_id')).filter(hospital__hospital_id__user=self.request.user, payment_status=True, status=True)
        context = {'appointments': appointments, 'applications': applications, 't_doctor': t_doctor, 't_patient': t_patient, 't_revenue': t_revenue['hospital__doctor_id__doctor_fees__sum'], 'g_doctor': g_doctor}
        return render(request, "admins/home.html", context=context)

# Admin Registeration view
# TODO
class AdminRegisterView(RegisterView):

    template_name = 'admins/admin_register.html'
    email_template_name = 'admins/admin_activation_email.html'
    subject_template_name = 'admins/admin_activation_subject.txt'
    form_class = AdminRegisterForm
    success_url = reverse_lazy('admin_signin')
    current_url = reverse_lazy('admin_signup')
    user_type = 'is_admin'


# Activate Email of Admin
# TODO
def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = CustomUser.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, CustomUser.DoesNotExist) as e:
        user = None
    if user is not None and tokenizer.check_token(user, token):
        user.is_active = True
        user.save()
        return render(request, 'admins/admin_registeration_successful.html')
    else:
        return render(request, 'admins/admin_registeration_unsuccessful.html')


# Login View
class AdminLoginView(LoginView):
    
    """
    Display the login form and handle the login action.
    """
    form_class = AdminLoginForm
    template_name = 'admins/admin_login.html'
    success_url = reverse_lazy('admin_home')


# Logout View
class AdminLogoutView(LogoutView):
    login_url = reverse_lazy('admin_signin')
    next_page = reverse_lazy('admin_signin')
    
# Change View For common fields
class AdminChangeView(ChangeView):
    
    login_url = reverse_lazy('admin_signin')
    template_name = 'admins/admin_change.html'
    success_url = reverse_lazy('admin_change')

# Password Change using old password view
class AdminPasswordChangeView(PasswordChangeView):
    
    success_url = reverse_lazy('admin_password_change')
    template_name = 'admins/admin_pass_change.html'
    login_url = reverse_lazy('admin_signin')

# Password Reset View via email
class AdminPasswordResetView(PasswordResetView):

    template_name = 'admins/admin_password_reset.html'
    success_url = reverse_lazy('admin_password_reset')
    email_template_name = 'admins/password_reset_email.html'
    subject_template_name = 'admins/password_reset_subject.txt'
    user_type = 'is_admin'

# Password Reset Confirm View
class AdminPasswordResetConfirmView(PasswordResetConfirmView):
    form_class = SetPasswordForm
    success_url = reverse_lazy('admin_signin')
    template_name = 'admins/admin_password_reset_confirm.html'

# Admin additional info updating
class AdminAdditionalChangeView(UpdateView):
    
    login_url = reverse_lazy('patient_login')
    form_class = AdminAdditionalForm
    template_name = 'admins/profile_additional.html'
    success_url = reverse_lazy('admin_profile_additional')

    def get_object(self):
        return self.request.user.adminadditional


# Doctor List View
class DoctorView(FilterView):
    # login_url = reverse_lazy('patient_login')
    model = HospitalDoctors
    template_name = 'admins/admin_all_doctors.html'
    filterset_class = DoctorFilter



# Doctor Application View
class DoctorApplicationView(FilterView):
    # login_url = reverse_lazy('patient_login')
    model = HospitalDoctors
    template_name = 'admins/admin_applied_doctors.html'
    filterset_class = DoctorApplicationsFilter


# Doctor UpdateView
class DoctorUpdateView(UpdateView):
    form_class = DoctorUpdateForm
    template_name = 'admins/doctor_update.html'
    success_url = reverse_lazy('all_doctors')
    
    def get_object(self):
        queryset = HospitalDoctors.objects.get(pk=self.kwargs['pk'], hospital_id__user=self.request.user.id)       
        return queryset 

# Delete a Doctor
def delete_doctor(request, pk):
    doctor = HospitalDoctors.objects.get(id=pk)
    doctor.status = 'laidoff'
    doctor.save()
    return HttpResponseRedirect(reverse_lazy('all_doctors'))    

# TO view all the appointment
class HospitalAppointmentBookedView(FilterView):
    # login_url = reverse_lazy('patient_login')
    model = Appointment
    template_name = 'admins/admin_appointment_booked.html'
    filterset_class = HospitalAppointmentFilter

# To delete an appointment
def delete_appointment(request, pk):
    appointment = Appointment.objects.get(id=pk)
    appointment.status = False
    appointment.save()
    # send_mail('Apppointment Cancelled', 'There is an update in your apppointment. For more info you can Login to our website.', settings.EMAIL_HOST_USER, [appointment.patient.user.email])
    return HttpResponseRedirect(reverse_lazy('patient_appointment'))
