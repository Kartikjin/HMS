from django.db import models
from core.models import CustomUser
from doctor.models import DoctorAdditional
# Create your models here.
class AdminAdditional(models.Model):
    user=models.OneToOneField(CustomUser,on_delete=models.CASCADE)
    hospital_name = models.CharField(max_length=100)
    hospital_address = models.CharField(max_length=100)
    is_recruiting = models.BooleanField(default=False, blank=True)

    def __str__(self):
        return self.user.email
    

status_choice = (
    ('applied','Applied'),
    ('rejected','Rejected'),
    ('approved','Approved'),
    ('laidoff','Laid-off'),
)
class HospitalDoctors(models.Model):
    doctor_id = models.ForeignKey(DoctorAdditional, related_name='doctor_id', null=True, on_delete=models.CASCADE)
    hospital_id = models.ForeignKey(AdminAdditional, related_name='hospital_id', null=True, on_delete=models.CASCADE)
    status = models.CharField(
        choices=status_choice,
        max_length=10, 
    )

    def __str__(self):
        return self.doctor_id.user.first_name