from django.db import models
from core.models import CustomUser
# Create your models here.

speciality_choice = (
    ('allergy and immunology','Allergy and Immunology'),
    ('dermatology','Dermatology'),
    ('ent','ENT'),
)

class DoctorAdditional(models.Model):
    user=models.OneToOneField(CustomUser,on_delete=models.CASCADE)
    doctor_speciality = models.CharField(max_length=100, choices=speciality_choice,)
    doctor_number = models.IntegerField(null=True, blank=True, default=None)
    doctor_fees = models.IntegerField()
    def __str__(self):
        return self.user.first_name