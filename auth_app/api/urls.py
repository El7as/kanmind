from django.urls import path


from auth_app.api.views import RegisterView, EmailLoginView, LogoutView, email_check



urlpatterns = [
    path('registration/', RegisterView.as_view(), name='registration'),
    path('login/', EmailLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('email-check/', email_check, name='email-check'),
]