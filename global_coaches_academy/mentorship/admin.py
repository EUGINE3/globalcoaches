from django.contrib import admin
from .models import MentorProfile, MentorshipPairing, MentorshipMessage, WeeklyCheckin, PeerReview

@admin.register(MentorProfile)
class MentorProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'years_experience', 'max_mentees', 'current_mentees_count', 'is_active')
    list_filter = ('is_active', 'years_experience', 'created_at')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'expertise_areas')
    readonly_fields = ('created_at',)
    raw_id_fields = ('user',)

@admin.register(MentorshipPairing)
class MentorshipPairingAdmin(admin.ModelAdmin):
    list_display = ('mentor', 'student', 'enrollment', 'status', 'paired_date', 'pairing_method')
    list_filter = ('status', 'pairing_method', 'paired_date')
    search_fields = ('mentor__user__username', 'student__username')
    readonly_fields = ('paired_date',)
    raw_id_fields = ('mentor', 'student', 'enrollment')

@admin.register(MentorshipMessage)
class MentorshipMessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'pairing', 'subject', 'sent_at', 'is_read')
    list_filter = ('is_read', 'sent_at')
    search_fields = ('sender__username', 'subject', 'content')
    readonly_fields = ('sent_at',)
    raw_id_fields = ('pairing', 'sender')

@admin.register(WeeklyCheckin)
class WeeklyCheckinAdmin(admin.ModelAdmin):
    list_display = ('student', 'pairing', 'week_ending', 'mood_rating', 'submitted_at', 'mentor_responded_at')
    list_filter = ('mood_rating', 'week_ending', 'submitted_at')
    search_fields = ('student__username', 'progress_summary')
    readonly_fields = ('submitted_at',)
    raw_id_fields = ('pairing', 'student')

@admin.register(PeerReview)
class PeerReviewAdmin(admin.ModelAdmin):
    list_display = ('reviewer', 'assignment_submission', 'get_average_rating', 'submitted_at', 'is_anonymous')
    list_filter = ('content_quality', 'creativity', 'presentation', 'is_anonymous', 'submitted_at')
    search_fields = ('reviewer__username', 'feedback')
    readonly_fields = ('submitted_at',)
    raw_id_fields = ('assignment_submission', 'reviewer')
    
    def get_average_rating(self, obj):
        return f"{obj.average_rating:.1f}"
    get_average_rating.short_description = 'Avg Rating'

