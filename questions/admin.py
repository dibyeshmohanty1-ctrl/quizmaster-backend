from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Question, Option


class OptionInline(admin.TabularInline):
    model = Option
    extra = 4


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "quiz",
        "marks",
        "difficulty",
    )

    list_filter = (
        "quiz",
        "difficulty",
    )

    search_fields = (
        "question_text",
    )

    inlines = [OptionInline]