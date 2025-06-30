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
from .models import (
    Candidate, Staff,
    Exam, Question,
    CandidateScore,
    CandidateAnswer,
)


@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    """
    Admin interface for the Candidate model.
    Displays key candidate details and allows filtering by role, verification, and active status.
    """

    list_display = (
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
        "description",
        "stage",
        "exam_date",
        "open_duration_hours",
        "countdown_minutes",
        "is_active",
        "date_created",
    )
    list_filter = ("stage", "is_active")
    search_fields = ("title", "stage")


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    """
    Admin interface for the Question model.
    Displays question text, difficulty, and creator.
    """

    list_display = ("id", "text", "difficulty", "created_by", "date_created")
    list_filter = ("difficulty",)
    search_fields = ("text",)


@admin.register(CandidateScore)
class CandidateScoreAdmin(admin.ModelAdmin):
    """
    Admin interface for the CandidateScore model.
    Displays score details per candidate and exam.
    """

    list_display = ("id", "candidate", "exam", "score", "date_recorded", "auto_score")
    list_filter = ("exam",)
    search_fields = ("candidate__user__username", "exam__title", "auto_score")
@admin.register(CandidateAnswer)
class CandidateAnswerAdmin(admin.ModelAdmin):
    """
    Admin interface for the CandidateAnswer model.
    Displays answers provided by each candidate in specific exams.
    """
    list_display = (
        "id",
        "get_candidate",
        "get_exam",
        "question",
        "selected_option",
        "answered_at",
    )
    list_filter = ("candidate_score__exam", "answered_at")
    search_fields = ("candidate_score__candidate__user__username", "question__text")
    autocomplete_fields = ("question", "candidate_score")

    def get_candidate(self, obj):
        return obj.candidate_score.candidate
    get_candidate.short_description = "Candidate"

    def get_exam(self, obj):
        return obj.candidate_score.exam
    get_exam.short_description = "Exam"
