from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

class AuthenticationTests(APITestCase):
    def setUp(self):
        # Create a test doctor
        self.doctor = User.objects.create_user(
            username='testdoctor',
            password='testpass123',
            email='doctor@test.com',
            role='DOCTOR'
        )
        
        # Create a test patient
        self.patient = User.objects.create_user(
            username='testpatient',
            password='testpass123',
            email='patient@test.com',
            role='PATIENT'
        )
        
        # URLs
        self.register_url = reverse('register')
        self.token_url = reverse('token_obtain_pair')
        self.token_refresh_url = reverse('token_refresh')
        self.profile_url = reverse('user-detail')

    def test_user_registration(self):
        """Test user registration with valid data"""
        data = {
            'username': 'newuser',
            'password': 'newpass123',
            'email': 'new@test.com',
            'role': 'PATIENT',
            'first_name': 'New',
            'last_name': 'User'
        }
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 3)
        self.assertEqual(User.objects.get(username='newuser').role, 'PATIENT')

    def test_user_login(self):
        """Test user can login and receive tokens"""
        data = {
            'username': 'testpatient',
            'password': 'testpass123'
        }
        response = self.client.post(self.token_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_token_refresh(self):
        """Test refresh token functionality"""
        # First get the refresh token
        refresh = RefreshToken.for_user(self.patient)
        data = {'refresh': str(refresh)}
        
        response = self.client.post(self.token_refresh_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)

    def test_protected_endpoint_access(self):
        """Test accessing protected endpoint with and without token"""
        # Try without token
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Try with token
        token = RefreshToken.for_user(self.patient)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token.access_token}')
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_invalid_registration(self):
        """Test registration with invalid data"""
        # Test with missing required fields
        data = {'username': 'testuser'}
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Test with invalid role
        data = {
            'username': 'testuser',
            'password': 'testpass123',
            'email': 'test@test.com',
            'role': 'INVALID_ROLE'
        }
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_login(self):
        """Test login with invalid credentials"""
        data = {
            'username': 'testpatient',
            'password': 'wrongpass'
        }
        response = self.client.post(self.token_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
