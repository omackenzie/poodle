from django.contrib import admin
from .models import Assignment, Section, Submission


# Register the models to the admin panel
admin.site.register(Assignment)
admin.site.register(Section)
admin.site.register(Submission)
