from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from programs.models import ProgramModule
from .models import (
    Module, ModuleTopic, Course, WeeklyResource,
    ResourceView, WeekProgress, ModuleProgress,
    Lesson, LessonResource, Assignment, AssignmentSubmission,
    LessonProgress, ResourceProgress
)


# Inline classes for better organization


class CourseInline(admin.TabularInline):
    model = Course
    extra = 0
    fields = ('title', 'slug', 'week_count', 'is_active')
    readonly_fields = ()

class WeeklyResourceInline(admin.TabularInline):
    model = WeeklyResource
    extra = 0
    fields = ('week_number', 'title', 'resource_type', 'is_required', 'order')
    readonly_fields = ()

class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 0
    fields = ('lesson_number', 'title', 'lesson_type', 'duration_minutes', 'sequence_order', 'is_active')
    readonly_fields = ()

class LessonResourceInline(admin.TabularInline):
    model = LessonResource
    extra = 0
    fields = ('title', 'resource_type', 'is_required', 'estimated_duration_minutes', 'order', 'is_active')
    readonly_fields = ()

class AssignmentInline(admin.TabularInline):
    model = Assignment
    extra = 0
    fields = ('title', 'assignment_type', 'due_date', 'max_points', 'is_active')
    readonly_fields = ()

class ModuleTopicInline(admin.StackedInline):
    model = ModuleTopic
    extra = 0
    fields = (
        ('topic_number', 'title', 'order'),
        ('total_credits', 'total_hours', 'theory_hours', 'practical_hours'),
        'description',
        'learning_objectives',
        'is_active'
    )
    readonly_fields = ()




@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ('name', 'module_type', 'active_status', 'created_at', 'updated_at')
    list_filter = ('module_type', 'is_active', 'created_at')
    search_fields = ('name', 'description', 'learning_objectives')
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'module_type', 'description', 'learning_objectives')
        }),
        ('Media', {
            'fields': ('image',)
        }),
        ('Settings', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def active_status(self, obj):
        if obj.is_active:
            return format_html('<span style="color: green;">✓ Active</span>')
        return format_html('<span style="color: red;">✗ Inactive</span>')
    active_status.short_description = 'Status'





@admin.register(ModuleTopic)
class ModuleTopicAdmin(admin.ModelAdmin):
    list_display = ('program_module', 'topic_number', 'title', 'total_credits', 'total_hours', 'lessons_count', 'assignments_count', 'is_active')
    list_filter = ('program_module__program_level', 'program_module__module', 'is_active')
    search_fields = ('title', 'description', 'learning_objectives')
    raw_id_fields = ('program_module',)
    inlines = [LessonInline, AssignmentInline]
    ordering = ('program_module', 'topic_number')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('program_module', 'topic_number', 'title', 'description', 'learning_objectives', 'order')
        }),
        ('Time & Credits', {
            'fields': ('total_credits', 'total_hours', 'theory_hours', 'practical_hours')
        }),
        ('Theory Component', {
            'fields': ('theory_content', 'theory_resources')
        }),
        ('Practical Component', {
            'fields': ('practical_activities', 'practical_deliverables', 'assessment_criteria')
        }),
        ('Settings', {
            'fields': ('is_active',)
        }),
    )

    def lessons_count(self, obj):
        count = obj.lessons.filter(is_active=True).count()
        return format_html('<span style="color: #007bff;">📖 {}</span>', count)
    lessons_count.short_description = 'Lessons'

    def assignments_count(self, obj):
        count = obj.assignments.filter(is_active=True).count()
        if count > 0:
            return format_html('<span style="color: #dc3545;">📝 {}</span>', count)
        return format_html('<span style="color: #6c757d;">None</span>')
    assignments_count.short_description = 'Assignments'


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'program_module', 'week_count', 'active_status', 'created_at')
    list_filter = ('program_module__program_level', 'program_module__module', 'is_active', 'created_at')
    search_fields = ('title', 'description', 'slug')
    readonly_fields = ('created_at', 'updated_at')
    raw_id_fields = ('program_module',)
    inlines = [WeeklyResourceInline]
    prepopulated_fields = {'slug': ('title',)}

    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'description', 'program_module')
        }),
        ('Course Settings', {
            'fields': ('week_count', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def active_status(self, obj):
        if obj.is_active:
            return format_html('<span style="color: green;">✓ Active</span>')
        return format_html('<span style="color: red;">✗ Inactive</span>')
    active_status.short_description = 'Status'


@admin.register(WeeklyResource)
class WeeklyResourceAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'week_number', 'resource_type_badge', 'required_status', 'order', 'is_required', 'created_at')
    list_filter = ('resource_type', 'is_required', 'course__program_module__program_level', 'week_number')
    search_fields = ('title', 'content', 'course__title')
    raw_id_fields = ('course',)
    readonly_fields = ('created_at',)
    list_editable = ('order', 'is_required')

    fieldsets = (
        ('Basic Information', {
            'fields': ('course', 'week_number', 'title', 'content')
        }),
        ('Resource Settings', {
            'fields': ('resource_type', 'is_required', 'order')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

    def resource_type_badge(self, obj):
        colors = {
            'video': '#ff6b6b',
            'reading': '#4ecdc4',
            'assignment': '#45b7d1',
            'discussion': '#96ceb4',
            'quiz': '#feca57'
        }
        color = colors.get(obj.resource_type, '#95a5a6')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 8px; border-radius: 3px; font-size: 11px;">{}</span>',
            color, obj.get_resource_type_display()
        )
    resource_type_badge.short_description = 'Type'

    def required_status(self, obj):
        if obj.is_required:
            return format_html('<span style="color: red;">✓ Required</span>')
        return format_html('<span style="color: #95a5a6;">Optional</span>')
    required_status.short_description = 'Required'


@admin.register(ResourceView)
class ResourceViewAdmin(admin.ModelAdmin):
    list_display = ('student', 'weekly_resource', 'viewed_at', 'time_spent')
    list_filter = ('weekly_resource__resource_type', 'viewed_at')
    search_fields = ('student__username', 'weekly_resource__title')
    raw_id_fields = ('student', 'weekly_resource')
    readonly_fields = ('viewed_at',)


@admin.register(WeekProgress)
class WeekProgressAdmin(admin.ModelAdmin):
    list_display = ('student', 'weekly_resource', 'is_completed', 'completed_at')
    list_filter = ('is_completed', 'weekly_resource__course__program_module__program_level', 'completed_at')
    search_fields = ('student__username', 'weekly_resource__title')
    raw_id_fields = ('student', 'weekly_resource')
    readonly_fields = ('completed_at',)


@admin.register(ModuleProgress)
class ModuleProgressAdmin(admin.ModelAdmin):
    list_display = ('student', 'program_module', 'unlock_status', 'progress_percentage', 'completion_status', 'last_accessed')
    list_filter = ('is_unlocked', 'is_completed', 'program_module__program_level', 'completed_at')
    search_fields = ('student__username', 'program_module__module__name')
    raw_id_fields = ('student', 'program_module')
    readonly_fields = ('progress_percentage', 'completed_at', 'unlocked_at', 'last_accessed')

    fieldsets = (
        ('Student & Module', {
            'fields': ('student', 'program_module')
        }),
        ('Progress Status', {
            'fields': ('is_unlocked', 'unlocked_at', 'progress_percentage', 'is_completed', 'completed_at')
        }),
        ('Timestamps', {
            'fields': ('last_accessed',),
            'classes': ('collapse',)
        }),
    )

    def unlock_status(self, obj):
        if obj.is_unlocked:
            return format_html('<span style="color: green;">🔓 Unlocked</span>')
        return format_html('<span style="color: red;">🔒 Locked</span>')
    unlock_status.short_description = 'Access'

    def completion_status(self, obj):
        if obj.is_completed:
            return format_html('<span style="color: green;">✅ Completed</span>')
        elif obj.is_unlocked:
            return format_html('<span style="color: orange;">⏳ In Progress</span>')
        return format_html('<span style="color: gray;">⏸️ Not Started</span>')
    completion_status.short_description = 'Status'





@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('topic', 'lesson_number', 'title', 'lesson_type', 'duration_minutes', 'resources_count', 'assignments_count', 'is_active')
    list_filter = ('lesson_type', 'topic__program_module__program_level', 'topic__program_module__module', 'is_active')
    search_fields = ('title', 'description', 'topic__title')
    raw_id_fields = ('topic',)
    filter_horizontal = ('prerequisites',)
    inlines = [LessonResourceInline, AssignmentInline]
    ordering = ('topic', 'sequence_order', 'lesson_number')

    fieldsets = (
        ('Basic Information', {
            'fields': ('topic', 'lesson_number', 'title', 'description', 'learning_objectives')
        }),
        ('Lesson Settings', {
            'fields': ('lesson_type', 'duration_minutes', 'sequence_order', 'prerequisites')
        }),
        ('Content', {
            'fields': ('content', 'instructor_notes')
        }),
        ('Settings', {
            'fields': ('is_active',)
        }),
    )

    def resources_count(self, obj):
        count = obj.resources.filter(is_active=True).count()
        return format_html('<span style="color: #007bff;">📚 {}</span>', count)
    resources_count.short_description = 'Resources'

    def assignments_count(self, obj):
        count = obj.assignments.filter(is_active=True).count()
        if count > 0:
            return format_html('<span style="color: #dc3545;">📝 {}</span>', count)
        return format_html('<span style="color: #6c757d;">None</span>')
    assignments_count.short_description = 'Assignments'


@admin.register(LessonResource)
class LessonResourceAdmin(admin.ModelAdmin):
    list_display = ('lesson', 'title', 'resource_type_badge', 'required_status', 'estimated_duration_minutes', 'order', 'is_required', 'is_active')
    list_filter = ('resource_type', 'is_required', 'lesson__topic__program_module__program_level', 'is_active')
    search_fields = ('title', 'description', 'lesson__title')
    raw_id_fields = ('lesson',)
    list_editable = ('order', 'is_required')
    ordering = ('lesson', 'order')

    fieldsets = (
        ('Basic Information', {
            'fields': ('lesson', 'title', 'description', 'resource_type')
        }),
        ('Content', {
            'fields': ('content', 'file', 'url')
        }),
        ('Settings', {
            'fields': ('is_required', 'estimated_duration_minutes', 'order', 'is_active')
        }),
    )

    def resource_type_badge(self, obj):
        colors = {
            'video': '#ff6b6b',
            'reading': '#4ecdc4',
            'document': '#45b7d1',
            'link': '#96ceb4',
            'presentation': '#feca57',
            'audio': '#a55eea',
            'interactive': '#26de81'
        }
        color = colors.get(obj.resource_type, '#95a5a6')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 8px; border-radius: 3px; font-size: 11px;">{}</span>',
            color, obj.get_resource_type_display()
        )
    resource_type_badge.short_description = 'Type'

    def required_status(self, obj):
        if obj.is_required:
            return format_html('<span style="color: red;">✓ Required</span>')
        return format_html('<span style="color: #95a5a6;">Optional</span>')
    required_status.short_description = 'Required'


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ('title', 'get_parent', 'assignment_type', 'due_date', 'max_points', 'submissions_count', 'is_active')
    list_filter = ('assignment_type', 'due_date', 'lesson__topic__program_module__program_level', 'is_active')
    search_fields = ('title', 'description', 'lesson__title', 'topic__title')
    raw_id_fields = ('lesson', 'topic')
    date_hierarchy = 'due_date'
    ordering = ('due_date',)

    fieldsets = (
        ('Assignment Details', {
            'fields': ('lesson', 'topic', 'title', 'description', 'instructions', 'assignment_type')
        }),
        ('Grading & Deadlines', {
            'fields': ('max_points', 'due_date', 'late_submission_penalty', 'allow_late_submission')
        }),
        ('Files', {
            'fields': ('assignment_file', 'rubric_file')
        }),
        ('Settings', {
            'fields': ('is_active',)
        }),
    )

    def get_parent(self, obj):
        if obj.lesson:
            return format_html('<span style="color: #007bff;">📖 {}</span>', obj.lesson.title)
        elif obj.topic:
            return format_html('<span style="color: #28a745;">📚 {}</span>', obj.topic.title)
        return "No Parent"
    get_parent.short_description = 'Parent'

    def submissions_count(self, obj):
        count = obj.submissions.count()
        graded_count = obj.submissions.filter(is_graded=True).count()
        if count > 0:
            return format_html(
                '<span style="color: #007bff;">📝 {} ({} graded)</span>',
                count, graded_count
            )
        return format_html('<span style="color: #6c757d;">No submissions</span>')
    submissions_count.short_description = 'Submissions'


@admin.register(AssignmentSubmission)
class AssignmentSubmissionAdmin(admin.ModelAdmin):
    list_display = ('student', 'assignment', 'submitted_at', 'is_late', 'grade_status', 'points_earned', 'attempt_number')
    list_filter = ('is_late', 'is_graded', 'assignment__assignment_type', 'submitted_at', 'graded_at')
    search_fields = ('student__username', 'student__first_name', 'student__last_name', 'assignment__title')
    raw_id_fields = ('student', 'assignment', 'graded_by')
    readonly_fields = ('submitted_at', 'is_late', 'grade_percentage')
    date_hierarchy = 'submitted_at'
    ordering = ('-submitted_at',)

    fieldsets = (
        ('Submission Info', {
            'fields': ('assignment', 'student', 'attempt_number', 'submitted_at', 'is_late')
        }),
        ('Content', {
            'fields': ('submission_text', 'submission_file')
        }),
        ('Grading', {
            'fields': ('is_graded', 'points_earned', 'grade_percentage', 'instructor_feedback', 'graded_by', 'graded_at')
        }),
    )

    def grade_status(self, obj):
        if not obj.is_graded:
            return format_html('<span style="color: orange;">⏳ Pending</span>')
        elif obj.grade_percentage >= 70:
            return format_html('<span style="color: green;">✅ Passed ({}%)</span>', round(obj.grade_percentage))
        else:
            return format_html('<span style="color: red;">❌ Failed ({}%)</span>', round(obj.grade_percentage))
    grade_status.short_description = 'Grade Status'