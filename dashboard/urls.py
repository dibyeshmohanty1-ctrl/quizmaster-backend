from django.urls import path

from .views import (
    StudentDashboardView,
    AdminAnalyticsView,
    LeaderboardView,
)


urlpatterns = [

    path(
        "student/",
        StudentDashboardView.as_view(),
        name="student-dashboard",
    ),

    path(
        "admin/analytics/",
        AdminAnalyticsView.as_view(),
        name="admin-analytics",
    ),

    path(
        "api/leaderboard/",
        LeaderboardView.as_view(),
        name="leaderboard",
    ),
]