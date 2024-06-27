from ddf import G
from django.contrib.auth.forms import PasswordChangeForm
from django.test import Client, TestCase
from django.urls import reverse

from ..models import User


class SettingsTestCase(TestCase):
    def test_settings(self):
        self.client.force_login(G(User))
        response = self.client.get(reverse('settings'))

        self.assertTemplateUsed(response, 'registration/settings.html')


class ChangePasswordTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='test', password='password')

    def test_change_password__get_request(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('change_password'))

        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context['form'], PasswordChangeForm)

    def test_change_password__post_valid(self):
        self.client.login(username='test', password='password')
        self.client.post(
            reverse('change_password'),
            {'old_password': 'password', 'new_password1': 'newpa$$word', 'new_password2': 'newpa$$word'}
        )

        # Verify the password was changed
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('newpa$$word'))


    def test_change_password__post_invalid(self):
        self.client.login(username='test', password='password')
        response = self.client.post(
            reverse('change_password'),
            {'old_password': 'password', 'new_password1': 'newpa$$word', 'new_password2': 'wrong'}
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['form'].is_valid())

        # Verify the password was not changed
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('password'))
