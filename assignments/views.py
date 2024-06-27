from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.core.files.storage import FileSystemStorage
from django.http import FileResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods
from django.views.generic.edit import DeleteView

from registration.models import Class, User

from .forms import AssignmentCreationForm, SectionForm
from .models import Assignment, Section, Submission


@login_required
def home(request):
    # Renders the home page

    # If the user is a teacher, return the classes they teach
    # If the user is a student, return the classes they are a part of
    if request.user.is_teacher:
        user_classes = Class.objects.filter(teacher=request.user)
    else:
        user_classes = Class.objects.filter(users=request.user)

    # Get the assignments for each class the user is part of
    assignments = Assignment.objects.all()
    user_assignments = []
    for assignment in assignments:
        if assignment.assigned_class in user_classes:
            user_assignments.append(assignment)

    sort_by = request.GET.get('sort_by', 'due_date')

    return render(request, 'assignments/home.html', {'assignments': user_assignments, 'sort_by': sort_by})


@login_required
def details(request, id):
    # Renders the details of the assignment after it's clicked

    assignment = get_object_or_404(Assignment, pk=id)
        
    # If the user is the class teacher, include the form to add a section
    if request.user == assignment.assigned_class.teacher:
        add_section_form = SectionForm(prefix='add')
        edit_section_form = SectionForm(prefix='edit')
        return render(
            request,
            'assignments/details.html',
            {
                'assignment': assignment,
                'add_section_form': add_section_form,
                'edit_section_form': edit_section_form
            }
        )
    # Check that user is part of the class
    if request.user in assignment.assigned_class.users.all():
        return render(request, 'assignments/details.html', {'assignment': assignment})
    else:
        # Deny access if the user isn't part of the class
        raise PermissionDenied()


@require_http_methods(['POST'])
@login_required
def upload_files(request, id):
    # Controls when a file is submitted

    assignment = get_object_or_404(Assignment, pk=id)

    # User must be part of the class
    if request.user not in assignment.assigned_class.users.all():
        raise PermissionDenied()

    # Goes through all the submitted files, creates the required objects and saves the files
    fs = FileSystemStorage()
    for i in range(len(assignment.section_set.all())):
        if f'document{i}' in request.FILES:
            for file in request.FILES.getlist(f'document{i}'):
                saved = fs.save(f'submissions/{file.name}', file)
                Submission.objects.create(document=saved, section=assignment.section_set.all()[i], user=request.user)

    # Redirect back to the details page
    return redirect('details', id=assignment.pk)


@require_http_methods(['POST'])
@login_required
def create_section(request, id):
    # Creates a new section for the assignment

    assignment = get_object_or_404(Assignment, pk=id)

    # Deny access if the user isn't the class teacher
    if assignment.assigned_class.teacher != request.user:
        raise PermissionDenied()
    else:
        updated_request = request.POST.copy()
        updated_request.update({'add-assignment': assignment.pk })
        form = SectionForm(updated_request, prefix='add')
        if form.is_valid():
            form.save()
            
        # Return to the assignment details page when a section is added
        return redirect(f'/assignments/{assignment.pk}/details')


@require_http_methods(['POST'])
@login_required
def edit_section(request):
    # Modifies a preexisting section

    section = get_object_or_404(Section, pk=request.POST['section_id'])
    assignment = section.assignment

    # Deny access if the user isn't the class teacher
    if section.assignment.assigned_class.teacher != request.user:
        raise PermissionDenied()
    else:
        updated_request = request.POST.copy()
        updated_request.update({'edit-assignment': assignment.pk })
        form = SectionForm(updated_request, instance=section, prefix='edit')
        if form.is_valid():
            form.save()

        # Return to the assignment details page when the section is changed
        return redirect(f'/assignments/{section.assignment.pk}/details')


@login_required
def download(request, submission_id):
    # Downloads the file when it is clicked

    submission = get_object_or_404(Submission, pk=submission_id)

    # Only allow teachers or the student themself to download to file
    if request.user.is_teacher or request.user == submission.user:
        filename = submission.document.path
        # Returns the raw file data, which allows it to be opened/downloaded
        response = FileResponse(open(filename, 'rb'))
        return response
    else:
        raise PermissionDenied()


class DeleteFileView(UserPassesTestMixin, DeleteView):
    model = Submission

    def test_func(self):
        obj = self.get_object()
        # User must be the owner to delete it
        return obj.user == self.request.user

    def get_success_url(self):
        next_url = self.request.GET.get('next')
        if next_url:
            return next_url # return next url for redirection
        return '/'


class DeleteSectionView(UserPassesTestMixin, DeleteView):
    model = Section

    def test_func(self):
        obj = self.get_object()
        # User must be teacher of the class to delete the section
        return obj.assignment.assigned_class.teacher == self.request.user       

    def get_success_url(self):
        next_url = self.request.GET.get('next')
        if next_url:
            return next_url # return next url for redirection
        return '/'


class DeleteAssignmentView(UserPassesTestMixin, DeleteView):
    model = Assignment
    success_url = '/'
    
    def test_func(self):
        obj = self.get_object()
        # User must be teacher of the class to delete the assignment
        return obj.assigned_class.teacher == self.request.user


def create_assignment(request):
    if request.user.is_teacher:
        # For submission handling
        if request.method == 'POST':
            form = AssignmentCreationForm(request.POST, user=request.user)
            if form.is_valid():
                assignment = form.save()
                # Redirect to the assignment details page when it is created
                return redirect(f'/assignments/{assignment.pk}/details')
            # If the form is invalid, return to the creation page
            return render(request, 'assignments/create_assignment.html', {'form': form})
            
        else:
            # Create a new form
            form = AssignmentCreationForm(user=request.user)
            return render(request, 'assignments/create_assignment.html', {'form': form})
    else:
        # Only allow teachers to create assignments
        raise PermissionDenied()


@login_required
def view_submissions(request, id):
    # View all submissions for a given assignment

    assignment = get_object_or_404(Assignment, pk=id)

    if assignment.assigned_class.teacher != request.user:
        # Deny access if the user is not the class teacher
        raise PermissionDenied()
    else:
        user_id = request.GET.get('user_id', assignment.assigned_class.users.all()[0].pk)

        # Gets the submissions for each user
        user = get_object_or_404(User, pk=user_id)
        sections = assignment.section_set.all()
        user_submissions = Submission.objects.filter(
            section__in=sections, user=user
        )

        return render(
            request,
            'assignments/view_submissions.html',
            {
                'assignment': assignment,
                'selected_student': user,
                'user_submissions': user_submissions
            }
        )


def help(request):
    return render(request, 'assignments/help.html')
