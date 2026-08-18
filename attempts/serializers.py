from rest_framework import serializers
from .models import Attempt, Answer

class AttemptSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attempt
        fields = [
                    "id",
                    "student",
                    "quiz",
                    "score",
                    "percentage",
                    "correct_answers",
                    "incorrect_answers",
                    "unanswered",
                    "time_taken",
                    "status",
                    "started_at",
                    "completed_at",

                ]

    read_only_fields = [
        "student",
        "score",
        "percentage",
        "correct_answers",
        "incorrect_answers",
        "unanswered",
        "time_taken",
        "status",
        "started_at",
        "completed_at",

    ]

    class AnswerSerializer(serializers.ModelSerializer):
        class Meta:
            model = Answer
            fields=[
                "id",
                "attempt",
                "question",
                "selected_option",
                "is_correct",
            ]

    read_only_fields = [ 
        "is_correct",
    ]       