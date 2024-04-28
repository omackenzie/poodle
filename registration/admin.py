from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group

from .models import Class, User

# Adds the "is teacher" field to the form to add a new user
ADDITIONAL_USER_FIELDS = (
    (None, {'fields': ('is_teacher',)}),
)


# Customises the user creation form in the admin panel
class CustomUserAdmin(UserAdmin):
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('first_name', 'last_name', 'username', 'password1', 'password2', 'is_teacher'),
        }),
    )

    
    fieldsets = UserAdmin.fieldsets + ADDITIONAL_USER_FIELDS


# Register the models to the admin panel
admin.site.register(Class)
admin.site.register(User, CustomUserAdmin)

# Unregister the Group model as it isn't necessary for this project
admin.site.unregister(Group)
