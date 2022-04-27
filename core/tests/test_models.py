""" Define all your models test here  """

from django.test import TestCase
from django.contrib.auth import get_user_model

from core import models


def sample_user(email='edward@castle.com', password='test123'):
    """ Create a sample user """
    return get_user_model().objects.create_user(email=email, password=password)


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

    def test_tag_str(self):
        """ Test String representation of Tag """
        tag = models.Tag.objects.create(
            user=sample_user(),
            name='edward'
        )

        self.assertEqual(str(tag), tag.name)

    def test_ingredient_str(self):
        """ Test String representation of Ingredient """
        ingredient = models.Ingredient.objects.create(
            user=sample_user(),
            name='Banana'
        )

        self.assertEqual(str(ingredient), ingredient.name)

    def test_recipe_str(self):
        """ Test String representation of Ingredient """
        recipe = models.Recipe.objects.create(
            user=sample_user(),
            title='Sample recipe',
            time_minutes=5,
            price=5.00
        )

        self.assertEqual(str(recipe), recipe.title)
