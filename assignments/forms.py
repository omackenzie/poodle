from django.forms import ModelChoiceField, ModelForm

from registration.models import Class

from .models import Assignment, Section, Submission


class SubmissionForm(ModelForm):
    class Meta:
        model = Submission
        fields = '__all__'


class AssignmentCreationForm(ModelForm):
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super(AssignmentCreationForm, self).__init__(*args, **kwargs)
        self.fields['assigned_class'] = ModelChoiceField(queryset=Class.objects.filter(teacher=user))

    class Meta:
        model = Assignment
        fields = '__all__'


class SectionForm(ModelForm):
    class Meta:
        model = Section
        fields = '__all__'
