from django.contrib import admin
from .models import (
    Module, Week, Assignment, AssignmentSubmission, StudentProgress,
    WeeklyResource, ResourceView, WeekProgress, ModuleProgress
)

class WeekInline(admin.TabularInline):
    model = Week
    extra = 4
    max_num = 4

class AssignmentInline(admin.StackedInline):
    model = Assignment
    extra = 0

class WeeklyResourceInline(admin.TabularInline):
    model = WeeklyResource
    extra = 1
    fields = ('title', 'resource_type', 'file', 'external_url', 'is_required', 'order', 'is_active')
    readonly_fields = ('file_size',)

@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ('course_code', 'name', 'faculty_program', 'month_number', 'credits', 'is_active')
    list_filter = ('faculty_program__faculty', 'faculty_program__academic_level', 'is_active', 'created_at')
    search_fields = ('name', 'course_code', 'description')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [WeekInline]

@admin.register(Week)
class WeekAdmin(admin.ModelAdmin):
    list_display = ('module', 'week_number', 'theme', 'value', 'get_resource_count')
    list_filter = ('module__faculty_program__faculty', 'week_number')
    search_fields = ('theme', 'value', 'content')
    raw_id_fields = ('module',)
    inlines = [AssignmentInline, WeeklyResourceInline]

    def get_resource_count(self, obj):
        return obj.learning_resources.count()
    get_resource_count.short_description = 'Resources'

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

@admin.register(WeeklyResource)
class WeeklyResourceAdmin(admin.ModelAdmin):
    list_display = ('title', 'week', 'resource_type', 'is_required', 'order', 'is_active', 'created_at')
    list_filter = ('resource_type', 'is_required', 'is_active', 'week__module__faculty_program__faculty')
    search_fields = ('title', 'description', 'week__theme')
    raw_id_fields = ('week',)
    readonly_fields = ('file_size', 'created_at', 'updated_at')
    fieldsets = (
        ('Basic Information', {
            'fields': ('week', 'title', 'description', 'resource_type', 'order')
        }),
        ('Content', {
            'fields': ('file', 'external_url', 'file_size', 'duration')
        }),
        ('Settings', {
            'fields': ('is_required', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(ResourceView)
class ResourceViewAdmin(admin.ModelAdmin):
    list_display = ('student', 'resource', 'completed', 'view_count', 'first_viewed_at', 'completion_date')
    list_filter = ('completed', 'resource__resource_type', 'first_viewed_at')
    search_fields = ('student__username', 'resource__title')
    raw_id_fields = ('student', 'resource')
    readonly_fields = ('first_viewed_at', 'last_viewed_at', 'view_count')

@admin.register(WeekProgress)
class WeekProgressAdmin(admin.ModelAdmin):
    list_display = ('student', 'week', 'is_unlocked', 'is_completed', 'started_at', 'completed_at')
    list_filter = ('is_unlocked', 'week__module__faculty_program__faculty', 'completed_at')
    search_fields = ('student__username', 'week__theme')
    raw_id_fields = ('student', 'week')
    readonly_fields = ('started_at',)

@admin.register(ModuleProgress)
class ModuleProgressAdmin(admin.ModelAdmin):
    list_display = ('student', 'module', 'is_unlocked', 'is_completed', 'completion_percentage', 'started_at', 'completed_at')
    list_filter = ('is_unlocked', 'module__faculty_program__faculty', 'completed_at')
    search_fields = ('student__username', 'module__name')
    raw_id_fields = ('student', 'module')
    readonly_fields = ('started_at', 'completion_percentage')

@admin.register(StudentProgress)
class StudentProgressAdmin(admin.ModelAdmin):
    list_display = ('student', 'module', 'week', 'completed', 'completion_date')
    list_filter = ('completed', 'module__faculty_program__faculty', 'completion_date')
    search_fields = ('student__username', 'module__name')
    raw_id_fields = ('student', 'module', 'week')

