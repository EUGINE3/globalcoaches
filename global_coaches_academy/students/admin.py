from django.contrib import admin
from .models import StudentEnrollment, Certificate, StudentReflection, FinalProject

@admin.register(StudentEnrollment)
class StudentEnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'faculty_program', 'status', 'enrollment_date', 'total_credits_earned', 'get_progress')
    list_filter = ('status', 'faculty_program__faculty', 'faculty_program__academic_level', 'enrollment_date')
    search_fields = ('student__username', 'student__first_name', 'student__last_name')
    readonly_fields = ('enrollment_date',)
    raw_id_fields = ('student', 'faculty_program')
    
    def get_progress(self, obj):
        return f"{obj.calculate_progress_percentage():.1f}%"
    get_progress.short_description = 'Progress'

@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ('student', 'certificate_type', 'certificate_number', 'issue_date', 'is_verified')
    list_filter = ('certificate_type', 'is_verified', 'issue_date')
    search_fields = ('student__username', 'certificate_number', 'verification_code')
    readonly_fields = ('issue_date',)
    raw_id_fields = ('student', 'enrollment')

@admin.register(StudentReflection)
class StudentReflectionAdmin(admin.ModelAdmin):
    list_display = ('student', 'title', 'enrollment', 'is_private', 'created_at')
    list_filter = ('is_private', 'enrollment__faculty_program__faculty', 'created_at')
    search_fields = ('student__username', 'title', 'content')
    readonly_fields = ('created_at', 'updated_at')
    raw_id_fields = ('student', 'enrollment')

@admin.register(FinalProject)
class FinalProjectAdmin(admin.ModelAdmin):
    list_display = ('student', 'title', 'enrollment', 'submitted_at', 'defense_date', 'approved')
    list_filter = ('approved', 'enrollment__faculty_program__faculty', 'submitted_at', 'defense_date')
    search_fields = ('student__username', 'title', 'description')
    readonly_fields = ('submitted_at',)
    raw_id_fields = ('student', 'enrollment', 'approved_by')

