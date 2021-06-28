from django.contrib.auth import authenticate
from django.contrib.sites.shortcuts import get_current_site
from django.db import transaction
from .models import CustomUser
from django import forms
from django.contrib.auth.forms import UserChangeForm, UserCreationForm, _unicode_ci_compare
from django.template import loader
from django.core.mail import EmailMultiAlternatives
from django.utils.translation import gettext, gettext_lazy as _
from django.utils.text import capfirst
from django.contrib.auth.hashers import (
    UNUSABLE_PASSWORD_PREFIX, identify_hasher,
)

from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode


class ContactForm(forms.Form):
    email = forms.EmailField(required=True)
    subject = forms.CharField(required=True)
    message = forms.CharField(widget=forms.Textarea, required=True)

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm):
        model = CustomUser
        fields = ('email',)


class CustomUserChangeForm(UserChangeForm):

    class Meta:
        model = CustomUser
        fields = ('email',)







'''  Generalized forms are here  '''

class RegisterForm(UserCreationForm):
    
    """User registration form."""
   
    first_name = forms.CharField(
        max_length=100,
        required=False
        )

    last_name = forms.CharField(
        max_length=100,
        required=False
        )

    email = forms.EmailField(
        max_length=254,
        required=True,
        )

    password1 = forms.CharField(
        label='Password',
        max_length=100,
        required=True,
        widget=forms.PasswordInput(
        attrs={
            'type': 'password',
            'autocomplete': 'new-password'
        }))

    password2 = forms.CharField(
        label='Confirm password',
        max_length=100,
        required=True,
        widget=forms.PasswordInput(
        attrs={
            'type': 'password',
            'autocomplete': 'new-password'
        }))

    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'email', 'password1', 'password2', )

    def send_mail(self, subject_template_name, email_template_name,
                  context, from_email, to_email, html_email_template_name=None):
        
        """
        Send a django.core.mail.EmailMultiAlternatives to `to_email`.
        """
        subject = loader.render_to_string(subject_template_name, context)
        # Email subject *must not* contain newlines
        subject = ''.join(subject.splitlines())
        body = loader.render_to_string(email_template_name, context)
        email_message = EmailMultiAlternatives(subject, body, from_email, [to_email])
        if html_email_template_name is not None:
            html_email = loader.render_to_string(html_email_template_name, context)
            email_message.attach_alternative(html_email, 'text/html')

        email_message.send()


# Login Form
class LoginForm(forms.Form):    
    
    email = forms.EmailField(widget=forms.TextInput(attrs={'autofocus': True}))
    password = forms.CharField(
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'current-password'}),
    )

    error_messages = {
        'invalid_login': _(
            "Please enter a correct %(email)s and password. Note that both "
            "fields may be case-sensitive."
        ),
        'inactive': _("This account is inactive."),
        'unauthorized': _("This account is not authorized to login on this page."),
    }

    def __init__(self, request=None, *args, **kwargs):
        
        """
        The 'request' parameter is set for custom auth use by subclasses.
        The form data comes in via the standard 'data' kwarg.
        """
        self.request = request
        self.user_cache = None
        super().__init__(*args, **kwargs)


        # Set the max length and label for the "email" field.
        self.email_field = CustomUser._meta.get_field(CustomUser.USERNAME_FIELD)
        email_max_length = self.email_field.max_length or 254
        self.fields['email'].max_length = email_max_length
        self.fields['email'].widget.attrs['maxlength'] = email_max_length
        if self.fields['email'].label is None:
            self.fields['email'].label = capfirst(self.email_field.verbose_name)

    def clean(self):
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')

        if email is not None and password:
            self.user_cache = authenticate(self.request, email=email, password=password)
            if self.user_cache is None:
                raise self.get_invalid_login_error()
            else:
                self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data
        
    def get_user(self):
        return self.user_cache

    def get_invalid_login_error(self):
        return forms.ValidationError(
            self.error_messages['invalid_login'],
            code='invalid_login',
            params={'email': self.email_field.verbose_name},
        )


# Change Form to change common fields
class ReadOnlyPasswordHashWidget(forms.Widget):
    template_name = 'patient/read_only_password_hash.html'
    read_only = True

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        summary = []
        if not value or value.startswith(UNUSABLE_PASSWORD_PREFIX):
            summary.append({'label': gettext("No password set.")})
        else:
            try:
                hasher = identify_hasher(value)
            except ValueError:
                summary.append({'label': gettext("Invalid password format or unknown hashing algorithm.")})
            else:
                # for key, value_ in hasher.safe_summary(value).items():
                #     summary.append({'label': gettext(key), 'value': value_})
                summary.append({'label': 'Hidden'})
        context['summary'] = summary
        return context

class ReadOnlyPasswordHashField(forms.Field):
    widget = ReadOnlyPasswordHashWidget

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("required", False)
        kwargs.setdefault('disabled', True)
        super().__init__(*args, **kwargs)
        
class ChangeForm(forms.ModelForm):

    first_name = forms.CharField(
        max_length=100,
        required=True,
        )

    last_name = forms.CharField(
        max_length=100,
        required=True,
        )

    email = forms.EmailField(
        max_length=254,
        widget = forms.EmailInput(attrs=
            {
                'readonly': True
            }
        ))

    password = ReadOnlyPasswordHashField(
        label=_("Password"),
        help_text=_(
            'Raw passwords are not stored, so there is no way to see this '
            'user’s password, but you can change the password using '
            '<a href="{}">this form</a>.'
        ),
    )

    class Meta:
        model = CustomUser
        fields = ('email','first_name', 'last_name' ,'password')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        password = self.fields.get('password')
        if password:
            password.help_text = password.help_text.format('../password_change/')


# Password Reset Form
class PasswordResetForm(forms.Form):
    email = forms.EmailField(
        label=_("Email"),
        max_length=254,
        widget=forms.EmailInput(attrs={'autocomplete': 'email'})
    )
    error_messages = {
        'invalid_email': _(
            "Please enter a correct email. Note that field may be case-sensitive."
        )}

    def send_mail(self, subject_template_name, email_template_name,
                  context, from_email, to_email, html_email_template_name=None):
        """
        Send a django.core.mail.EmailMultiAlternatives to `to_email`.
        """
        subject = loader.render_to_string(subject_template_name, context)
        # Email subject *must not* contain newlines
        subject = ''.join(subject.splitlines())
        body = loader.render_to_string(email_template_name, context)

        email_message = EmailMultiAlternatives(subject, body, from_email, [to_email])
        if html_email_template_name is not None:
            html_email = loader.render_to_string(html_email_template_name, context)
            email_message.attach_alternative(html_email, 'text/html')

        email_message.send()

    def get_users(self, email, user_type):
 
        """Given an email, return matching user(s) who should receive a reset.

        This allows subclasses to more easily customize the default policies
        that prevent inactive users and users with unusable passwords from
        resetting their password.
        """

        email_field_name = CustomUser.get_email_field_name()
        active_users = CustomUser._default_manager.filter(**{
            '%s__iexact' % email_field_name: email,
            'is_active': True,
        })

        for u in active_users:
            if u.has_usable_password() and _unicode_ci_compare(email, getattr(u, email_field_name)) and getattr(u, user_type):
                return active_users
            else:
                return False

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
        
        email = self.cleaned_data["email"]
        if not domain_override:
            current_site = get_current_site(request)
            site_name = current_site.name
            domain = current_site.domain
        else:
            site_name = domain = domain_override
        
        email_field_name = CustomUser.get_email_field_name()
        users = self.get_users(email, user_type)
        if not users:
            return False
        else:
            for user in users:
                user_email = getattr(user, email_field_name)
                context = {
                    'email': user_email,
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
                    user_email, html_email_template_name=html_email_template_name,
                )    
            return True



