from doctor.models import DoctorAdditional
from django import forms
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.sites.shortcuts import get_current_site
from django.db import transaction
from core.forms import RegisterForm, LoginForm
from .models import AdminAdditional, HospitalDoctors

from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

# Define your own forms here

# Register Form For Admin
class AdminRegisterForm(RegisterForm):
    hospital_name = forms.CharField(max_length=100)
    hospital_address = forms.CharField(max_length=100)
    is_recruiting = forms.BooleanField(required=False)

            
    @transaction.atomic
    def save(self, domain_override=None,
             subject_template_name=None,
             email_template_name=None,
             use_https=False, token_generator=None,
             from_email=None, request=None, html_email_template_name=None,
             extra_email_context=None):
        
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
        user.is_admin = True
        user.save()
        adminadditional = AdminAdditional.objects.create(user=user)
        adminadditional.hospital_name = self.cleaned_data.get('hospital_name')
        adminadditional.hospital_address = self.cleaned_data.get('hospital_address')
        adminadditional.is_recruiting = self.cleaned_data.get('is_recruiting')
        adminadditional.save()
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
class AdminLoginForm(LoginForm):
    def confirm_login_allowed(self, user):
        
        if not user.is_active:
            raise forms.ValidationError(
                self.error_messages['inactive'],
                code='inactive',
            )
        # This function will stop the users from login who are not a patient
        if not user.is_admin:
            raise forms.ValidationError(
                self.error_messages['unauthorized'],
                code='unauthorized',
            )
            
class SetPasswordForm(SetPasswordForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for fieldname in ['new_password1', 'new_password2']:
            self.fields[fieldname].help_text = None

# TODO
class AdminAdditionalForm(forms.ModelForm):
    class Meta:
        model = AdminAdditional
        fields = ('hospital_name', 'hospital_address', 'is_recruiting')


status_choice = (
    ('applied','Applied'),
    ('rejected','Rejected'),
    ('approved','Approved'),
)

class DoctorUpdateForm(forms.ModelForm):
    status = forms.ChoiceField(choices=status_choice)
    def __init__(self, *args, **kwargs):
       super(DoctorUpdateForm, self).__init__(*args, **kwargs)
       self.fields['doctor_id'].disabled = True
       self.fields['doctor_id'].label = 'Doctor Name'
       
    class Meta:
        model = HospitalDoctors
        fields = ['doctor_id', 'status']
        # read_only = ('hospital_id')