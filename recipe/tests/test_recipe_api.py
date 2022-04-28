from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe, Tag, Ingredient
from recipe.serializers import RecipeSerializer, RecipeDetailSerializer

RECIPES_URL = reverse('recipe:recipe-list')


def sample_tag(user, name='Main course'):
    """ Create Tag example """
    return Tag.objects.create(user=user, name=name)


def sample_ingredient(user, name='Sugar'):
    """ Create ingredient example"""
    return Ingredient.objects.create(user=user, name=name)


def sample_recipe(user, **params):
    """ Create recipe example"""
    defaults = {
        'title': 'Sample recipe',
        'time_minutes': 10,
        'price': 5.00
    }
    defaults.update(params)

    return Recipe.objects.create(user=user, **defaults)


def detail_url(recipe_id):
    """ Return recipe detail url """
    return reverse('recipe:recipe-detail', args=[recipe_id])


class PublicRecipeApiTest(TestCase):
    """ Test no authenticate access to the API """

    def setUp(self):
        self.client = APIClient()

    def test_required_auth(self):
        request = self.client.get(RECIPES_URL)

        self.assertEqual(request.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeApiTest(TestCase):
    """ Test authenticate access to the API """

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'test@test.com',
            'test123'
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_recipes(self):
        """ Test retrieve a list of recipes """
        sample_recipe(user=self.user)
        sample_recipe(user=self.user)

        request = self.client.get(RECIPES_URL)
        recipes = Recipe.objects.all().order_by('id')
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(request.status_code, status.HTTP_200_OK)
        self.assertEqual(request.data, serializer.data)

    def test_retrieve_recipes_limited_to_user(self):
        """ Test retrieve a list of recipes for a user """
        user2 = get_user_model().objects.create_user(
            'edward@castle.com',
            'pass123'
        )
        sample_recipe(user=user2)
        sample_recipe(user=self.user)

        request = self.client.get(RECIPES_URL)
        recipes = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(request.status_code, status.HTTP_200_OK)
        self.assertEqual(len(request.data), 1)
        self.assertEqual(request.data, serializer.data)

    def test_view_recipe_detail(self):
        """ Test to see recipe details """
        recipe = sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))
        recipe.ingredients.add(sample_ingredient(user=self.user))

        url = detail_url(recipe.id)
        request = self.client.get(url)

        serializer = RecipeDetailSerializer(recipe)

        self.assertEqual(request.data, serializer.data)

    def test_create_basic_recipe(self):
        """ Test create new recipe, (with no tags) """

        payload = {
            'title': 'Sample recipe',
            'time_minutes': 10,
            'price': 5.00
        }

        request = self.client.post(RECIPES_URL, payload)
        self.assertEqual(request.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=request.data['id'])

        for key in payload.keys():
            self.assertEqual(payload[key], getattr(recipe, key))

    def test_create_recipe_with_tags(self):
        """ Test create a new recipe with tags """

        tag1 = Tag.objects.create(user=self.user, name='Tag 1')
        tag2 = Tag.objects.create(user=self.user, name='Tag 2')
        payload = {
            'title': 'Test recipe 2 tags',
            'tags': [tag1.id, tag2.id],
            'time_minutes': 10,
            'price': 5.00
        }

        request = self.client.post(RECIPES_URL, payload)

        self.assertEqual(request.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=request.data['id'])
        tags = recipe.tags.all()
        print('******')
        print(tags)
        self.assertEqual(tags.count(), 2)
        self.assertIn(tag1, tags)
        self.assertIn(tag2, tags)

    def test_create_recipe_with_ingredients(self):
        """ Test create a new recipe with ingredients """

        ingredient1 = Ingredient.objects.create(user=self.user, name='ingredient 1')
        ingredient2 = Ingredient.objects.create(user=self.user, name='ingredient 2')
        payload = {
            'title': 'Test recipe 2 ingredients',
            'ingredients': [ingredient1.id, ingredient2.id],
            'time_minutes': 10,
            'price': 5.00
        }

        request = self.client.post(RECIPES_URL, payload)

        self.assertEqual(request.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=request.data['id'])
        ingredients = recipe.ingredients.all()
        self.assertEqual(ingredients.count(), 2)
        self.assertIn(ingredient1, ingredients)
        self.assertIn(ingredient2, ingredients)
