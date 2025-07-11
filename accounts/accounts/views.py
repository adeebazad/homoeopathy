from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth import get_user_model
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_protect
from django.utils.decorators import method_decorator
from django.http import JsonResponse
from .serializers import UserSerializer, UserUpdateSerializer

User = get_user_model()

@method_decorator(ensure_csrf_cookie, name='dispatch')
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = UserSerializer
    authentication_classes = []  # Disable authentication for registration

    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        print(f"Request Headers: {request.headers}")  # Debug log
        return response

    def options(self, request, *args, **kwargs):
        response = super().options(request, *args, **kwargs)
        response["Access-Control-Allow-Origin"] = "http://localhost:14074"
        response["Access-Control-Allow-Headers"] = "Content-Type, X-CSRFToken"
        response["Access-Control-Allow-Credentials"] = "true"
        return response

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                'status': 'success',
                'message': 'User registered successfully',
                'user': UserSerializer(user).data
            }, status=status.HTTP_201_CREATED)
        return Response({
            'status': 'error',
            'message': 'Registration failed',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

class UserDetailView(generics.RetrieveUpdateAPIView):
    queryset = User.objects.all()
    permission_classes = (permissions.IsAuthenticated,)
    # Default to UserUpdateSerializer for PATCH/PUT
    serializer_class = UserUpdateSerializer

    def get_object(self):
        return self.request.user

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return UserSerializer
        return UserUpdateSerializer

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                'status': 'success',
                'message': 'Profile updated successfully',
                'user': UserSerializer(user).data
            })
        return Response({
            'status': 'error',
            'message': 'Profile update failed',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

from rest_framework.pagination import PageNumberPagination

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 100
    page_size_query_param = 'page_size'
    max_page_size = 1000

class DoctorListView(generics.ListAPIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = UserSerializer
    pagination_class = StandardResultsSetPagination
    filterset_fields = ['is_active']
    search_fields = ['username', 'first_name', 'last_name', 'email']
    ordering_fields = ['first_name', 'last_name', 'date_joined']
    ordering = ['first_name', 'last_name']

    def get_queryset(self):
        return User.objects.filter(role='DOCTOR', is_active=True)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        if request.query_params.get('no_page', False):
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        return super().list(request, *args, **kwargs)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_current_user(request):
    """
    Get current user profile (with all fields)
    """
    print('DEBUG: request.user:', request.user)
    print('DEBUG: request.user.__class__:', request.user.__class__)
    serializer = UserSerializer(request.user)
    print('DEBUG: serializer.data:', serializer.data)
    return Response(serializer.data)

@ensure_csrf_cookie
@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def get_csrf_token(request):
    response = JsonResponse({'detail': 'CSRF cookie set'})
    response["Access-Control-Allow-Origin"] = "http://localhost:3000"
    response["Access-Control-Allow-Credentials"] = "true"
    return response
    print("Setting CSRF cookie...")  # Debug log
    response = JsonResponse({'detail': 'CSRF cookie set'})
    if 'csrftoken' not in request.COOKIES:
        print("CSRF cookie not found in request")
    else:
        print(f"CSRF cookie found: {request.COOKIES['csrftoken']}")
    return response

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def debug_current_user(request):
    from django.http import JsonResponse
    return JsonResponse(request.user.__dict__)
