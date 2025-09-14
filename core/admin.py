from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.utils.html import format_html
from django.db.models import Count
from .models import UserProfile, Partner, Testimonial

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'
    fields = ('bio', 'phone', 'location', 'is_mentor', 'is_admin')

class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('username', 'get_full_name', 'email', 'is_staff', 'get_is_mentor', 'get_is_admin', 'date_joined')
    list_filter = BaseUserAdmin.list_filter + ('userprofile__is_mentor', 'userprofile__is_admin')
    search_fields = ('username', 'first_name', 'last_name', 'email', 'userprofile__bio')

    actions = ['make_mentor', 'remove_mentor', 'make_admin', 'remove_admin']

    def get_full_name(self, obj):
        return obj.get_full_name() or obj.username
    get_full_name.short_description = 'Full Name'

    def get_is_mentor(self, obj):
        if hasattr(obj, 'userprofile') and obj.userprofile.is_mentor:
            return format_html('<span style="color: green;">✓ Mentor</span>')
        return format_html('<span style="color: #95a5a6;">-</span>')
    get_is_mentor.short_description = 'Mentor'

    def get_is_admin(self, obj):
        if hasattr(obj, 'userprofile') and obj.userprofile.is_admin:
            return format_html('<span style="color: blue;">✓ Admin</span>')
        return format_html('<span style="color: #95a5a6;">-</span>')
    get_is_admin.short_description = 'Admin'

    def make_mentor(self, request, queryset):
        for user in queryset:
            profile, created = UserProfile.objects.get_or_create(user=user)
            profile.is_mentor = True
            profile.save()
        self.message_user(request, f"{queryset.count()} users marked as mentors.")
    make_mentor.short_description = "Mark selected users as mentors"

    def remove_mentor(self, request, queryset):
        for user in queryset:
            if hasattr(user, 'userprofile'):
                user.userprofile.is_mentor = False
                user.userprofile.save()
        self.message_user(request, f"{queryset.count()} users removed from mentors.")
    remove_mentor.short_description = "Remove mentor status from selected users"

    def make_admin(self, request, queryset):
        for user in queryset:
            profile, created = UserProfile.objects.get_or_create(user=user)
            profile.is_admin = True
            profile.save()
        self.message_user(request, f"{queryset.count()} users marked as admins.")
    make_admin.short_description = "Mark selected users as admins"

    def remove_admin(self, request, queryset):
        for user in queryset:
            if hasattr(user, 'userprofile'):
                user.userprofile.is_admin = False
                user.userprofile.save()
        self.message_user(request, f"{queryset.count()} users removed from admins.")
    remove_admin.short_description = "Remove admin status from selected users"

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

@admin.register(Partner)
class PartnerAdmin(admin.ModelAdmin):
    list_display = ('name', 'website_link', 'is_active', 'active_status', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at',)
    list_editable = ('is_active',)

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'website')
        }),
        ('Media', {
            'fields': ('logo',)
        }),
        ('Settings', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

    def website_link(self, obj):
        if obj.website:
            return format_html('<a href="{}" target="_blank">{}</a>', obj.website, obj.website)
        return '-'
    website_link.short_description = 'Website'

    def active_status(self, obj):
        if obj.is_active:
            return format_html('<span style="color: green;">✓ Active</span>')
        return format_html('<span style="color: red;">✗ Inactive</span>')
    active_status.short_description = 'Status'

@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ('name', 'role', 'is_featured', 'featured_status', 'created_at')
    list_filter = ('role', 'is_featured', 'created_at')
    search_fields = ('name', 'role', 'content')
    readonly_fields = ('created_at',)
    list_editable = ('is_featured',)

    fieldsets = (
        ('Person Information', {
            'fields': ('name', 'role', 'content')
        }),
        ('Media', {
            'fields': ('image',)
        }),
        ('Settings', {
            'fields': ('is_featured',)
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

    def featured_status(self, obj):
        if obj.is_featured:
            return format_html('<span style="color: gold;">⭐ Featured</span>')
        return format_html('<span style="color: #95a5a6;">-</span>')
    featured_status.short_description = 'Featured'

