from rest_framework import serializers
from patients.models import PatientRecord, UpdateRequest
from appointments.models import Appointment
from django.contrib.auth import get_user_model

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        read_only_fields = ['id']

class PatientRecordSerializer(serializers.ModelSerializer):
    patient = UserSerializer(read_only=True)
    
    class Meta:
        model = PatientRecord
        fields = ['id', 'patient', 'blood_group', 'allergies', 'medical_history', 
                 'current_medications', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

class UpdateRequestSerializer(serializers.ModelSerializer):
    patient = UserSerializer(read_only=True)
    
    class Meta:
        model = UpdateRequest
        fields = ['id', 'patient', 'field_name', 'current_value', 'requested_value',
                 'reason', 'status', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

class AppointmentSerializer(serializers.ModelSerializer):
    patient = UserSerializer(read_only=True)
    doctor = UserSerializer(read_only=True)
    
    class Meta:
        model = Appointment
        fields = ['id', 'patient', 'doctor', 'date', 'time', 'status',
                 'reason', 'notes', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
        
    def validate(self, data):
        """
        Check that the appointment date and time are valid
        """
        # Add validation logic here if needed
        return data
