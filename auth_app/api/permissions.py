from rest_framework.permissions import BasePermission


class IsNotAuthenticated(BasePermission):

    def has_permission(self, request, view):
        return not request.user.is_authenticated
    
    """
    Permission that only allows access to users who are NOT authenticated.

    Use cases:
        - Registration endpoints
        - Login endpoints
        - Password reset requests
        - Public availability checks (e.g., email/username check)

    Behavior:
        - If the user is authenticated → permission is denied.
        - If the user is anonymous → permission is granted.

    Methods:
        has_permission(request, view):
            Returns True only when request.user.is_authenticated is False.
    """


