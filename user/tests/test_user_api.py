from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')
MY_URL = reverse('user:me')


def create_user(**params):
    return get_user_model().objects.create_user(**params)


class PublicUserApi(TestCase):
    """ Test Public User API """

    def setUp(self):
        self.client = APIClient()

    def test_create_valid_user_success(self):
        """ Test create user with a payload correctly """

        payload = {
            'email': 'edward@castle.com',
            'password': 'test123',
            'name': 'edward'
        }

        request = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(request.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(**request.data)
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', request.data)

    def test_user_exists(self):
        """ Test if an user already exists """

        payload = {
            'email': 'edward@castle.com',
            'password': 'test123',
            'name': 'edward'
        }

        create_user(**payload)
        request = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(request.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        """ Test that the password is longer than 5 characters """

        payload = {
            'email': 'edward@castle.com',
            'password': 'test',
            'name': 'edward'
        }

        request = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(request.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()
        self.assertFalse(user_exists)

    def test_create_token_for_user(self):
        """ Test if the token have been created by the user """

        payload = {
            'email': 'edward@castle.com',
            'password': 'test123',
            'name': 'edward'
        }

        create_user(**payload)
        request = self.client.post(TOKEN_URL, payload)
        self.assertIn('token', request.data)
        self.assertEqual(request.status_code, status.HTTP_200_OK)

    def test_create_token_invalid_credentials(self):
        """ Test that the token was not created with invalid credentials """

        create_user(email='edward@castle.com', password='test123')
        payload = {'email': 'edward@castle.com', 'password': '123'}
        request = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', request.data)
        self.assertEqual(request.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_no_user(self):
        """ Test that the token is not created if the user does not exist """

        payload = {
            'email': 'edward@castle.com',
            'password': 'test123',
            'name': 'edward'
        }

        request = self.client.post(TOKEN_URL, payload)
        self.assertNotIn('token', request.data)
        self.assertEqual(request.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_missing_field(self):
        """ Test that the user and password are required """

        payload = {
            'email': 'edwad',
            'password': '',
            'name': 'edward'
        }

        request = self.client.post(TOKEN_URL, payload)
        self.assertNotIn('token', request.data)
        self.assertEqual(request.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_user_unauthorized(self):
        """ Test that the authentication is required for the user """

        request = self.client.get(MY_URL)
        self.assertEqual(request.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserApiTests(TestCase):
    """ Test Private API for the user """

    def setUp(self):
        self.user = create_user(
            email='edward@castle.com',
            password='test123',
            name='edward'
        )

        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_profile_success(self):
        """ Test retrieve a logged in User """

        request = self.client.get(MY_URL)
        self.assertEqual(request.status_code, status.HTTP_200_OK)
        self.assertEqual(request.data, {
            'name': self.user.name,
            'email': self.user.email,
        })

    def test_not_allowed(self):
        """ Test that POST is not allowed """

        request = self.client.post(MY_URL, {})
        self.assertEqual(request.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_profile(self):
        """ Test that the user is being updated if is authenticate """

        payload = {
            'name': 'newname',
            'password': 'newpass',
        }

        request = self.client.patch(MY_URL, payload)
        self.user.refresh_from_db()
        self.assertEqual(self.user.name, payload['name'])
        self.assertTrue(self.user.check_password(payload['password']))
        self.assertEqual(request.status_code, status.HTTP_200_OK)
