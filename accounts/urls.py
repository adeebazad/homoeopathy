from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from . import views
from .views import RegisterView, UserDetailView, get_csrf_token, DoctorListView, get_current_user, debug_current_user

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('profile/', UserDetailView.as_view(), name='user-profile'),
    path('profile/debug/', debug_current_user, name='debug-user-profile'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('csrf/', get_csrf_token, name='csrf'),
    path('doctors/', DoctorListView.as_view(), name='doctor-list'),
]
