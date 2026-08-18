from django.contrib import admin
from .models import Attempt, Answer


class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 0


@admin.register(Attempt)
class AttemptAdmin(admin.ModelAdmin):
    list_display = (
        "student",
        "quiz",
        "percentage",
        "status",
        "started_at",
    )

    inlines = [AnswerInline]