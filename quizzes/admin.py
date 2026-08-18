from django.contrib import admin
from .models import Quiz


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "category",
        "difficulty",
        "status",
        "duration",
    )

    list_filter = (
        "status",
        "difficulty",
        "category",
    )

    search_fields = (
        "title",
        "description",
    )