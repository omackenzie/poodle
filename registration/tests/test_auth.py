from django.test import TestCase


class AuthTestCase(TestCase):
    """Tests the functionality of the authentication system"""

    def test_login_redirect_if_not_authenticated(self):
        response = self.client.get('', follow=True)
        self.assertRedirects(response, '/accounts/login/?next=/assignments/home/')
