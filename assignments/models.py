import os
from datetime import datetime

from django.db import models

from registration.models import Class, User


class Assignment(models.Model):
    # Assignment model

    name = models.CharField(max_length=50)
    details = models.TextField(blank=True, null=True)
    due_date = models.DateTimeField(blank=True, null=True)
    creation_date = models.DateTimeField(auto_now_add=True)
    assigned_class = models.ForeignKey(Class, on_delete=models.CASCADE)

    # Returns the time left until the assignment is due
    @property
    def time_remaining(self):
        delta = datetime.date(self.due_date) - datetime.now().date()
        if delta.days < 0:
            return 'overdue'
        elif delta.days == 0:
            return 'today'
        elif delta.days == 1:
            return 'in 1 day'
        elif delta.days == 7:
            return 'in 1 week'
        elif delta.days >= 7:
            return f'in {delta.days // 7} weeks'
        else:
            return f'in {delta.days} days'

    def __str__(self):
        return self.name


class Section(models.Model):
    # Section model

    title = models.CharField(max_length=100)
    total_marks = models.PositiveIntegerField()
    details = models.TextField(blank=True, null=True)
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.assignment} - {self.title}'


class Submission(models.Model):
    # Submission model

    document = models.FileField(upload_to='submissions', blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    section = models.ForeignKey(Section, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    # Returns the path of the submission file
    @property
    def file_path(self):
        return self.document.name.split('/')[-1]

    # Returns the type of icon that should be used depending on the extension
    @property
    def file_image(self):
        _, extension = os.path.splitext(self.document.name)
        if extension == '.pdf':
            return 'file-pdf'
        elif extension in ['.png', '.jpg', '.gif', '.bmp']:
            return 'file-image'
        else:
            return 'file-lines'
    
    def __str__(self):
        return f'{self.section.assignment} - {self.file_path} ({self.user.first_name} {self.user.last_name})'
