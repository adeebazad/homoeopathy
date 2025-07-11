from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    DOCTOR = 'DOCTOR'
    PATIENT = 'PATIENT'
    
    ROLE_CHOICES = [
        (DOCTOR, 'Doctor'),
        (PATIENT, 'Patient'),
    ]
    
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default=PATIENT
    )
    phone_number = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    
    def is_doctor(self):
        return self.role == self.DOCTOR
    
    def is_patient(self):
        return self.role == self.PATIENT
