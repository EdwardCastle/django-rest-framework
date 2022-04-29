from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from core.models import Tag
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
