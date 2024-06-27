from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.shortcuts import redirect, render


@login_required
def settings(request):
    # Renders the profile page
    return render(request, 'registration/settings.html')


@login_required
def change_password(request):
    # Changes the user's password at their request

    # If the request is a POST, save the form
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            # Update the session hash so the user stays signed in
            update_session_auth_hash(request, user)
            return redirect('index')
    # Give the password change form to the user
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'registration/change_password.html', {
        'form': form
    })
