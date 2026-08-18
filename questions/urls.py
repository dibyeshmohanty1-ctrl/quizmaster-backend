from django.urls import path

from .views import (
    QuizQuestionListView,
    QuestionDetailView,
)


urlpatterns = [
    path(
        "quizzes/<int:quiz_id>/questions/",
        QuizQuestionListView.as_view(),
        name="quiz-question-list",
    ),

    path(
        "questions/<int:pk>/",
        QuestionDetailView.as_view(),
        name="question-detail",
    ),
]