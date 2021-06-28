from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils.translation import ugettext_lazy as _
from .managers import CustomUserManager

# Custom Model defined here


class CustomUser(AbstractBaseUser, PermissionsMixin):
  
  email = models.EmailField(
    verbose_name='email',
    max_length=255,
    unique=True,
  )
  first_name = models.CharField(max_length=255, blank=True, null=True)
  last_name = models.CharField(max_length=255, blank=True, null=True)
  is_staff = models.BooleanField(default=False)
  is_active = models.BooleanField(default=False)
  date_joined = models.DateTimeField(auto_now_add=True)

  is_doctor = models.BooleanField(default=False)
  is_patient = models.BooleanField(default=False)
  is_admin = models.BooleanField(default=False)
  
  objects = CustomUserManager()

  USERNAME_FIELD = 'email'
  REQUIRED_FIELDS = []

  class Meta:
    verbose_name = 'User'
    verbose_name_plural = 'Users'

  def get_full_name(self):
    return self.email

  def get_short_name(self):
    return self.email

  def __str__(self):
    return self.email