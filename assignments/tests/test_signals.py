
import os

from django.core.files import File
from django.test import Client, TestCase

from assignments.models import Assignment, Section, Submission
from registration.models import Class, User


class DeleteSubmissionTestCase(TestCase):
    """Tests that files are handled correctly when deleted"""

    def setUp(self):
        self.client = Client()

        self.user = User.objects.create_user(username='test', password='password', email='test@poodle.com')
        temp_class = Class.objects.create(name='temp', teacher=self.user, graphic='')
        temp_assignment = Assignment.objects.create(name='temp', details='', assigned_class=temp_class)
        temp_section = Section.objects.create(title='temp', total_marks=0, assignment=temp_assignment)
        with open('assignments/urls.py', 'r') as f:
             self.uploaded_file = Submission.objects.create(document=File(f), section=temp_section, user=self.user)

    def test_delete_submission(self):
        self.client.force_login(self.user)

        # Ensure files are actually deleted when an assignment is deleted
        self.client.delete(f'/assignments/{self.uploaded_file.id}/delete_file/')
        self.assertFalse(os.path.exists(os.path.realpath(self.uploaded_file.document.url[1:])))
