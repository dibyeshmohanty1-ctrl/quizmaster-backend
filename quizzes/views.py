from rest_framework import generics
from rest_framework.permissions import AllowAny

from .models import Quiz
from .serializers import QuizSerializer
from accounts.permissions import IsAdminUserRole


class QuizListCreateView(generics.ListCreateAPIView):
    queryset = Quiz.objects.all()
    serializer_class = QuizSerializer

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAdminUserRole()]

        return [AllowAny()]


class QuizDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Quiz.objects.all()
    serializer_class = QuizSerializer

    def get_permissions(self):
        if self.request.method in ["PUT", "PATCH", "DELETE"]:
            return [IsAdminUserRole()]

        return [AllowAny()]