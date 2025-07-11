from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import ValidationError
from .models import PatientRecord, UpdateRequest
from .serializers import PatientRecordSerializer, UpdateRequestSerializer

class IsOwnerOrDoctor(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.role == 'DOCTOR':
            return True
        return obj.patient == request.user

class PatientRecordList(generics.ListAPIView):
    serializer_class = PatientRecordSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'DOCTOR':
            return PatientRecord.objects.all()
        return PatientRecord.objects.filter(patient=user)

class PatientRecordDetail(generics.RetrieveUpdateAPIView):
    serializer_class = PatientRecordSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrDoctor]

    def get_object(self):
        if self.request.user.role == 'PATIENT':
            return PatientRecord.objects.get_or_create(patient=self.request.user)[0]
        # For doctors, allow /api/patients/record/<patient_id>/
        patient_id = self.kwargs.get('patient_id')
        if patient_id:
            return get_object_or_404(PatientRecord, patient_id=patient_id)
        # If no patient_id, return 404
        raise ValidationError({'detail': 'Patient ID required for doctors.'})

class UpdateRequestList(generics.ListCreateAPIView):
    serializer_class = UpdateRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'DOCTOR':
            return UpdateRequest.objects.all()
        return UpdateRequest.objects.filter(patient=user)

    def perform_create(self, serializer):
        serializer.save(patient=self.request.user)

class UpdateRequestDetail(generics.RetrieveUpdateAPIView):
    queryset = UpdateRequest.objects.all()
    serializer_class = UpdateRequestSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrDoctor]

    def update(self, request, *args, **kwargs):
        if request.user.role != 'DOCTOR':
            return Response(
                {'error': 'Only doctors can approve/reject update requests'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().update(request, *args, **kwargs)
