from django.contrib.auth.views import PasswordResetConfirmView
from django.http.response import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls.base import reverse_lazy
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode
from django.views.generic.base import TemplateView, View
from django.db.models import Sum, Count

# Custom imports
from .forms import DoctorLoginForm, DoctorRegisterForm, SetPasswordForm
from core.models import CustomUser
# from .mixins import Is_login
from core.views import RegisterView, LogoutView, LoginView, ChangeView, PasswordChangeView, PasswordResetView
from core.tokens import tokenizer
from admins.models import AdminAdditional, HospitalDoctors
from .models import DoctorAdditional
from .filters import HospitalFilter, ApplicationFilter, DoctorAppointmentFilter
from django_filters.views import FilterView
from patient.models import Appointment



# Create your views here.
class Home(View):
    def get(self, request, *args, **kwargs):
        appointments = Appointment.objects.filter(hospital__doctor_id__user=self.request.user, payment_status=True, status=True).order_by('-date')[:5]
        applications = HospitalDoctors.objects.filter(doctor_id__user=self.request.user)[:5]
        t_patient = Appointment.objects.filter(hospital__doctor_id__user=self.request.user, payment_status=True, status=True).distinct().count()
        t_revenue = Appointment.objects.filter(hospital__doctor_id__user=self.request.user, payment_status=True, status=True).aggregate(Sum('hospital__doctor_id__doctor_fees'))
        context = {'appointments': appointments, 'applications': applications,'t_patient': t_patient, 't_revenue': t_revenue['hospital__doctor_id__doctor_fees__sum']}
        return render(request, "doctor/home.html", context=context)

# Patient Registeration view
# TODO
class DoctorRegisterView(RegisterView):

    template_name = 'doctor/doctor_register.html'
    email_template_name = 'doctor/doctor_activation_email.html'
    subject_template_name = 'doctor/doctor_activation_subject.txt'
    form_class = DoctorRegisterForm
    success_url = reverse_lazy('doctor_signin')
    current_url = reverse_lazy('doctor_signup')
    user_type = 'is_doctor'

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
        return render(request, 'doctor/doctor_registeration_successful.html')
    else:
        return render(request, 'doctor/doctor_registeration_unsuccessful.html')


# Login View
class DoctorLoginView(LoginView):
    
    """
    Display the login form and handle the login action.
    """
    form_class = DoctorLoginForm
    template_name = 'doctor/doctor_login.html'
    success_url = reverse_lazy('doctor_home')


# Logout View
class DoctorLogoutView(LogoutView):
    login_url = reverse_lazy('doctor_signin')
    next_page = reverse_lazy('doctor_signin')

# Password Reset View via email
class DoctorPasswordResetView(PasswordResetView):

    template_name = 'doctor/doctor_password_reset.html'
    success_url = reverse_lazy('doctor_password_reset')
    email_template_name = 'doctor/password_reset_email.html'
    subject_template_name = 'doctor/password_reset_subject.txt'
    user_type = 'is_doctor'

# Password Reset Confirm View
class DoctorPasswordResetConfirmView(PasswordResetConfirmView):
    form_class = SetPasswordForm
    success_url = reverse_lazy('doctor_signin')
    template_name = 'doctor/doctor_password_reset_confirm.html'

# Viewing all hospitals and apply
class HospitalView(FilterView):
    # login_url = reverse_lazy('patient_login')
    model = AdminAdditional
    template_name = 'doctor/hospital_apply.html'
    filterset_class = HospitalFilter
    

# Confirm apply 
class DoctorAppliedView(View):
    def get(self, request, *args, **kwargs):
        try:
            existing_doctor = DoctorAdditional.objects.get(user_id=request.user.id)
            doctor = HospitalDoctors.objects.filter(doctor_id=existing_doctor.id)
            for d in doctor:
                if d.hospital_id.id == self.kwargs['pk']:
                    return render(request, 'doctor/doctor_applied.html')
        except:
            pass
        hospital_id = AdminAdditional.objects.get(id=self.kwargs['pk'])
        doctor = HospitalDoctors.objects.create(doctor_id=existing_doctor, hospital_id=hospital_id, status='applied')
        doctor.save() 
        return render(request, 'doctor/hospital_apply_successful.html')


class DoctorApplicationView(FilterView):
    model = HospitalDoctors
    template_name = 'doctor/doctor_application.html'
    filterset_class = ApplicationFilter

# TO view all the appointment
class DoctorAppointmentBookedView(FilterView):
    # login_url = reverse_lazy('patient_login')
    model = Appointment
    template_name = 'doctor/doctor_appointment_booked.html'
    filterset_class = DoctorAppointmentFilter

def DoctorAppointmentDelete(request, pk):
    appointment = Appointment.objects.get(id=pk)
    if appointment.status:
        appointment.status=False
        appointment.save()
        return HttpResponseRedirect(reverse_lazy('doctor_appointments'))

'''    
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
    success_url = reverse_lazy('patient_login')
    template_name = 'patient/password_reset_confirm.html'

# Admin additional info updating
class AdminAdditionalChangeView(UpdateView):
    
    login_url = reverse_lazy('patient_login')
    form_class = AdminAdditionalForm
    template_name = 'admins/profile_additional.html'
    success_url = reverse_lazy('admin_profile_additional')

    def get_object(self):
        return self.request.user.adminadditional
'''