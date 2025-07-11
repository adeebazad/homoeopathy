from rest_framework import serializers
from .models import PatientRecord, UpdateRequest

class PatientRecordSerializer(serializers.ModelSerializer):
    patient_name = serializers.SerializerMethodField()
    
    class Meta:
        model = PatientRecord
        fields = ('id', 'patient', 'patient_name', 'blood_group', 'allergies',
                 'medical_history', 'current_medications', 'created_at', 'updated_at')
        read_only_fields = ('patient',)
    
    def get_patient_name(self, obj):
        return f"{obj.patient.first_name} {obj.patient.last_name}"

class UpdateRequestSerializer(serializers.ModelSerializer):
    patient = serializers.PrimaryKeyRelatedField(read_only=True)
    patient_name = serializers.SerializerMethodField()
    
    class Meta:
        model = UpdateRequest
        fields = ('id', 'patient', 'patient_name', 'field_name', 'current_value',
                 'requested_value', 'reason', 'status', 'created_at', 'updated_at')
        read_only_fields = ('status',)
    
    def get_patient_name(self, obj):
        return f"{obj.patient.first_name} {obj.patient.last_name}"
