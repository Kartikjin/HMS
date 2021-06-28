from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView, PasswordResetView
from django.http.response import HttpResponseRedirect
from django.utils.decorators import method_decorator

from django.views.decorators.debug import sensitive_post_parameters
from django.views.generic import TemplateView
from django.views import View
from django.views.generic.edit import CreateView, UpdateView
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect

from .forms import ChangeForm, ContactForm, PasswordResetForm

from django.shortcuts import render

from django.core.mail import EmailMessage

from django.conf import settings

from django.contrib import messages

from .tokens import tokenizer
from .models import CustomUser

# Create your views here.
class Home(TemplateView):
    template_name = 'core/index.html'

class Aboutus(TemplateView):
    template_name = 'core/about.html'

class Contactus(View):
    form_class = ContactForm
    template_name = 'core/contact.html'

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, self.template_name, {'email_form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            
            email = form.cleaned_data['email']
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']
            try:
                message = 'Subject: ' + subject + '<br>Message: ' + message
                mail = EmailMessage(email, message, settings.EMAIL_HOST_USER, [settings.EMAIL_HOST_USER])
                mail.content_subtype = 'html'
                mail.send()
                form = ContactForm()
                messages.success(request, 'Sent email to %s'%settings.EMAIL_HOST_USER)
                return render(request, self.template_name, {'email_form': form})
            except:
                messages.error(request, 'There is some error in sending email try after sometime.')
                return render(request, self.template_name, {'email_form': form})
        messages.error(request, 'Unable to send email. Please try again later')
        return render(request, self.template_name, {'email_form': form})



''' Generalized views for all types of users '''

# Register View
class RegisterView(CreateView):

    template_name = None
    form_class = None
    success_url = None
    current_url = None
    token_generator = tokenizer
    email_template_name = None
    subject_template_name = None
    user_type = None
    
    @method_decorator(sensitive_post_parameters())
    @method_decorator(csrf_protect)
    @method_decorator(never_cache)
    def dispatch(self, *args, **kwargs):    
        return super().dispatch(*args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        user_email = request.POST.get('email')
        try:
            existing_user = CustomUser.objects.get(email = user_email)
            if(existing_user.is_active == False):
                existing_user.delete()
            else:
                if not getattr(existing_user, self.user_type):
                    setattr(existing_user, self.user_type, True)
                    existing_user.save()
                    messages.success(request, 'Updated Succesfully')
                    return HttpResponseRedirect(self.success_url)
                else:
                    messages.error(request, 'Your Are already registered')
                    return HttpResponseRedirect(self.current_url)
        except:
            pass
        if form.is_valid():
            opts = {
                'use_https': self.request.is_secure(),
                'token_generator': self.token_generator,
                'from_email': None,
                'email_template_name': self.email_template_name,
                'subject_template_name': self.subject_template_name,
                'request': self.request,
                'html_email_template_name': None,
                'extra_email_context': None,
            }
            form.save(**opts)
            messages.success(self.request, "link has been sent to your email id. please check your inbox and if its not there check your spam as well.")
            return HttpResponseRedirect(self.success_url)
        return render(request, self.template_name, {'form': form})

# Logout View
class LogoutView(LoginRequiredMixin, LogoutView):
    
    # login_url = reverse_lazy('patient_login')
    # next_page = reverse_lazy('patient_login')
    login_url = None
    next_page = None

    @method_decorator(never_cache)
    def dispatch(self, request, *args, **kwargs):
        logout(request)
        next_page = self.get_next_page()
        if next_page:
            # Redirect to this page until the session has been cleared.
            messages.success(request, "You are logged out Successfully")
            return HttpResponseRedirect(next_page)
        return super().dispatch(request, *args, **kwargs)

# Login View
class LoginView(LoginView):
    
    """
    Display the login form and handle the login action.
    """
    form_class = None
    template_name = None
    success_url = None
    
    @method_decorator(sensitive_post_parameters())
    @method_decorator(csrf_protect)
    @method_decorator(never_cache)
    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            redirect_to = self.success_url
            return HttpResponseRedirect(redirect_to)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        """Security check complete. Log the user in."""
        login(self.request, form.get_user())
        return HttpResponseRedirect(self.success_url)

# Change View For common fields
class ChangeView(UpdateView):
    
    login_url = None
    form_class = ChangeForm
    template_name = None
    success_url = None

    def get_object(self):
        return self.request.user

# Password Change using old password view
class PasswordChangeView(PasswordChangeView):
    
    form_class = PasswordChangeForm
    success_url = None
    template_name = None
    login_url = None

    def form_valid(self, form):
        form.save()
        # Updating the password logs out all other sessions for the user
        # except the current one.
        messages.success(self.request, "Your Password Has been Successfully changed.")
        update_session_auth_hash(self.request, form.user)
        return super().form_valid(form)


# Password Reset View via email
class PasswordResetView(PasswordResetView):

    template_name = None
    success_url = None
    user_type = None
    form_class = PasswordResetForm
    email_template_name = None
    subject_template_name = None
    
    def form_valid(self, form):
        opts = {
            'use_https': self.request.is_secure(),
            'token_generator': self.token_generator,
            'from_email': self.from_email,
            'email_template_name': self.email_template_name,
            'subject_template_name': self.subject_template_name,
            'request': self.request,
            'html_email_template_name': self.html_email_template_name,
            'extra_email_context': self.extra_email_context,
            'user_type': self.user_type,
        }
        if form.save(**opts):
            messages.success(self.request, "Email has been sent to you.")
        else:
            messages.error(self.request, "This email is not registered.")
        return render(self.request, self.template_name, {'form': form})

