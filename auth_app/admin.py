from django.contrib import admin
from django.contrib.auth import get_user_model

# Register your models here.

User = get_user_model()

admin.site.register(User)

"""
    Admin configuration for the custom User model.

    Provides:
        - Basic user management in the Django admin interface.
        - Displays email and name fields.
        - Allows searching by email, first name, and last name.

    Notes:
        - Since username is removed, email is the primary identifier.
    """