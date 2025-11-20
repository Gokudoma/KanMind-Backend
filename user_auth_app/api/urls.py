from django.urls import path

from .views import CustomAuthToken, EmailCheckView, UserRegistrationView

urlpatterns = [
    path('registration/', UserRegistrationView.as_view(), name='registration'),
    path('login/', CustomAuthToken.as_view(), name='login'),
    path('email-check/', EmailCheckView.as_view(), name='email-check'),
]