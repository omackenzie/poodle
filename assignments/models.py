import os

from django.db import models
from django.utils import timezone

from registration.models import Class, User


class Assignment(models.Model):
    name = models.CharField(max_length=50)
    details = models.TextField(blank=True, null=True)
    due_date = models.DateTimeField(blank=True, null=True)
    creation_date = models.DateTimeField(auto_now_add=True)
    assigned_class = models.ForeignKey(Class, on_delete=models.CASCADE)

    # Returns the time left until the assignment is due
    @property
    def time_remaining(self):
        if not self.due_date:
            return 'no due date'

        delta = self.due_date - timezone.now()
        if delta.days < 0:
            return 'overdue'
        elif delta.days == 0:
            return 'today'
        elif delta.days == 1:
            return 'in 1 day'
        elif 7 <= delta.days < 14:
            return 'in 1 week'
        elif delta.days >= 7:
            return f'in {delta.days // 7} weeks'
        else:
            return f'in {delta.days} days'

    def __str__(self):
        return self.name


class Section(models.Model):
    title = models.CharField(max_length=100)
    total_marks = models.PositiveIntegerField()
    details = models.TextField(blank=True, null=True)
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.assignment} - {self.title}'


class Submission(models.Model):
    document = models.FileField(upload_to='submissions')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    section = models.ForeignKey(Section, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    @property
    def document_path(self):
        return self.document.name

    # Returns the path of the submission file
    @property
    def filename(self):
        return os.path.basename(self.document_path)

    # Returns the type of icon that should be used depending on the extension
    @property
    def file_image(self):
        _, extension = os.path.splitext(self.document_path)
        if extension == '.pdf':
            return 'file-pdf'
        elif extension in ['.png', '.jpg', '.gif', '.bmp']:
            return 'file-image'
        else:
            return 'file-lines'

    def __str__(self):
        return f'{self.section.assignment} - {self.filename} ({self.user.first_name} {self.user.last_name})'
