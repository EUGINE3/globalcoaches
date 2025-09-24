from django.contrib import admin
from .models import (
    Assignment, QuizQuestion, QuizChoice
)

# Quiz-related inlines
class QuizChoiceInline(admin.TabularInline):
    model = QuizChoice
    extra = 2
    fields = ('text', 'is_correct', 'explanation', 'order')

class QuizQuestionInline(admin.StackedInline):
    model = QuizQuestion
    extra = 1
    fields = ('question_type', 'text', 'points', 'order')

# Admin models
@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    inlines = [QuizQuestionInline]
    list_display = ('title', 'assignment_type', 'is_quiz', 'due_date', 'max_points')
    list_filter = ('is_quiz', 'assignment_type')
    search_fields = ('title', 'description')
    
    fieldsets = (
        (None, {
            'fields': ('title', 'description', 'instructions')
        }),
        ('Assignment Settings', {
            'fields': ('lesson', 'topic', 'assignment_type', 'max_points', 'due_date')
        }),
        ('Quiz Settings', {
            'fields': ('is_quiz', 'time_limit_minutes', 'passing_score', 'shuffle_questions', 'show_correct_answers'),
            'classes': ('collapse',),
            'description': 'Configure quiz-specific settings here'
        })
    )

    def get_inlines(self, request, obj=None):
        if obj and obj.is_quiz:
            return [QuizQuestionInline]
        return []

@admin.register(QuizQuestion)
class QuizQuestionAdmin(admin.ModelAdmin):
    inlines = [QuizChoiceInline]
    list_display = ('text', 'assignment', 'question_type', 'points', 'order')
    list_filter = ('question_type', 'assignment')
    search_fields = ('text', 'assignment__title')
    ordering = ('assignment', 'order')
admin.site.register(QuizQuestion, QuizQuestionAdmin)
