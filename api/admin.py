from django.contrib import admin
from .models import Candidate, Staff, Exam, Question, CandidateScore

@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'school', 'role', 'is_verified', 'is_active', 'date_created')
    list_filter = ('role', 'is_verified', 'is_active')
    search_fields = ('user__username', 'school')

@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'role', 'occupation', 'is_verified', 'is_active', 'date_created')
    list_filter = ('role', 'is_verified', 'is_active')
    search_fields = ('user__username', 'occupation')

@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'stage', 'exam_date', 'duration_minutes', 'is_published', 'date_created')
    list_filter = ('stage', 'is_published')
    search_fields = ('title', 'stage')

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'description', 'difficulty', 'created_by', 'date_created')
    list_filter = ('difficulty',)
    search_fields = ('description',)

@admin.register(CandidateScore)
class CandidateScoreAdmin(admin.ModelAdmin):
    list_display = ('id', 'candidate', 'exam', 'score', 'date_created')
    list_filter = ('exam',)
    search_fields = ('candidate__user__username', 'exam__title')