from django.db import models
from django.conf import settings
from quizzes.models import Quiz
from questions.models import Question, Option


class Attempt(models.Model):
    STATUS_CHOICES = [
        ("PASSED", "Passed"),
        ("FAILED", "Failed"),
        ("IN_PROGRESS", "In Progress"),
    ]

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="attempts"
    )

    quiz = models.ForeignKey(
        Quiz,
        on_delete=models.CASCADE,
        related_name="attempts"
    )

    score = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    correct_answers = models.PositiveIntegerField(default=0)

    incorrect_answers = models.PositiveIntegerField(default=0)

    unanswered = models.PositiveIntegerField(default=0)

    time_taken = models.PositiveIntegerField(default=0)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="IN_PROGRESS"
    )

    started_at = models.DateTimeField(auto_now_add=True)

    completed_at = models.DateTimeField(
        blank=True,
        null=True
    )

    class Meta:
        ordering = ["-started_at"]

    def __str__(self):
        return f"{self.student.username} - {self.quiz.title}"


class Answer(models.Model):
    attempt = models.ForeignKey(
        Attempt,
        on_delete=models.CASCADE,
        related_name="answers"
    )

    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE
    )

    selected_option = models.ForeignKey(
        Option,
        on_delete=models.CASCADE
    )

    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.attempt.student.username} - {self.question.id}"