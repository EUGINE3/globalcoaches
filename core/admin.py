from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import UserProfile, Partner, Testimonial

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'

class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_is_mentor', 'date_joined')
    list_filter = BaseUserAdmin.list_filter + ('userprofile__is_mentor', 'userprofile__is_admin')
    
    def get_is_mentor(self, obj):
        return hasattr(obj, 'userprofile') and obj.userprofile.is_mentor
    get_is_mentor.boolean = True
    get_is_mentor.short_description = 'Is Mentor'

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

@admin.register(Partner)
class PartnerAdmin(admin.ModelAdmin):
    list_display = ('name', 'website', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at',)

@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ('name', 'role', 'is_featured', 'created_at')
    list_filter = ('role', 'is_featured', 'created_at')
    search_fields = ('name', 'role', 'content')
    readonly_fields = ('created_at',)

