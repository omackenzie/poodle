from django.views.generic.edit import DeleteView
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import AccessMixin
from django.core.exceptions import PermissionDenied
from django.http import FileResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.core.files.storage import FileSystemStorage
from registration.models import Class, User
from .models import Assignment, Section, Submission
from .forms import AssignmentCreationForm, SectionCreationForm


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
        section_form = SectionCreationForm()
        return render(request, 'assignments/details.html', {'assignment': assignment, 'section_form': section_form})
    # Check that user is part of the class
    if request.user in assignment.assigned_class.users.all():
        return render(request, 'assignments/details.html', {'assignment': assignment})
    else:
        # Deny access if the user isn't part of the class
        raise PermissionDenied()


# Only allow POST requests for this view
@require_http_methods(['POST'])
@login_required
def upload_files(request, id):
    # Controls when a file is submitted

    assignment = get_object_or_404(Assignment, pk=id)

    # Check that user is part of the class
    if request.user in assignment.assigned_class.users.all() or request.user.is_teacher:
        # Goes through all the submitted files, creates the required objects and saves the files
        fs = FileSystemStorage()
        for i in range(len(assignment.section_set.all())):
            if f'document{i}' in request.FILES:
                for file in request.FILES.getlist(f'document{i}'):
                    saved = fs.save(f'submissions/{file.name}', file)
                    Submission.objects.create(document=saved, section=assignment.section_set.all()[i], user=request.user)
    
    # Redirect back to the details page
    return redirect('details', id=assignment.pk)


# Only allow POST requests for this view
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
        updated_request.update({'assignment': assignment.pk })
        form = SectionCreationForm(updated_request)
        if form.is_valid():
            form.save()
            
        # Return to the assignment details page when a section is added
        return redirect(f'/assignments/{assignment.pk}/details')


# Only allow POST requests for this view
@require_http_methods(['POST'])
@login_required
def edit_section(request):
    # Modifies a preexisting section

    section = get_object_or_404(Section, pk=request.POST['section_id'])

    # Deny access if the user isn't the class teacher
    if section.assignment.assigned_class.teacher != request.user:
        raise PermissionDenied()
    else:
        section.title = request.POST['edit_title']
        section.total_marks = request.POST['edit_total_marks']
        section.details = request.POST['edit_details']
        section.save()

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


class DeleteFileView(DeleteView):
    # Django class-based view for deleting a submission
    model = Submission
    
    def get_context_data(self, **kwargs):
        context = super(DeleteFileView, self).get_context_data(**kwargs)
        # Pass 'next' parameter received from previous page to the context 
        context['next_url'] = self.request.GET.get('next')
        return context

    def get_success_url(self):
        next_url = self.request.GET.get('next')
        if next_url:
            return next_url # return next url for redirection
        return '/'


class DeleteSectionView(DeleteView):
    # Django class-based view for deleting a section
    model = Section

    def get_context_data(self, **kwargs):
        context = super(DeleteSectionView, self).get_context_data(**kwargs)
        # Pass 'next' parameter received from previous page to the context 
        context['next_url'] = self.request.GET.get('next')
        return context

    def get_success_url(self):
        next_url = self.request.GET.get('next')
        if next_url:
            return next_url # return next url for redirection
        return '/'


class DeleteAssignmentView(AccessMixin, DeleteView):
    # Django class-based for deleting an assignment
    model = Assignment
    success_url = '/'

    def dispatch(self, request, *args, **kwargs):
        assignment = self.get_object()
        if assignment.assigned_class.teacher != request.user:
            raise PermissionDenied()
        return super().dispatch(request, *args, **kwargs)


def create_assignment(request):
    # Creates a new assignment

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
    # View all submissions for that assignment

    assignment = get_object_or_404(Assignment, pk=id)

    if assignment.assigned_class.teacher != request.user:
        # Deny access if the user is not the class teacher
        raise PermissionDenied()
    else:
        user_id = request.GET.get('user_id', assignment.assigned_class.users.all()[0].pk)
        
        # Gets the submissions for each user
        user = get_object_or_404(User, pk=user_id)
        user_submissions = []
        for section in assignment.section_set.all():
            for submission in section.submission_set.all():
                if submission.user == user:
                    user_submissions.append(submission)

        return render(request, 'assignments/view_submissions.html', {'assignment': assignment, 'selected_student': user, 'user_submissions': user_submissions})


def help(request):
    # Renders the help page
    
    return render(request, 'assignments/help.html')
