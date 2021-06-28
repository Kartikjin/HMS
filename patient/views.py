from django.contrib import messages
from django.contrib.auth.views import PasswordResetConfirmView
from django.http.response import HttpResponse, HttpResponseRedirect
from django.urls.base import reverse_lazy
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode
from django.views.generic.base import TemplateView, View
from django.views.generic.edit import CreateView
from django.views.generic.list import ListView
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.contrib.sites.shortcuts import get_current_site
from HMS import settings
from django_filters.views import FilterView
from django.db.models import Sum, Count

# Custom imports
from .forms import AppointmentBookingForm, PatientLoginForm, PatientRegisterForm, SetPasswordForm
from core.models import CustomUser
from core.views import RegisterView, LoginView, LogoutView, PasswordResetView
# , ChangeView, PasswordChangeView
from core.tokens import tokenizer
from admins.models import HospitalDoctors
from .models import Appointment, PatientAdditional
from .filters import DoctorFilter, AppointmentFilter
# from .mixins import Is_login



# Create your views here.
class Home(View):
    def get(self, request, *args, **kwargs):
        appointments = Appointment.objects.filter(patient__user=self.request.user, payment_status=True, status=True).order_by('-date')[:5]
        t_patient = Appointment.objects.filter(patient__user=self.request.user, payment_status=True, status=True).distinct().count()
        t_revenue = Appointment.objects.filter(patient__user=self.request.user, payment_status=True, status=True).aggregate(Sum('hospital__doctor_id__doctor_fees'))
        context = {'appointments': appointments,'t_patient': t_patient, 't_revenue': t_revenue['hospital__doctor_id__doctor_fees__sum']}
        return render(request, "patient/home.html", context=context)


# Patient Registeration view
# TODO
class PatientRegisterView(RegisterView):

    template_name = 'patient/patient_register.html'
    email_template_name = 'patient/patient_activation_email.html'
    subject_template_name = 'patient/patient_activation_subject.txt'
    form_class = PatientRegisterForm
    success_url = reverse_lazy('patient_signin')
    current_url = reverse_lazy('patient_signup')
    user_type = 'is_patient'


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
        return render(request, 'patient/patient_registeration_successful.html')
    else:
        return render(request, 'patient/patient_registeration_unsuccessful.html')


# Login View
class PatientLoginView(LoginView):
    
    """
    Display the login form and handle the login action.
    """
    form_class = PatientLoginForm
    template_name = 'patient/patient_login.html'
    success_url = reverse_lazy('patient_home')


# Logout View
class PatientLogoutView(LogoutView):
    login_url = reverse_lazy('patient_signin')
    next_page = reverse_lazy('patient_signin')
  
# Password Reset View via email
class PatientPasswordResetView(PasswordResetView):

    template_name = 'patient/patient_password_reset.html'
    success_url = reverse_lazy('patient_password_reset')
    email_template_name = 'patient/password_reset_email.html'
    subject_template_name = 'patient/password_reset_subject.txt'
    user_type = 'is_patient'

# Password Reset Confirm View
class PatientPasswordResetConfirmView(PasswordResetConfirmView):
    form_class = SetPasswordForm
    success_url = reverse_lazy('patient_signin')
    template_name = 'patient/patient_password_reset_confirm.html'

# Appointment

# Appointment List View
class DoctorView(FilterView):
    # login_url = reverse_lazy('patient_login')
    model = HospitalDoctors
    template_name = 'patient/appointment.html'
    filterset_class = DoctorFilter


# Razorpay Integeration
import razorpay
client = razorpay.Client(auth=(settings.razorpay_id, settings.razorpay_account_id))

class AppointmentBookView(CreateView):

    form_class = AppointmentBookingForm
    template_name = 'patient/appointment_book.html'
    success_url = reverse_lazy('patient_appointment_book')

    def form_valid(self, form):
        date = form.cleaned_data['date']
        try:
            appointment = Appointment.objects.get(patient__user=self.request.user, date=date, hospital_id=self.kwargs['pk'])
            if appointment.payment_status:  
                messages.error(self.request, "Your already have an appoint for the same day.")
                return render(self.request, self.template_name, {'form':form})
            elif not appointment.payment_status:
                appointment.delete()
        except:
            pass

        hospital = HospitalDoctors.objects.get(id=self.kwargs['pk'])
        patient = PatientAdditional.objects.get(user=self.request.user)
        opts = {
                'hospital': hospital,
                'patient': patient
            }
        appointment = form.save(**opts)
        
        # payment
        callbackurl = 'http://'+ str(get_current_site(self.request))+"/patient/appointment/done"
        payment_currency = 'INR'
        notes = {'payment':'appointment booked'}
        razor_pay = client.order.create(dict(amount=appointment.hospital.doctor_id.doctor_fees*100, currency=payment_currency, notes=notes, receipt=str(appointment.id)))
        appointment.razorpay_order_id = razor_pay['id']
        appointment.save()
        # messages.success(self.request, "link has been sent to your email id. please check your inbox and if its not there check your spam as well.")
        return render(self.request, 'patient/payment/payment.html', {'appointment':appointment, 'order_id': razor_pay['id'], 'razorpay_merchant_id':settings.razorpay_id, 'callbackurl':callbackurl})

# Appointment Booked View
@csrf_exempt
def AppointmentDone(request):
    if request.method == "POST":
        try:
            payment_id = request.POST.get('razorpay_payment_id')
            order_id = request.POST.get('razorpay_order_id')
            signature = request.POST.get('razorpay_signature')
            params_dict = { 
            'razorpay_order_id': order_id, 
            'razorpay_payment_id': payment_id,
            'razorpay_signature': signature
            }
            try:
                appointment = Appointment.objects.get(razorpay_order_id=order_id)
            except:
                return HttpResponse("505 Not Found")

            result = client.utility.verify_payment_signature(params_dict)
            if not result:
                appointment.razorpay_payment_id = payment_id
                appointment.razorpay_signature = signature
                appointment.save()
                try:
                    client.payment.capture(payment_id, appointment.hospital.doctor_id.doctor_fees*100)
                    appointment.payment_status = True
                    appointment.save()
                    return render(request, 'patient/payment/payment_successfull.html')
                except:
                    return HttpResponse("505 Not Found")
            else:
                return render(request, 'patient/payment/payment_failed.html')
        except:
            return HttpResponse("505 Not Found")
    else:
        return redirect(reverse_lazy('patient_appointment_book'))

# TO view all the appointment
class PatientAppointmentBookedView(FilterView):
    # login_url = reverse_lazy('patient_login')
    model = Appointment
    template_name = 'patient/patient_appointment_booked.html'
    filterset_class = AppointmentFilter

        
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

# Admin additional info updating
class AdminAdditionalChangeView(UpdateView):
    
    login_url = reverse_lazy('patient_login')
    form_class = AdminAdditionalForm
    template_name = 'admins/profile_additional.html'
    success_url = reverse_lazy('admin_profile_additional')

    def get_object(self):
        return self.request.user.adminadditional


# Admin additional info updating
class DoctorView(ListView):
    
    # login_url = reverse_lazy('patient_login')
    # form_class = DoctorUpdateForm
    model = HospitalDoctors
    template_name = 'admins/doctor.html'
    success_url = reverse_lazy('doctor_update')
    
    def get_queryset(self):
        queryset = HospitalDoctors.objects.filter(hospital_id__user_id=self.request.user.id) 
        return queryset
    
class DoctorUpdateView(UpdateView):
    form_class = DoctorUpdateForm
    template_name = 'admins/doctor_update.html'
    success_url = reverse_lazy('doctors')
    
    def get_object(self):
        queryset = HospitalDoctors.objects.get(pk=self.kwargs['pk'])       
        return queryset 
    # TODO doctors arent handled proper while updating
'''