from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from patients.models import PatientRecord, UpdateRequest
from appointments.models import Appointment
from .serializers import (
    PatientRecordSerializer,
    UpdateRequestSerializer,
    AppointmentSerializer
)
from django.contrib.auth import get_user_model

class PatientRecordViewSet(viewsets.ModelViewSet):
    serializer_class = PatientRecordSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['patient__username', 'patient__email', 'blood_group']

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return PatientRecord.objects.all()
        return PatientRecord.objects.filter(patient=user)

    def perform_create(self, serializer):
        serializer.save(patient=self.request.user)

class UpdateRequestViewSet(viewsets.ModelViewSet):
    serializer_class = UpdateRequestSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return UpdateRequest.objects.all()
        return UpdateRequest.objects.filter(patient=user)

    def perform_create(self, serializer):
        serializer.save(patient=self.request.user)

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        update_request = self.get_object()
        update_request.status = 'APPROVED'
        update_request.save()
        
        # Update the patient record
        patient_record = update_request.patient.medical_record
        setattr(patient_record, update_request.field_name, update_request.requested_value)
        patient_record.save()
        
        return Response({'status': 'request approved'})

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        update_request = self.get_object()
        update_request.status = 'REJECTED'
        update_request.save()
        return Response({'status': 'request rejected'})

class AppointmentViewSet(viewsets.ModelViewSet):
    serializer_class = AppointmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['patient__username', 'doctor__username', 'status']

    def get_queryset(self):
        user = self.request.user
        if user.role == 'DOCTOR':
            return Appointment.objects.filter(doctor=user)
        return Appointment.objects.filter(patient=user)

    def perform_create(self, serializer):
        doctor_id = self.request.data.get('doctor')
        doctor = get_object_or_404(get_user_model(), id=doctor_id, role='DOCTOR')
        serializer.save(patient=self.request.user, doctor=doctor)

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        appointment = self.get_object()
        if request.user != appointment.doctor:
            return Response(
                {'error': 'Only the assigned doctor can approve appointments'},
                status=status.HTTP_403_FORBIDDEN
            )
        appointment.status = 'APPROVED'
        appointment.save()
        return Response({'status': 'appointment approved'})

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        appointment = self.get_object()
        if request.user != appointment.doctor:
            return Response(
                {'error': 'Only the assigned doctor can reject appointments'},
                status=status.HTTP_403_FORBIDDEN
            )
        appointment.status = 'REJECTED'
        appointment.save()
        return Response({'status': 'appointment rejected'})

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        appointment = self.get_object()
        if request.user != appointment.patient:
            return Response(
                {'error': 'Only the patient can cancel their appointments'},
                status=status.HTTP_403_FORBIDDEN
            )
        appointment.status = 'CANCELLED'
        appointment.save()
        return Response({'status': 'appointment cancelled'})

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        appointment = self.get_object()
        if request.user != appointment.doctor:
            return Response(
                {'error': 'Only the assigned doctor can complete appointments'},
                status=status.HTTP_403_FORBIDDEN
            )
        appointment.status = 'COMPLETED'
        appointment.save()
        return Response({'status': 'appointment completed'})
