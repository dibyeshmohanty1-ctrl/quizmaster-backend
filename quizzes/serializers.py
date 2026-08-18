from rest_framework import serializers
from .models import Quiz


class QuizSerializer(serializers.ModelSerializer):
    question_count = serializers.SerializerMethodField()
    def get_question_count(self, obj):
     return obj.questions.count()
    category_name = serializers.CharField(
        source="category.name",
        read_only=True
    )

    class Meta:
        model = Quiz
        fields = [
            "id",
            "title",
            "question_count",
            "description",
            "category",
            "category_name",
            "difficulty",
            "duration",
            "passing_percentage",
            "max_attempts",
            "status",
            "thumbnail",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
        ]