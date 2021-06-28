from django import forms
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.sites.shortcuts import get_current_site
from django.db import transaction
from django.forms import fields, widgets
from core.forms import RegisterForm, LoginForm
from .models import Appointment, PatientAdditional

from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

# Define your own forms here

# Register Form For Admin
class PatientRegisterForm(RegisterForm):
    
    medical_history = forms.CharField(max_length=100)
    
    @transaction.atomic
    def save(self, domain_override=None,
             subject_template_name=None,
             email_template_name=None,
             use_https=False, token_generator=None,
             from_email=None, request=None, html_email_template_name=None,
             extra_email_context=None, user_type=None):
        
        """
        Generate a one-use only link for resetting password and send it to the
        user.
        """

        if not domain_override:
            current_site = get_current_site(request)
            site_name = current_site.name
            domain = current_site.domain
        else:
            site_name = domain = domain_override
        
        
        email = self.cleaned_data['email']
        user = super().save(commit=False)
        user.is_patient = True
        user.save()
        patientadditional = PatientAdditional.objects.create(user=user)
        patientadditional.medical_history = self.cleaned_data.get('medical_history')
        patientadditional.save()
        # student.interests.add(*self.cleaned_data.get('interests'))
        context = {
            'email': email,
            'domain': domain,
            'site_name': site_name,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'user': user,
            'token': token_generator.make_token(user),
            'protocol': 'https' if use_https else 'http',
            **(extra_email_context or {}),
        }
        self.send_mail(
            subject_template_name, email_template_name, context, from_email,
            email, html_email_template_name=html_email_template_name,
        )    
        return user

# Login Form
class PatientLoginForm(LoginForm):
    def confirm_login_allowed(self, user):
        
        if not user.is_active:
            raise forms.ValidationError(
                self.error_messages['inactive'],
                code='inactive',
            )
        # This function will stop the users from login who are not a patient
        if not user.is_patient:
            raise forms.ValidationError(
                self.error_messages['unauthorized'],
                code='unauthorized',
            )
class SetPasswordForm(SetPasswordForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for fieldname in ['new_password1', 'new_password2']:
            self.fields[fieldname].help_text = None

class AppointmentBookingForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ('problem', 'date')

    # @transaction.atomic
    def save(self, hospital, patient):
        problem = self.cleaned_data['problem']
        date = self.cleaned_data['date']
        return Appointment.objects.create(patient=patient, hospital=hospital, problem=problem, date=date)

'''
# TODO
class AdminAdditionalForm(forms.ModelForm):
    class Meta:
        model = AdminAdditional
        fields = ('hospital_name', 'hospital_address', 'is_recruiting')

class DoctorUpdateForm(forms.ModelForm):
    class Meta:
        model = HospitalDoctors
        fields = ('status',)

'''