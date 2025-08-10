from django.contrib import admin
from .models import APIConfiguration, InterviewAssistant, PhoneNumber, InterviewCall

@admin.register(APIConfiguration)
class APIConfigurationAdmin(admin.ModelAdmin):
    list_display = ['user', 'is_twilio_configured', 'is_vapi_configured', 'created_at', 'updated_at']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['created_at', 'updated_at']
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        # Hide sensitive fields in admin view
        if 'twilio_auth_token' in form.base_fields:
            form.base_fields['twilio_auth_token'].widget.attrs['type'] = 'password'
        if 'vapi_api_key' in form.base_fields:
            form.base_fields['vapi_api_key'].widget.attrs['type'] = 'password'
        return form


@admin.register(InterviewAssistant)
class InterviewAssistantAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'voice_provider', 'voice_id', 'model_provider', 'model', 'created_at']
    list_filter = ['voice_provider', 'model_provider', 'created_at']
    search_fields = ['name', 'user__username', 'vapi_assistant_id']
    readonly_fields = ['vapi_assistant_id', 'created_at', 'updated_at']
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'name', 'vapi_assistant_id', 'first_message')
        }),
        ('AI Configuration', {
            'fields': ('voice_provider', 'voice_id', 'model_provider', 'model')
        }),
        ('Knowledge Base', {
            'fields': ('knowledge_text', 'knowledge_urls'),
            'classes': ('collapse',)
        }),
        ('Technical Details', {
            'fields': ('configuration', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(PhoneNumber)
class PhoneNumberAdmin(admin.ModelAdmin):
    list_display = ['phone_number', 'user', 'friendly_name', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['phone_number', 'user__username', 'vapi_phone_number_id', 'friendly_name']
    readonly_fields = ['vapi_phone_number_id', 'created_at', 'updated_at']


@admin.register(InterviewCall)
class InterviewCallAdmin(admin.ModelAdmin):
    list_display = ['customer_number', 'user', 'assistant', 'status', 'outcome_status', 'cost', 'duration_formatted', 'created_at']
    list_filter = ['status', 'outcome_status', 'created_at']
    search_fields = ['customer_number', 'user__username', 'vapi_call_id', 'assistant__name']
    readonly_fields = ['vapi_call_id', 'created_at', 'started_at', 'ended_at', 'duration_formatted']
    fieldsets = (
        ('Call Information', {
            'fields': ('user', 'vapi_call_id', 'assistant', 'phone_number', 'customer_number')
        }),
        ('Call Status', {
            'fields': ('status', 'outcome_status', 'outcome_description')
        }),
        ('Timing', {
            'fields': ('created_at', 'started_at', 'ended_at', 'duration_seconds', 'duration_formatted')
        }),
        ('Results', {
            'fields': ('cost', 'end_reason', 'transcript_text'),
            'classes': ('collapse',)
        }),
        ('Technical Data', {
            'fields': ('transcript', 'cost_breakdown', 'raw_call_data'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'assistant', 'phone_number')
