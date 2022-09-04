from django.test import TestCase


class LoginTest(TestCase):
    """Tests the functionality of the login system"""

    def test_login_redirect_if_not_authenticated(self):
        response = self.client.get('', follow=True)
        self.assertRedirects(response, '/accounts/login/?next=/assignments/home/')
