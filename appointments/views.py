from rest_framework import generics, permissions, status, serializers
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from .models import Appointment
from .serializers import AppointmentSerializer

class IsDoctorOrPatient(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user == obj.doctor or request.user == obj.patient

class AppointmentList(generics.ListCreateAPIView):
    serializer_class = AppointmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['status']
    search_fields = ['doctor__username', 'doctor__first_name', 'doctor__last_name', 'reason']
    ordering_fields = ['date', 'time', 'created_at', 'status']
    ordering = ['-date', '-time']

    def get_queryset(self):
        user = self.request.user
        if user.role == 'DOCTOR':
            return Appointment.objects.filter(doctor=user)
        return Appointment.objects.filter(patient=user)

    def perform_create(self, serializer):
        doctor_id = self.request.data.get('doctor')
        if not doctor_id:
            raise serializers.ValidationError({'doctor': 'Doctor is required'})
            
        User = get_user_model()
        doctor = get_object_or_404(User, id=doctor_id, role='DOCTOR', is_active=True)

        # Check if the patient already has a pending appointment with this doctor
        existing_appointment = Appointment.objects.filter(
            patient=self.request.user,
            doctor=doctor,
            status='PENDING',
            date=serializer.validated_data['date']
        ).exists()
        
        if existing_appointment:
            raise serializers.ValidationError({
                'appointment': 'You already have a pending appointment with this doctor for this date'
            })
        
        serializer.save(
            patient=self.request.user,
            doctor=doctor,
            status='PENDING'
        )

class AppointmentDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer
    permission_classes = [permissions.IsAuthenticated, IsDoctorOrPatient]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'DOCTOR':
            return Appointment.objects.filter(doctor=user)
        return Appointment.objects.filter(patient=user)

    def perform_update(self, serializer):
        if serializer.validated_data.get('status'):
            if self.request.user.role != 'DOCTOR':
                raise serializers.ValidationError({'status': 'Only doctors can update appointment status'})
        serializer.save()

class AppointmentStatusUpdate(generics.UpdateAPIView):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def update(self, request, *args, **kwargs):
        appointment = self.get_object()
        new_status = kwargs.get('status', request.data.get('status'))
        
        if new_status in ['APPROVED', 'REJECTED', 'COMPLETED']:
            if request.user != appointment.doctor:
                return Response(
                    {'error': 'Only the assigned doctor can update this appointment status'},
                    status=status.HTTP_403_FORBIDDEN
                )
        elif new_status == 'CANCELLED':
            if request.user != appointment.patient:
                return Response(
                    {'error': 'Only the patient can cancel their appointments'},
                    status=status.HTTP_403_FORBIDDEN
                )
        else:
            return Response(
                {'error': 'Invalid status update'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        appointment.status = new_status
        appointment.save()
        return Response({'status': f'appointment {new_status.lower()}'})

class AppointmentBaseAction(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_appointment(self, pk):
        return get_object_or_404(Appointment, pk=pk)

    def post(self, request, pk, format=None):
        appointment = self.get_appointment(pk)
        if not self.check_permission(request.user, appointment):
            return Response(
                {'error': self.error_message},
                status=status.HTTP_403_FORBIDDEN
            )
        appointment.status = self.new_status
        appointment.save()
        return Response({'status': f'appointment {self.new_status.lower()}'})

class AppointmentApprove(AppointmentBaseAction):
    new_status = 'APPROVED'
    error_message = 'Only the assigned doctor can approve appointments'

    def check_permission(self, user, appointment):
        return user == appointment.doctor

class AppointmentReject(AppointmentBaseAction):
    new_status = 'REJECTED'
    error_message = 'Only the assigned doctor can reject appointments'

    def check_permission(self, user, appointment):
        return user == appointment.doctor

class AppointmentCancel(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        appointment = get_object_or_404(Appointment, pk=pk)
        
        # Only allow cancellation if the appointment is pending or approved
        if appointment.status not in ['PENDING', 'APPROVED']:
            return Response(
                {'error': 'Only pending or approved appointments can be cancelled'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if user is the patient
        if request.user != appointment.patient:
            return Response(
                {'error': 'Only the patient can cancel their appointments'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        appointment.status = 'CANCELLED'
        appointment.save()
        
        serializer = AppointmentSerializer(appointment)
        return Response(serializer.data)

class AppointmentComplete(AppointmentBaseAction):
    new_status = 'COMPLETED'
    error_message = 'Only the assigned doctor can complete appointments'

    def check_permission(self, user, appointment):
        return user == appointment.doctor
