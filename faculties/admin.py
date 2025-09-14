from django.contrib import admin
from .models import ProgramLevel, Module, ProgramModule

@admin.register(ProgramLevel)
class ProgramLevelAdmin(admin.ModelAdmin):
    list_display = ('name', 'level_type', 'duration_months', 'is_active', 'created_at')
    list_filter = ('level_type', 'is_active', 'created_at')
    search_fields = ('name', 'description', 'focus_areas')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ('name', 'module_type', 'is_active', 'created_at')
    list_filter = ('module_type', 'is_active', 'created_at')
    search_fields = ('name', 'description', 'learning_objectives')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(ProgramModule)
class ProgramModuleAdmin(admin.ModelAdmin):
    list_display = ('program_level', 'module', 'depth_level', 'credits', 'is_active')
    list_filter = ('program_level', 'module', 'depth_level', 'is_active')
    search_fields = ('program_level__name', 'module__name', 'description')
    raw_id_fields = ('program_level', 'module')

