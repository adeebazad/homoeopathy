from django.urls import path
from . import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()

urlpatterns = [
    path('record/', views.PatientRecordDetail.as_view(), name='patient-record'),
    path('record/<int:patient_id>/', views.PatientRecordDetail.as_view(), name='patient-record-by-id'),
    path('records/', views.PatientRecordList.as_view(), name='patient-record-list'),  # Added plural endpoint
    path('updates/', views.UpdateRequestList.as_view(), name='update-request-list'),
    path('updates/<int:pk>/', views.UpdateRequestDetail.as_view(), name='update-request-detail'),
] + router.urls
