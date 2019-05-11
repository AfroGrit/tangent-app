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
