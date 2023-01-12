import os
from django.test import TestCase
from django.core.files import File
from registration.models import User, Class
from .models import Assignment, Section, Submission


class FileTest(TestCase):
    """Tests that files are handled correctly"""

    def setUp(self):
        user = User.objects.create_user(username='test', password='password', email='test@poodle.com')
        temp_class = Class.objects.create(name='temp', teacher=user, graphic='')
        temp_assignment = Assignment.objects.create(name='temp', details='', assigned_class=temp_class)
        temp_section = Section.objects.create(title='temp', total_marks=0, assignment=temp_assignment)
        with open('assignments/urls.py', 'r') as f:
             self.uploaded_file = Submission.objects.create(document=File(f), section=temp_section, user=user)

    def test_delete_file(self):
        # Ensure files are actually deleted when an assignment is deleted
        self.client.delete(f'/assignments/{self.uploaded_file.id}/delete_file/')
        self.assertFalse(os.path.exists(os.path.realpath(self.uploaded_file.document.url[1:])))
        