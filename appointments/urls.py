from django.urls import path
from . import views
from rest_framework.urlpatterns import format_suffix_patterns

urlpatterns = format_suffix_patterns([
    path('', views.AppointmentList.as_view(), name='appointment-list'),
    path('<int:pk>/', views.AppointmentDetail.as_view(), name='appointment-detail'),
    path('<int:pk>/status/', views.AppointmentStatusUpdate.as_view(), name='appointment-status'),
    path('<int:pk>/approve/', views.AppointmentApprove.as_view(), name='appointment-approve'),
    path('<int:pk>/reject/', views.AppointmentReject.as_view(), name='appointment-reject'),
    path('<int:pk>/cancel/', views.AppointmentCancel.as_view(), name='appointment-cancel'),
    path('<int:pk>/complete/', views.AppointmentComplete.as_view(), name='appointment-complete'),
])
