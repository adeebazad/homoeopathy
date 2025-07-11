from django.contrib import admin
from .models import PatientRecord, UpdateRequest

@admin.register(PatientRecord)
class PatientRecordAdmin(admin.ModelAdmin):
    list_display = ('patient', 'blood_group', 'created_at', 'updated_at')
    search_fields = ('patient__username', 'medical_history', 'allergies')
    date_hierarchy = 'created_at'

@admin.register(UpdateRequest)
class UpdateRequestAdmin(admin.ModelAdmin):
    list_display = ('patient', 'field_name', 'status', 'created_at')
    list_filter = ('status', 'field_name')
    search_fields = ('patient__username', 'field_name', 'reason')
    date_hierarchy = 'created_at'
