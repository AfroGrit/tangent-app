from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Employee, Tag, Department

from staff.serializers import EmployeeSerializer, EmployeeDetailSerializer


EMPLOYEE_URL = reverse('staff:employee-list')


def detail_url(employee_id):
    """Return employee detail URL"""
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

    def test_create_basic_employee(self):
        """Test creating employee"""
        payload = {
            'title': 'Test employee',
            'experience': 3,
            'salary': 10.00,
        }
        res = self.client.post(EMPLOYEE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        employee = Employee.objects.get(id=res.data['id'])
        for key in payload.keys():
            self.assertEqual(payload[key], getattr(employee, key))

    def test_create_employee_with_tags(self):
        """Test creating a employee with tags"""
        tag1 = sample_tag(user=self.user, name='fixer')
        tag2 = sample_tag(user=self.user, name='singer')
        payload = {
            'title': 'Test employee with 2 tags',
            'tags': [tag1.id, tag2.id],
            'experience': 3,
            'salary': 10.00
        }
        res = self.client.post(EMPLOYEE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        employee = Employee.objects.get(id=res.data['id'])
        tags = employee.tags.all()
        self.assertEqual(tags.count(), 2)
        self.assertIn(tag1, tags)
        self.assertIn(tag2, tags)

    def test_create_employee_with_department(self):
        """Test creating employee with dept"""
        dept1 = sample_department(user=self.user, name='Department 1')
        dept2 = sample_department(user=self.user, name='Department 2')
        payload = {
            'title': 'Test employee with departments',
            'department': [dept1.id, dept2.id],
            'experience': 5,
            'salary': 15.00
        }

        res = self.client.post(EMPLOYEE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        employee = Employee.objects.get(id=res.data['id'])
        department = employee.department.all()
        self.assertEqual(department.count(), 2)
        self.assertIn(dept1, department)
        self.assertIn(dept2, department)

    def test_partial_update_employee(self):
        """Test updating an employee with patch"""
        employee = sample_employee(user=self.user)
        employee.tags.add(sample_tag(user=self.user))
        new_tag = sample_tag(user=self.user, name='brewer')

        payload = {'title': 'Run for charity', 'tags': [new_tag.id]}
        url = detail_url(employee.id)
        self.client.patch(url, payload)

        employee.refresh_from_db()
        self.assertEqual(employee.title, payload['title'])
        tags = employee.tags.all()
        self.assertEqual(len(tags), 1)
        self.assertIn(new_tag, tags)

    def test_full_update_employee(self):
        """Test updating an employee with put"""
        employee = sample_employee(user=self.user)
        employee.tags.add(sample_tag(user=self.user))

        payload = {
            'title': 'Monster Maker',
            'experience': 25,
            'salary': 5.00
        }
        url = detail_url(employee.id)
        self.client.put(url, payload)

        employee.refresh_from_db()
        self.assertEqual(employee.title, payload['title'])
        self.assertEqual(employee.experience, payload['experience'])
        self.assertEqual(employee.salary, payload['salary'])
        tags = employee.tags.all()
        self.assertEqual(len(tags), 0)
