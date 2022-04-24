from django.test import TestCase
from django.contrib.auth import get_user_model


class ModelTest(TestCase):

    def test_create_user_with_email(self):
        """ Test for creating a new user email correctly """

        email = 'edward@castle.com'
        password = 'test123'
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )
        self.assertEqual(email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """" Test for a new normalized user email """

        email = 'edward@CASTLE.com'
        password = 'test123'
        user = get_user_model().objects.create_user(email=email, password=password)
        self.assertEqual(user.email, email.lower())

    def test_new_user_invalid_email(self):
        """ Test new invalid user email """

        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None, 'test123')

    def test_create_new_superuser(self):
        """ Test new created superuser """

        email = 'edward@castle.com'
        password = 'test123'
        user = get_user_model().objects.create_superuser(
            email=email,
            password=password
        )

        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)


