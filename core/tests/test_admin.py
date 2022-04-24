from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse


class AdminSites(TestCase):

    def setUp(self):
        self.client = Client()
        self.admin_user = get_user_model().objects.create_superuser(
            email='admin@admin.com',
            password='admin123'
        )
        self.client.force_login(self.admin_user)
        self.user = get_user_model().objects.create_user(
            email='edward@caslte.com',
            password='test123',
            name='Testing user'
        )

    def test_users_list(self):
        """ Test that all the user have been listed in user page """

        url = reverse('admin:core_user_changelist')
        response = self.client.get(url)

        self.assertContains(response, self.user.name)
        self.assertContains(response, self.user.email)

    def test_user_change_page(self):
        """ Test user edit page """

        url = reverse('admin:core_user_change', args=[self.user.id])  # admin/core/user/1
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)