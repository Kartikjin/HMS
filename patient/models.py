from datetime import timezone, datetime
from django.core.exceptions import ValidationError
from django.db import models
from core.models import CustomUser
from admins.models import HospitalDoctors

# Create your models here.
class PatientAdditional(models.Model):
    user = models.OneToOneField(CustomUser, on_delete = models.CASCADE)
    medical_history = models.CharField(max_length=100, null=True, blank=True)
    def __str__(self):
        return self.user.email

class Appointment(models.Model):
    
    def validate_date(date):
        try:
            format = "%Y-%m-%d"
            date = datetime.strptime(date, format).date()
            if date < datetime.now().date():
                raise ValidationError("Date cannot be in the past")
        except ValueError:
            raise ValidationError("Date is not in proper format")
            
    patient = models.ForeignKey(PatientAdditional, on_delete=models.CASCADE)
    hospital = models.ForeignKey(HospitalDoctors, on_delete=models.CASCADE)
    payment_status = models.BooleanField(default=False)
    status = models.BooleanField(default=True)
    problem = models.CharField(max_length=100)
    date = models.CharField(max_length=20,validators=[validate_date])
    # Related to razor pay
    razorpay_order_id = models.CharField(max_length=500, null=True, blank=True)
    razorpay_payment_id = models.CharField(max_length=500, null=True, blank=True)
    razorpay_signature = models.CharField(max_length=500, null=True, blank=True)

    