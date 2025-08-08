from django.contrib import admin
from .models import Faculty, AcademicLevel, FacultyProgram

@admin.register(Faculty)
class FacultyAdmin(admin.ModelAdmin):
    list_display = ('name', 'faculty_type', 'is_active', 'created_at')
    list_filter = ('faculty_type', 'is_active', 'created_at')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('created_at', 'updated_at')

@admin.register(AcademicLevel)
class AcademicLevelAdmin(admin.ModelAdmin):
    list_display = ('name', 'level_type', 'duration_months', 'credits_required')
    list_filter = ('level_type', 'duration_months')
    search_fields = ('name', 'description')

@admin.register(FacultyProgram)
class FacultyProgramAdmin(admin.ModelAdmin):
    list_display = ('faculty', 'academic_level', 'is_active')
    list_filter = ('faculty', 'academic_level', 'is_active')
    search_fields = ('faculty__name', 'academic_level__name')
    raw_id_fields = ('faculty', 'academic_level')

