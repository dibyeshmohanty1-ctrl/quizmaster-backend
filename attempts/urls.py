from django.urls import path

from .views import (
    StartQuizView,
    SubmitQuizView,
    AttemptResultView,
    AttemptHistoryView,
    AnswerReviewView,
    AdminAttemptListView,
    AdminAttemptDetailView,
)


urlpatterns = [

    path(
        "quizzes/<int:quiz_id>/start/",
        StartQuizView.as_view(),
        name="start-quiz",
    ),

    path(
        "attempts/<int:attempt_id>/submit/",
        SubmitQuizView.as_view(),
        name="submit-quiz",
    ),

    path(
        "attempts/<int:attempt_id>/result/",
        AttemptResultView.as_view(),
        name="attempt-result",
    ),

    path(
        "attempts/history/",
        AttemptHistoryView.as_view(),
        name="attempt-history",
    ),

    path(
        "attempts/<int:attempt_id>/review/",
        AnswerReviewView.as_view(),
        name="answer-review",
    ),

    path(
        "admin/attempts/",
        AdminAttemptListView.as_view(),
        name="admin-attempt-list",
    ),

    path(
        "admin/attempts/<int:attempt_id>/",
        AdminAttemptDetailView.as_view(),
        name="admin-attempt-detail",
    ),
]