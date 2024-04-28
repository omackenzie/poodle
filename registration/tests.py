from django.test import TestCase

from .models import User


class AuthTest(TestCase):
    """Tests the functionality of the authentication system"""

    def test_login_redirect_if_not_authenticated(self):
        response = self.client.get('', follow=True)
        self.assertRedirects(response, '/accounts/login/?next=/assignments/home/')
    
    def test_password_changes(self):
        User.objects.create_user(username='test', password='password', email='test@poodle.com')
        self.client.login(username='test', password='password')
        self.client.post('/accounts/change_password/', {'old_password': 'password', 'new_password1': 'newpa$$word', 'new_password2': 'newpa$$word'})
        self.client.logout()

        authenticated = self.client.login(username='test', password='newpa$$word')
        self.assertEqual(authenticated, True)
