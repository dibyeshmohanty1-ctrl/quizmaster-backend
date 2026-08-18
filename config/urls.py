from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from dashboard.views import LeaderboardView

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)


urlpatterns = [

    path(
        "admin/",
        admin.site.urls
    ),

    # Authentication
    path(
        "api/auth/",
        include("accounts.urls")
    ),

    # JWT Login
    path(
        "api/auth/login/",
        TokenObtainPairView.as_view(),
        name="token-obtain-pair",
    ),

    # JWT Refresh
    path(
        "api/auth/refresh/",
        TokenRefreshView.as_view(),
        name="token-refresh",
    ),

    # Quiz Attempts
    path(
        "api/",
        include("attempts.urls"),
    ),

    # Quizzes
    path(
        "api/quizzes/",
        include("quizzes.urls"),
    ),

    # Questions
    path(
        "api/",
        include("questions.urls"),
    ),

    # Dashboard
    path(
        "api/dashboard/",
        include("dashboard.urls"),
    ),

    # Leaderboard
    path(
        "api/leaderboard/",
        LeaderboardView.as_view(),
        name="leaderboard",
    ),
]


if settings.DEBUG:

    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )