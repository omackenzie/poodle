import os
from unittest.mock import mock_open, patch

from ddf import G
from django.http import FileResponse
from django.test import Client, TestCase
from django.urls import reverse

from assignments.models import Assignment, Class, Section, Submission
from registration.models import User


class HomeViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()

        # Users
        self.teacher_user = G(User, is_teacher=True)
        self.student_user = G(User, is_teacher=False)

        # Classes
        self.class_teacher = G(Class, name='Math', teacher=self.teacher_user)
        self.class_student = G(Class, name='Science')
        self.class_student.users.add(self.student_user)

        # Assignments
        self.assignment_teacher = G(Assignment, name='Math Assignment', assigned_class=self.class_teacher)
        self.assignment_student = G(Assignment, name='Science Assignment', assigned_class=self.class_student)

    def test_as_teacher(self):
        # Log in as teacher
        self.client.force_login(self.teacher_user)
        response = self.client.get(reverse('home'))

        self.assertEqual(response.status_code, 200)
        self.assertCountEqual(response.context['assignments'], [self.assignment_teacher])
        self.assertEqual(response.context['sort_by'], 'due_date')

    def test_as_student(self):
        # Log in as student
        self.client.force_login(self.student_user)
        response = self.client.get(reverse('home'))

        self.assertEqual(response.status_code, 200)
        self.assertCountEqual(response.context['assignments'], [self.assignment_student])
        self.assertEqual(response.context['sort_by'], 'due_date')

    def test_sort_by(self):
        self.client.force_login(self.teacher_user)
        response = self.client.get(reverse('home') + '?sort_by=title')

        self.assertEqual(response.status_code, 200)
        self.assertIn('sort_by', response.context)
        self.assertEqual(response.context['sort_by'], 'title')


class DetailsViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()

        # Users
        self.teacher_user = G(User, is_teacher=True)
        self.student_user = G(User, is_teacher=False)

        # Classes
        self.class_teacher = G(Class, name='Math', teacher=self.teacher_user)
        self.class_teacher.users.add(self.student_user)

        # Assignments
        self.assignment = G(Assignment, name='Math Assignment', assigned_class=self.class_teacher)

    def test_as_teacher(self):
        # Log in as teacher
        self.client.force_login(self.teacher_user)
        response = self.client.get(reverse('details', args=[self.assignment.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertIn('add_section_form', response.context)
        self.assertIn('edit_section_form', response.context)

    def test_as_student(self):
        # Log in as student
        self.client.force_login(self.student_user)
        response = self.client.get(reverse('details', args=[self.assignment.pk]))
        self.assertEqual(response.status_code, 200)

    def test_non_class_member(self):
        # Create a user who is not part of the class
        non_member_user = User.objects.create_user(username='non_member', password='password')
        self.client.force_login(non_member_user)
        
        response = self.client.get(reverse('details', args=[self.assignment.pk]))
        self.assertEqual(response.status_code, 403)


class UploadFilesViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.created_files = ['test_file.txt']

        # Users
        self.user = G(User, is_teacher=False)

        # Classes
        self.test_class = G(Class)
        self.test_class.users.add(self.user)

        # Assignment for the class
        self.assignment = G(Assignment, assigned_class=self.test_class)

        # Assignment sections
        self.section1 = G(Section, assignment=self.assignment)
        self.section2 = G(Section, assignment=self.assignment)

    def test_upload_files(self):
        self.client.force_login(self.user)

        # Create a file to upload
        with open('test_file.txt', 'w') as f:
            f.write('Test file content')

        with open('test_file.txt', 'rb') as f:
            response = self.client.post(reverse('upload', kwargs={'id': self.assignment.pk}),
                             {'document0': f})

        # Redirected to the details page
        self.assertEqual(response.status_code, 302)

        # Check if submission is created
        submission = Submission.objects.filter(section=self.section1, user=self.user).first()
        self.assertIsNotNone(submission)

        self.created_files.append(submission.document.path)

    def test_upload_files__permission_denied(self):
        # Create a user who is not part of the class
        non_member = G(User, is_teacher=False)
        self.client.force_login(non_member)

        response = self.client.post(reverse('upload', kwargs={'id': self.assignment.pk}))
        self.assertEqual(response.status_code, 403)
    
    def tearDown(self):
        # Clean up the files created for tests
        for file in self.created_files:
            if os.path.exists(file):
                os.remove(file)


class CreateSectionTestCase(TestCase):
    def setUp(self):
        self.client = Client()

        # Users
        self.teacher_user = G(User, is_teacher=True)

        # Classes
        self.test_class = G(Class, teacher=self.teacher_user)

        # Assignment for the class
        self.assignment = G(Assignment, assigned_class=self.test_class)

    def test_create_section(self):
        self.client.force_login(self.teacher_user)

        response = self.client.post(
            reverse(
                'create_section', kwargs={'id': self.assignment.pk}
            ),
            {
                'add-title': 'Section 1',
                'add-total_marks': 10,
                'add-details': 'Section 1 details'
            }
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Section.objects.count(), 1)
        
        section = Section.objects.get(title='Section 1')
        self.assertEqual(section.title, 'Section 1')
        self.assertEqual(section.total_marks, 10)
        self.assertEqual(section.details, 'Section 1 details')

    def test_create_section__not_class_teacher(self):
        # Another teacher who doesn't teach this class
        different_teacher = G(User, is_teacher=True)
        self.client.force_login(different_teacher)

        response = self.client.post(reverse('create_section', kwargs={'id': self.assignment.pk}),
                                    {'add-title': 'Section 1', 'add-total_marks': 10})

        self.assertEqual(response.status_code, 403)
    
    def test_create_section__invalid_form(self):
        self.client.force_login(self.teacher_user)

        response = self.client.post(
            reverse(
                'create_section', kwargs={'id': self.assignment.pk}
            ),
            {
                'add-total_marks': '10',
                'add-details': 'Section 1 details'
            }
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Section.objects.count(), 0)


class EditSectionTestCase(TestCase):
    def setUp(self):
        self.client = Client()

        # Users
        self.teacher_user = G(User, is_teacher=True)

        # Classes
        self.test_class = G(Class, teacher=self.teacher_user)

        # Assignment for the class
        self.assignment = G(Assignment, assigned_class=self.test_class)

    def test_edit_section(self):
        section = G(
            Section,
            assignment=self.assignment,
            title='Section 0'
        )

        self.client.force_login(self.teacher_user)

        response = self.client.post(
            reverse('edit_section'),
            {
                'section_id': section.pk,
                'edit-title': 'Section 1',
                'edit-total_marks': 10,
                'edit-details': 'Section 1 details'
            }
        )

        self.assertEqual(response.status_code, 302)
        section.refresh_from_db()
        self.assertEqual(section.title, 'Section 1')
        self.assertEqual(section.total_marks, 10)
        self.assertEqual(section.details, 'Section 1 details')

    def test_edit_section__not_class_teacher(self):
        section = G(Section, assignment=self.assignment, title='Section 0')

        # Another teacher who doesn't teach this class
        different_teacher = G(User, is_teacher=True)
        self.client.force_login(different_teacher)

        response = self.client.post(
            reverse('edit_section'),
            {'section_id': section.pk, 'edit-title': 'Section 1', 'edit-total_marks': 10}
        )

        self.assertEqual(response.status_code, 403)
        section.refresh_from_db()
        self.assertEqual(section.title, 'Section 0')

    def test_edit_section__invalid_form(self):
        section = G(Section, assignment=self.assignment, total_marks=5)

        self.client.force_login(self.teacher_user)

        response = self.client.post(
            reverse('edit_section'),
            {
                'section_id': section.pk,
                'edit-total_marks': 10,
                'edit-details': 'Section 1 details'
            }
        )

        self.assertEqual(response.status_code, 302)
        section.refresh_from_db()
        self.assertEqual(section.total_marks, 5)


class DownloadTestCase(TestCase):
    def setUp(self):
        self.client = Client()

        # Users
        self.teacher_user = G(User, is_teacher=True)
        self.student_user = G(User, is_teacher=False)

        # Classes
        self.test_class = G(Class, teacher=self.teacher_user)

        # Assignment for the class
        self.assignment = G(Assignment, assigned_class=self.test_class)

        # Assignment section
        self.section = G(Section, assignment=self.assignment)

        # Submission
        self.submission = G(Submission, section=self.section, user=self.student_user)

    def test_download__teacher(self):
        self.client.force_login(self.teacher_user)

        with patch('builtins.open', mock_open(read_data=b'Test file content')) as mock_file:
            response = self.client.get(reverse('download', kwargs={'submission_id': self.submission.pk}))
            mock_file.assert_called_with(self.submission.document.path, 'rb')
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue(isinstance(response, FileResponse))

    def test_download__student(self):
        self.client.force_login(self.student_user)

        with patch('builtins.open', mock_open(read_data=b'Test file content')) as mock_file:
            response = self.client.get(reverse('download', kwargs={'submission_id': self.submission.pk}))
            mock_file.assert_called_with(self.submission.document.path, 'rb')
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue(isinstance(response, FileResponse))

    def test_download__different_student(self):
        # Student who did not create the submission
        different_student = G(User, is_teacher=False)
        self.client.force_login(different_student)

        response = self.client.get(reverse('download', kwargs={'submission_id': self.submission.pk}))
        self.assertEqual(response.status_code, 403)


class DeleteFileViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()

        # Users
        self.teacher_user = G(User, is_teacher=True)
        self.student_user = G(User, is_teacher=False)

        # Classes
        self.test_class = G(Class, teacher=self.teacher_user)

        # Assignment for the class
        self.assignment = G(Assignment, assigned_class=self.test_class)

        # Assignment section
        self.section = G(Section, assignment=self.assignment)

        # Submission
        self.submission = G(Submission, section=self.section, user=self.student_user)

    def test_delete_file(self):
        self.client.force_login(self.student_user)

        with patch('assignments.signals.os.remove') as mock_remove:
            response = self.client.post(reverse('delete_file', kwargs={'pk': self.submission.pk}))
            mock_remove.assert_called_with(self.submission.document.path)

        self.assertRedirects(response, '/', target_status_code=302)
        self.assertFalse(Submission.objects.filter(pk=self.submission.pk).exists())

    def test_delete_file__next_url(self):
        self.client.force_login(self.student_user)

        next_url = '/assignments/help/'
        with patch('assignments.signals.os.remove') as mock_remove:
            response = self.client.post(reverse('delete_file', kwargs={'pk': self.submission.pk}) + f'?next={next_url}')
            mock_remove.assert_called_once()
        self.assertRedirects(response, next_url)

    def test_delete_file__different_student(self):
        # Student who did not create the submission
        different_student = G(User, is_teacher=False)
        self.client.force_login(different_student)

        response = self.client.post(reverse('delete_file', kwargs={'pk': self.submission.pk}))
        self.assertEqual(response.status_code, 403)


class DeleteSectionViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()

        # Users
        self.teacher_user = G(User, is_teacher=True)

        # Classes
        self.test_class = G(Class, teacher=self.teacher_user)

        # Assignment for the class
        self.assignment = G(Assignment, assigned_class=self.test_class)

        # Assignment section
        self.section = G(Section, assignment=self.assignment)

    def test_delete_section(self):
        self.client.force_login(self.teacher_user)

        response = self.client.post(reverse('delete_section', kwargs={'pk': self.section.pk}))
        self.assertRedirects(response, '/', target_status_code=302)

        self.assertFalse(Section.objects.filter(pk=self.section.pk).exists())

    def test_delete_section__next_url(self):
        self.client.force_login(self.teacher_user)

        next_url = '/assignments/help/'
        response = self.client.post(reverse('delete_section', kwargs={'pk': self.section.pk}) + f'?next={next_url}')
        self.assertRedirects(response, next_url)

    def test_delete_section__not_class_teacher(self):
        # Another teacher who doesn't teach this class
        different_teacher = G(User, is_teacher=True)
        self.client.force_login(different_teacher)

        response = self.client.post(reverse('delete_section', kwargs={'pk': self.section.pk}))
        self.assertEqual(response.status_code, 403)


class DeleteAssignmentViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()

        # Users
        self.teacher_user = G(User, is_teacher=True)

        # Classes
        self.test_class = G(Class, teacher=self.teacher_user)

        # Assignment for the class
        self.assignment = G(Assignment, assigned_class=self.test_class)

    def test_delete_assignment(self):
        self.client.force_login(self.teacher_user)

        response = self.client.post(reverse('delete_assignment', kwargs={'pk': self.assignment.pk}))
        self.assertRedirects(response, '/', target_status_code=302)

        self.assertFalse(Assignment.objects.filter(pk=self.assignment.pk).exists())

    def test_delete_assignment__not_class_teacher(self):
        # Another teacher who doesn't teach this class
        different_teacher = G(User, is_teacher=True)
        self.client.force_login(different_teacher)

        response = self.client.post(reverse('delete_assignment', kwargs={'pk': self.assignment.pk}))
        self.assertEqual(response.status_code, 403)


class CreateAssignmentTestCase(TestCase):
    def setUp(self):
        self.client = Client()

        # Users
        self.teacher_user = G(User, is_teacher=True)

        # Classes
        self.test_class = G(Class, teacher=self.teacher_user)

    def test_create_assignment__get(self):
        self.client.force_login(self.teacher_user)

        response = self.client.get(reverse('create_assignment'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)

    def test_create_assignment__student(self):
        self.client.force_login(G(User, is_teacher=False))

        response = self.client.get(reverse('create_assignment'))
        self.assertEqual(response.status_code, 403)

    def test_create_assignment__post(self):
        self.client.force_login(self.teacher_user)

        response = self.client.post(
            reverse('create_assignment'),
            {
                'name': 'Math Assignment',
                'assigned_class': self.test_class.pk
            }
        )

        self.assertTrue(Assignment.objects.filter(name='Math Assignment').exists())
        assignment = Assignment.objects.get(name='Math Assignment')
        self.assertRedirects(
            response,
            f'/assignments/{assignment.pk}/details',
            target_status_code=302,
            fetch_redirect_response=False
        )

    def test_create_assignment__invalid_form(self):
        self.client.force_login(self.teacher_user)

        response = self.client.post(
            reverse('create_assignment'),
            {
                'assigned_class': self.test_class.pk
            }
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)
        self.assertEqual(Assignment.objects.count(), 0)


class ViewSubmissionsTestCase(TestCase):
    def setUp(self):
        self.client = Client()

        # Users
        self.teacher_user = G(User, is_teacher=True)
        self.student1 = G(User, is_teacher=False)
        self.student2 = G(User, is_teacher=False)

        # Classes
        self.test_class = G(Class, teacher=self.teacher_user)
        self.test_class.users.add(self.student1, self.student2)

        # Assignment for the class
        self.assignment = G(Assignment, assigned_class=self.test_class)

        # Assignment section
        self.section = G(Section, assignment=self.assignment)

        # Submissions
        self.submission1 = G(Submission, section=self.section, user=self.student1)
        self.submission2 = G(Submission, section=self.section, user=self.student1)
        self.submission3 = G(Submission, section=self.section, user=self.student2)

    def test_view_submissions__not_class_teacher(self):
        other_teacher = G(User, is_teacher=True)
        self.client.force_login(other_teacher)

        response = self.client.get(
            reverse('view_submissions', args=[self.assignment.pk])
        )
        self.assertEqual(response.status_code, 403)

    def test_view_submissions__no_student_specified(self):
        self.client.force_login(self.teacher_user)

        response = self.client.get(
            reverse('view_submissions', args=[self.assignment.pk])
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['assignment'], self.assignment)
        self.assertEqual(response.context['selected_student'], self.student1)
        self.assertCountEqual(
            response.context['user_submissions'],
            [self.submission1, self.submission2]
        )

    def test_view_submissions__student_specified(self):
        self.client.force_login(self.teacher_user)

        response = self.client.get(
            reverse('view_submissions', args=[self.assignment.pk]),
            {'user_id': self.student2.pk}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['assignment'], self.assignment)
        self.assertEqual(response.context['selected_student'], self.student2)
        self.assertCountEqual(response.context['user_submissions'], [self.submission3])


class HelpTestCase(TestCase):
    def test_help(self):
        response = self.client.get(reverse('help'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('assignments/help.html')
