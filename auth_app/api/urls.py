from django.urls import path


from auth_app.api.views import RegisterView, EmailLoginView, LogoutView, email_check



urlpatterns = [
    path('registration/', RegisterView.as_view(), name='registration'),
    path('login/', EmailLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('email-check/', email_check, name='email-check'),
]

"""
URL configuration for the authentication API.

This module defines all authentication-related endpoints, including:

Endpoints:
    POST /registration/   - Register a new user account
    POST /login/          - Login using email + password
    POST /logout/         - Logout and delete auth token
    GET  /email-check/    - Check whether an email is already registered

These endpoints are used by the frontend for user onboarding and session
management.
"""