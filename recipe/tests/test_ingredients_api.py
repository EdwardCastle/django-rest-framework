from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from core.models import Ingredient
from recipe.serializers import IngredientSerializer

INGREDIENT_URL = reverse('recipe:ingredient-list')


class PublicIngredientApiTests(TestCase):
    """ Test API Ingredient public access """

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """ Test that login is necessary to access to this endpoint """
        request = self.client.get(INGREDIENT_URL)
        self.assertEqual(request.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientApiTests(TestCase):
    """ Test API Ingredient private access """

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'edward@castle.com',
            'test123'
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_ingredient_list(self):
        """ Test retrieve list of ingredients """
        Ingredient.objects.create(user=self.user, name='Tomato')
        Ingredient.objects.create(user=self.user, name='Sugar')

        request = self.client.get(INGREDIENT_URL)

        ingredients = Ingredient.objects.all().order_by('name')
        serializer = IngredientSerializer(ingredients, many=True)
        self.assertEqual(request.status_code, status.HTTP_200_OK)
        self.assertEqual(request.data, serializer.data)

    def test_ingredients_limited_to_user(self):
        """ Test return ingredients just authenticated by the user """
        user2 = get_user_model().objects.create_user(
            'testuser',
            'testpass'
        )
        Ingredient.objects.create(user=user2, name='Vinegar')
        ingredient = Ingredient.objects.create(user=self.user, name='gallic')

        request = self.client.get(INGREDIENT_URL)
        self.assertEqual(request.status_code, status.HTTP_200_OK)
        self.assertEqual(len(request.data), 1)
        self.assertEqual(request.data[0]['name'], ingredient.name)

    def test_create_ingredient_succesfully(self):
        """ Test create new ingredient """

        payload = {'name': 'chocolate'}

        self.client.post(INGREDIENT_URL, payload)

        exists = Ingredient.objects.filter(
            user=self.user,
            name=payload['name']
        ).exists()

        self.assertTrue(exists)

    def test_create_invalid_ingredient(self):
        """ Test create invalid ingredient """
        payload = {'name': ''}

        request = self.client.post(INGREDIENT_URL, payload)

        self.assertEqual(request.status_code, status.HTTP_400_BAD_REQUEST)
