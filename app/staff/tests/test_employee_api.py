from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Employee, Tag, Department

from staff.serializers import EmployeeSerializer, EmployeeDetailSerializer


EMPLOYEE_URL = reverse('staff:employee-list')


def detail_url(employee_id):
    """Return recipe detail URL"""
    return reverse('staff:employee-detail', args=[employee_id])


def sample_tag(user, name='Sprints'):
    """Create and return a sample tag"""
    return Tag.objects.create(user=user, name=name)


def sample_department(user, name='Accounts'):
    """Create and return a sample dept"""
    return Department.objects.create(user=user, name=name)


def sample_employee(user, **params):
    """Create and return a sample Employee"""
    defaults = {
        'title': 'Sample employee',
        'experience': 10,
        'salary': 5.00,
    }
    defaults.update(params)

    return Employee.objects.create(user=user, **defaults)


class PublicEmployeeApiTests(TestCase):
    """Test unauthenticated Employee API access"""

    def setUp(self):
        self.client = APIClient()

    def test_required_auth(self):
        """Test the authenticaiton is required"""
        res = self.client.get(EMPLOYEE_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateEmployeeApiTests(TestCase):
    """Test authenticated Employee API access"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'test@tangent.com',
            'testpass'
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_employee(self):
        """Test retrieving list of Employees"""
        sample_employee(user=self.user)
        sample_employee(user=self.user)

        res = self.client.get(EMPLOYEE_URL)

        employee = Employee.objects.all().order_by('-id')
        serializer = EmployeeSerializer(employee, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_employee_limited_to_user(self):
        """Test retrieving Employees for user"""
        user2 = get_user_model().objects.create_user(
            'other@tangent.com',
            'pass'
        )
        sample_employee(user=user2)
        sample_employee(user=self.user)

        res = self.client.get(EMPLOYEE_URL)

        employee = Employee.objects.filter(user=self.user)
        serializer = EmployeeSerializer(employee, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data, serializer.data)

    def test_view_employee_detail(self):
        """Test viewing a employee detail"""
        employee = sample_employee(user=self.user)
        employee.tags.add(sample_tag(user=self.user))
        employee.department.add(sample_department(user=self.user))

        url = detail_url(employee.id)
        res = self.client.get(url)

        serializer = EmployeeDetailSerializer(employee)
        self.assertEqual(res.data, serializer.data)
