from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'patient-records', views.PatientRecordViewSet, basename='patient-record')
router.register(r'update-requests', views.UpdateRequestViewSet, basename='update-request')
router.register(r'appointments', views.AppointmentViewSet, basename='appointment')

urlpatterns = [
    path('', include(router.urls)),
]
