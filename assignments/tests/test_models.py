from unittest.mock import PropertyMock, patch

from ddf import G
from django.test import TestCase
from django.utils import timezone

from assignments.models import Assignment, Section, Submission
from registration.models import User


class AssignmentTestCase(TestCase):
    """Tests for the Assignment model"""

    def setUp(self):
        # Set up method to patch now for all tests.
        self.mocked_now = timezone.datetime(2023, 2, 1, 11, 30, tzinfo=timezone.utc)
        self.now_patcher = patch('assignments.models.timezone.now', return_value=self.mocked_now)
        self.now_patcher.start()

    def tearDown(self):
        self.now_patcher.stop()

    def test_time_remaining__no_due_date(self):
        assignment = G(Assignment, due_date=None)
        self.assertEqual(assignment.time_remaining, 'no due date')
    
    def test_time_remaining__overdue(self):
        assignment = G(Assignment, due_date=timezone.datetime(2023, 2, 1, 11, 29, tzinfo=timezone.utc))
        self.assertEqual(assignment.time_remaining, 'overdue')

    def test_time_remaining__today(self):
        assignment = G(Assignment, due_date=timezone.datetime(2023, 2, 1, 11, 31, tzinfo=timezone.utc))
        self.assertEqual(assignment.time_remaining, 'today')

    def test_time_remaining__in_1_day(self):
        assignment = G(Assignment, due_date=timezone.datetime(2023, 2, 2, 13, 30, tzinfo=timezone.utc))
        self.assertEqual(assignment.time_remaining, 'in 1 day')

    def test_time_remaining__in_1_week(self):
        assignment = G(Assignment, due_date=timezone.datetime(2023, 2, 10, 11, 30, tzinfo=timezone.utc))
        self.assertEqual(assignment.time_remaining, 'in 1 week')

    def test_time_remaining__over_1_week(self):
        assignment = G(Assignment, due_date=timezone.datetime(2023, 3, 1, 11, 30, tzinfo=timezone.utc))
        self.assertEqual(assignment.time_remaining, 'in 4 weeks')

    def test_time_remaining__between_1_day_and_1_week(self):
        assignment = G(Assignment, due_date=timezone.datetime(2023, 2, 5, 11, 30, tzinfo=timezone.utc))
        self.assertEqual(assignment.time_remaining, 'in 4 days')


class SectionTestCase(TestCase):
    """Tests for the Section model"""

    def test_str(self):
        assignment = G(Assignment, name='Assignment 1')
        section = G(Section, title='Section 1', assignment=assignment)
        self.assertEqual(str(section), 'Assignment 1 - Section 1')


class SubmissionTestCase(TestCase):
    """Tests for the Submission model"""

    def test_filename(self):
        submission = G(Submission)
        with patch('assignments.models.Submission.document_path', new_callable=PropertyMock) as mock_document_path:
            mock_document_path.return_value = 'submission/test.pdf'
            self.assertEqual(submission.filename, 'test.pdf')

    def test_file_image__pdf(self):
        submission = G(Submission)
        with patch('assignments.models.Submission.document_path', new_callable=PropertyMock) as mock_document_path:
            mock_document_path.return_value = 'submission/test.pdf'
            self.assertEqual(submission.file_image, 'file-pdf')

    def test_file_image__img(self):
        submission = G(Submission)
        with patch('assignments.models.Submission.document_path', new_callable=PropertyMock) as mock_document_path:
            mock_document_path.return_value = 'submission/test.jpg'
            self.assertEqual(submission.file_image, 'file-image')

    def test_file_image__other(self):
        submission = G(Submission)
        with patch('assignments.models.Submission.document_path', new_callable=PropertyMock) as mock_document_path:
            mock_document_path.return_value = 'submission/test.docx'
            self.assertEqual(submission.file_image, 'file-lines')

    def test_str(self):
        assignment = G(Assignment, name='Assignment 1')
        section = G(Section, assignment=assignment)
        user = G(User, first_name='John', last_name='Doe')
        submission = G(Submission, section=section, user=user)
        
        with patch('assignments.models.Submission.document_path', new_callable=PropertyMock) as mock_document_path:
            mock_document_path.return_value = 'submission/test.pdf'

            self.assertEqual(str(submission), 'Assignment 1 - test.pdf (John Doe)')
