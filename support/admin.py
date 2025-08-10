from django.contrib import admin
from .models import FAQ, Feedback, SupportTicket, SupportTicketResponse, ContactInfo

@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ('question', 'category', 'is_featured', 'order', 'created_at')
    list_filter = ('category', 'is_featured', 'created_at')
    search_fields = ('question', 'answer')
    readonly_fields = ('created_at', 'updated_at')
    raw_id_fields = ('created_by',)

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('subject', 'feedback_type', 'user', 'status', 'priority', 'submitted_at')
    list_filter = ('feedback_type', 'status', 'priority', 'submitted_at')
    search_fields = ('subject', 'message', 'user__username')
    readonly_fields = ('submitted_at',)
    raw_id_fields = ('user', 'responded_by')

class SupportTicketResponseInline(admin.TabularInline):
    model = SupportTicketResponse
    extra = 0
    readonly_fields = ('created_at',)
    raw_id_fields = ('user',)

@admin.register(SupportTicket)
class SupportTicketAdmin(admin.ModelAdmin):
    list_display = ('ticket_number', 'user', 'subject', 'category', 'priority', 'status', 'created_at')
    list_filter = ('category', 'priority', 'status', 'created_at')
    search_fields = ('ticket_number', 'subject', 'user__username')
    readonly_fields = ('created_at', 'updated_at')
    raw_id_fields = ('user', 'assigned_to')
    inlines = [SupportTicketResponseInline]

@admin.register(ContactInfo)
class ContactInfoAdmin(admin.ModelAdmin):
    list_display = ('label', 'contact_type', 'value', 'is_emergency', 'is_active', 'order')
    list_filter = ('contact_type', 'is_emergency', 'is_active')
    search_fields = ('label', 'value', 'description')
    list_editable = ('order', 'is_active')

