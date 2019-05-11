from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status


CREATE_USERS_URL = reverse('users:create')


def create_user(**params):
    """Helper function to create new user"""
    return get_user_model().objects.create_user(**params)


class PublicUserApiTests(TestCase):
    """Test the users API (public)"""

    def setUp(self):
        self.client = APIClient()

    def test_create_valid_user_success(self):
        """Test creating using with a valid payload is successful"""
        payload = {
            'email': 'test@tangent.co.za',
            'password': 'testpass',
            'name': 'name',
        }
        res = self.client.post(CREATE_USERS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        users = get_user_model().objects.get(**res.data)
        self.assertTrue(
            users.check_password(payload['password'])
        )
        self.assertNotIn('password', res.data)

    def test_user_exists(self):
        """ Test creating a duplicate user (already exists fails)"""
        payload = {'email': 'test@tangent.co.za', 'password': 'testpass'}
        create_user(**payload)
        res = self.client.post(CREATE_USERS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        """Test that password must be more than 5 characters"""
        payload = {'email': 'test@tangent.co.za', 'password': 'pw'}
        res = self.client.post(CREATE_USERS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        users_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()
        self.assertFalse(users_exists)
