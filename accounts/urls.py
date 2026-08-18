from django.urls import path
from .views import RegisterView, CurrentUserView, AdminTestView
from .views import (
    RegisterView,
    CurrentUserView,
    AdminTestView,
    ForgotPasswordView,
    ResetPasswordView,
    LogoutView,
)
urlpatterns = [
    path(
        "register/",
        RegisterView.as_view(),
        name="register",
    ),
    path(
        "me/",
        CurrentUserView.as_view(),
        name="current-user",
    ),
    path(
        "admin-test/",
        AdminTestView.as_view(),
        name="admin-test",
    ),
        path(
        "forgot-password/",
        ForgotPasswordView.as_view(),
        name="forgot-password",
    ),

    path(   
        "reset-password/",
        ResetPasswordView.as_view(),
        name="reset-password",
    ),

    path(
        "logout/",
        LogoutView.as_view(),
        name="logout",
    ),
]