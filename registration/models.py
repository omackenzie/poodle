from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    # Extends the base User model and adds a teacher field
    is_teacher = models.BooleanField(default=False)


class Class(models.Model):
    # Class model

    name = models.CharField(max_length=50)
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name='teaching_classes')
    graphic = models.ImageField(upload_to='course_images')
    users = models.ManyToManyField(User, related_name='classes')

    def __str__(self):
        return self.name

    class Meta:
        # Uses the plural form of 'classes', rather than what Django sets by default (classs)
        verbose_name_plural = 'classes'
