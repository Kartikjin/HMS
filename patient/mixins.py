from django.contrib.auth import mixins
from django.shortcuts import HttpResponseRedirect
from django.urls.base import reverse_lazy
class Is_login(mixins.AccessMixin):
    """Verify that the current user is logged in or not"""
    redirect_to = reverse_lazy('patient_home')
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return HttpResponseRedirect(self.redirect_to)
        return super().dispatch(request, *args, **kwargs)