from rest_framework import generics
from rest_framework.permissions import AllowAny

from .models import Question
from .serializers import QuestionSerializer
from accounts.permissions import IsAdminUserRole


class QuizQuestionListView(generics.ListCreateAPIView):
    serializer_class = QuestionSerializer

    def get_queryset(self):
        quiz_id = self.kwargs["quiz_id"]
        return Question.objects.filter(quiz_id=quiz_id)

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAdminUserRole()]

        return [AllowAny()]


class QuestionDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer

    def get_permissions(self):
        if self.request.method in ["PUT", "PATCH", "DELETE"]:
            return [IsAdminUserRole()]

        return [AllowAny()]