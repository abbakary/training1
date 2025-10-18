from django.contrib import admin
from .models import Dreva, TrainingSession, SessionEnrollment

@admin.register(Dreva)
class DrevaAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'driver_id', 'organization', 'status', 'date_enrolled')
    list_filter = ('status', 'organization', 'date_enrolled')
    search_fields = ('full_name', 'driver_id', 'email', 'phone')
    readonly_fields = ('date_enrolled', 'date_updated')
    fieldsets = (
        ('Personal Information', {
            'fields': ('full_name', 'driver_id', 'phone', 'email', 'profile_photo')
        }),
        ('Organization & Status', {
            'fields': ('organization', 'status')
        }),
        ('Timestamps', {
            'fields': ('date_enrolled', 'date_updated'),
            'classes': ('collapse',)
        }),
    )

@admin.register(TrainingSession)
class TrainingSessionAdmin(admin.ModelAdmin):
    list_display = ('name', 'organization', 'period', 'start_date', 'end_date')
    list_filter = ('organization', 'start_date')
    search_fields = ('name', 'period')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Session Information', {
            'fields': ('name', 'period', 'organization')
        }),
        ('Dates', {
            'fields': ('start_date', 'end_date')
        }),
        ('Description', {
            'fields': ('description',),
            'classes': ('wide',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(SessionEnrollment)
class SessionEnrollmentAdmin(admin.ModelAdmin):
    list_display = ('dreva', 'training_session', 'enrollment_date', 'completion_date')
    list_filter = ('training_session', 'enrollment_date')
    search_fields = ('dreva__full_name', 'training_session__name')
    readonly_fields = ('enrollment_date',)
