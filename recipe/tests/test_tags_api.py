from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from core.models import Tag, Recipe
from recipe.serializers import TagSerializer

TAGS_URL = reverse('recipe:tag-list')


class PublicTagsTest(TestCase):
    """ Test all public Tags api """

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """ Test that login is required to see the tags """

        request = self.client.get(TAGS_URL)

        self.assertEqual(request.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagsTest(TestCase):
    """ Test all private Tags api """

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            'edward@castle.com',
            'password'
        )

        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_tags(self):
        """ Test get Tags """

        Tag.objects.create(user=self.user, name='Meat')
        Tag.objects.create(user=self.user, name='Rice')

        request = self.client.get(TAGS_URL)
        tags = Tag.objects.all().order_by('name')
        serializer = TagSerializer(tags, many=True)
        self.assertEqual(request.status_code, status.HTTP_200_OK)
        self.assertEqual(request.data, serializer.data)

    def test_tags_limited_to_user(self):
        """ Test that the returned tags are from the user """

        user2 = get_user_model().objects.create_user(
            'edward@zzz.com',
            'password'
        )

        Tag.objects.create(user=user2, name='Mango')
        tag = Tag.objects.create(user=self.user, name='Some Food')
        request = self.client.get(TAGS_URL)
        self.assertEqual(request.status_code, status.HTTP_200_OK)
        self.assertEqual(len(request.data), 1)
        self.assertEqual(request.data[0]['name'], tag.name)

    def test_create_tag_successfully(self):
        """ Test Create new Tag """

        payload = {'name': 'simple'}
        self.client.post(TAGS_URL, payload)
        exists = Tag.objects.filter(
            user=self.user,
            name=payload['name']
        ).exists()
        self.assertTrue(exists)

    def test_create_tag_invalid(self):
        """ Test create a new tag with an invalid payload """

        payload = {'name': ''}
        request = self.client.post(TAGS_URL, payload)

        self.assertEqual(request.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_tags_assigned_to_recipe(self):
        """ Test filter tags base on recipe """
        tag1 = Tag.objects.create(user=self.user, name='Breakfast')
        tag2 = Tag.objects.create(user=self.user, name='Dinner')

        recipe = Recipe.objects.create(
            user=self.user,
            title='Coriander eggs and toast',
            time_minutes=10,
            price=5.00,
        )
        recipe.tags.add(tag1)
        request = self.client.get(TAGS_URL, {'assigned_only': 1})

        serializer1 = TagSerializer(tag1)
        serializer2 = TagSerializer(tag2)
        self.assertIn(serializer1.data, request.data)
        self.assertNotIn(serializer2.data, request.data)

    def test_retrieve_tags_assigned_unique(self):
        """ Test filter tags assigned for unique items """
        tag = Tag.objects.create(user=self.user, name='Breakfast')
        recipe1 = Recipe.objects.create(
            user=self.user,
            title='pancakes',
            time_minutes=5,
            price=3.0,
        )
        recipe1.tags.add(tag)
        recipe2 = Recipe.objects.create(
            title='Porridge',
            time_minutes=2,
            price=12.0,
            user=self.user
        )
        recipe2.tags.add(tag)
        request = self.client.get(TAGS_URL, {'assigned_only': 1})

        self.assertEqual(len(request.data), 1)
