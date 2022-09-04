import os
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from .models import Submission


@receiver(pre_delete, sender=Submission)
def delete_submission(sender, instance, **kwargs):
    # When a submission object is deleted, the file is physically deleted too
    os.remove(instance.document.path)
