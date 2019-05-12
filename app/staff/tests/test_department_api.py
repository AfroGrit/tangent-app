from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Department

from staff.serializers import DepartmentSerializer


DEPARTMENT_URL = reverse('staff:department-list')


class PublicDepartmentApiTests(TestCase):
    """Test the publically available Department API"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test that login is required to access this endpoint"""
        res = self.client.get(DEPARTMENT_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateDepartmentAPITests(TestCase):
    """Test department can be retrieved by authorized user"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'test@tangent.com',
            'testpass'
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_department_list(self):
        """Test retrieving a list of department"""
        Department.objects.create(user=self.user, name='research')
        Department.objects.create(user=self.user, name='design')

        res = self.client.get(DEPARTMENT_URL)

        department = Department.objects.all().order_by('-name')
        serializer = DepartmentSerializer(department, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_department_limited_to_user(self):
        """Test that only department for authenticated user are returned"""
        user2 = get_user_model().objects.create_user(
            'other@tangent.com',
            'testpass'
        )

        Department.objects.create(user=user2, name='HR')
        department = Department.objects.create(user=self.user, name='drafting')

        res = self.client.get(DEPARTMENT_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], department.name)

    def test_create_department_successful(self):
        """Test creating a new department"""
        payload = {'name': 'rejects'}
        self.client.post(DEPARTMENT_URL, payload)

        exists = Department.objects.filter(
            user=self.user,
            name=payload['name']
        ).exists()
        self.assertTrue(exists)

    def test_create_department_invalid(self):
        """Test creating invalid department fails"""
        payload = {'name': ''}
        res = self.client.post(DEPARTMENT_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
