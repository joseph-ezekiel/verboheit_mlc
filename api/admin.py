"""
Admin configuration for managing core models in the Django admin interface.

Includes custom display, filtering, and search options for:
- Candidate
- Staff
- Exam
- Question
- CandidateScore
"""

from django.contrib import admin
from .models import Candidate, Staff, Exam, Question, CandidateScore


@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    """
    Admin interface for the Candidate model.
    Displays key candidate details and allows filtering by role, verification, and active status.
    """

    list_display = (
        "id",
        "user",
        "school",
        "role",
        "is_verified",
        "is_active",
        "date_created",
    )
    list_filter = ("role", "is_verified", "is_active")
    search_fields = ("user__username", "school")


@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    """
    Admin interface for the Staff model.
    Displays key staff information and allows filtering by role, verification, and active status.
    """

    list_display = (
        "id",
        "user",
        "role",
        "occupation",
        "is_verified",
        "is_active",
        "date_created",
    )
    list_filter = ("role", "is_verified", "is_active")
    search_fields = ("user__username", "occupation")


@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    """
    Admin interface for the Exam model.
    Displays exam metadata and allows filtering by stage and publication status.
    """

    list_display = (
        "id",
        "title",
        "stage",
        "exam_date",
        "duration_minutes",
        "is_published",
        "date_created",
    )
    list_filter = ("stage", "is_published")
    search_fields = ("title", "stage")


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    """
    Admin interface for the Question model.
    Displays question text, difficulty, and creator.
    """

    list_display = ("id", "description", "difficulty", "created_by", "date_created")
    list_filter = ("difficulty",)
    search_fields = ("description",)


@admin.register(CandidateScore)
class CandidateScoreAdmin(admin.ModelAdmin):
    """
    Admin interface for the CandidateScore model.
    Displays score details per candidate and exam.
    """

    list_display = ("id", "candidate", "exam", "score", "date_taken")
    list_filter = ("exam",)
    search_fields = ("candidate__user__username", "exam__title")
