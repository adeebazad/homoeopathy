from rest_framework import serializers
from .models import Appointment

class AppointmentSerializer(serializers.ModelSerializer):
    patient_name = serializers.SerializerMethodField()
    doctor_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Appointment
        fields = ('id', 'patient', 'doctor', 'patient_name', 'doctor_name',
                 'date', 'time', 'status', 'reason', 'notes',
                 'created_at', 'updated_at')
        read_only_fields = ('status', 'patient', 'patient_name', 'doctor_name')
    
    def get_patient_name(self, obj):
        return f"{obj.patient.first_name} {obj.patient.last_name}"
    
    def get_doctor_name(self, obj):
        return f"{obj.doctor.first_name} {obj.doctor.last_name}"

    def validate(self, data):
        if not data.get('doctor'):
            raise serializers.ValidationError({'doctor': 'Doctor is required'})
        if not data.get('date'):
            raise serializers.ValidationError({'date': 'Date is required'})
        if not data.get('time'):
            raise serializers.ValidationError({'time': 'Time is required'})
        if not data.get('reason'):
            raise serializers.ValidationError({'reason': 'Reason is required'})
        return data
