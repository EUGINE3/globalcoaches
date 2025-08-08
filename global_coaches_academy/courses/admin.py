from django.contrib import admin
from .models import Module, Week, Assignment, AssignmentSubmission, StudentProgress

class WeekInline(admin.TabularInline):
    model = Week
    extra = 4
    max_num = 4

class AssignmentInline(admin.StackedInline):
    model = Assignment
    extra = 0

@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ('course_code', 'name', 'faculty_program', 'month_number', 'credits', 'is_active')
    list_filter = ('faculty_program__faculty', 'faculty_program__academic_level', 'is_active', 'created_at')
    search_fields = ('name', 'course_code', 'description')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [WeekInline]

@admin.register(Week)
class WeekAdmin(admin.ModelAdmin):
    list_display = ('module', 'week_number', 'theme', 'value')
    list_filter = ('module__faculty_program__faculty', 'week_number')
    search_fields = ('theme', 'value', 'content')
    raw_id_fields = ('module',)
    inlines = [AssignmentInline]

@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ('title', 'week', 'max_points', 'due_date_offset', 'is_required')
    list_filter = ('is_required', 'max_points', 'submission_format')
    search_fields = ('title', 'description')
    raw_id_fields = ('week',)

@admin.register(AssignmentSubmission)
class AssignmentSubmissionAdmin(admin.ModelAdmin):
    list_display = ('student', 'assignment', 'submitted_at', 'grade', 'graded_by')
    list_filter = ('assignment__week__module__faculty_program__faculty', 'submitted_at', 'graded_by')
    search_fields = ('student__username', 'assignment__title')
    readonly_fields = ('submitted_at',)
    raw_id_fields = ('assignment', 'student', 'graded_by')

@admin.register(StudentProgress)
class StudentProgressAdmin(admin.ModelAdmin):
    list_display = ('student', 'module', 'week', 'completed', 'completion_date')
    list_filter = ('completed', 'module__faculty_program__faculty', 'completion_date')
    search_fields = ('student__username', 'module__name')
    raw_id_fields = ('student', 'module', 'week')

