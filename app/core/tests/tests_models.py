from unittest.mock import patch

from django.test import TestCase
from django.contrib.auth import get_user_model

from core import models


def sample_user(email='test@tangent.com', password='testpass'):
    """ Creating a sample user """
    return get_user_model().objects.create_user(email, password)


class ModelTests(TestCase):

    def test_create_user_with_email_successful(self):
        """ Test create new users with email """
        email = 'test@tangent.com'
        password = 'Testpass123'
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """ normalize email """
        email = 'test@TANGENT.COM'
        user = get_user_model().objects.create_user(email, 'test123')

        self.assertEqual(user.email, email.lower())

    def test_new_user_invalid_email(self):
        """ Error with no email """
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None, 'test123')

    def test_create_superuser(self):
        """ Test creating superusers"""
        user = get_user_model().objects.create_superuser(
            'test@tangent.com',
            'test123'
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_tag_str(self):
        """ Test the tag string """
        tag = models.Tag.objects.create(
            user=sample_user(),
            name='Intern'
        )

        self.assertEqual(str(tag), tag.name)

    def test_department_str(self):
        """Test the department string representation"""
        department = models.Department.objects.create(
            user=sample_user(),
            name='Marketing'
        )

        self.assertEqual(str(department), department.name)

    def test_employee_str(self):
        """Test the employee string representation"""
        employee = models.Employee.objects.create(
            user=sample_user(),
            title='Story teller',
            experience=5,
            salary=50.00
        )

        self.assertEqual(str(employee), employee.title)

    @patch('uuid.uuid4')
    def test_employee_file_name_uuid(self, mock_uuid):
        """Test that image is saved in the correct dir"""
        uuid = 'test-uuid'
        mock_uuid.return_value = uuid
        file_path = models.employee_image_file_path(None, 'myimage.jpg')

        exp_path = f'uploads/employee/{uuid}.jpg'
        self.assertEqual(file_path, exp_path)
