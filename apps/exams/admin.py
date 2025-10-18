from django.contrib import admin
from .models import Exam, ExamQuestion, ExamAssignment

@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ('title', 'training_session', 'subject', 'max_marks', 'created_at')
    list_filter = ('training_session', 'created_at')
    search_fields = ('title', 'subject')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Exam Information', {
            'fields': ('title', 'subject', 'training_session')
        }),
        ('Settings', {
            'fields': ('max_marks', 'duration_minutes', 'passing_percentage')
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

@admin.register(ExamQuestion)
class ExamQuestionAdmin(admin.ModelAdmin):
    list_display = ('exam', 'question_number', 'question_type', 'marks')
    list_filter = ('exam', 'question_type')
    search_fields = ('exam__title', 'question_text')
    ordering = ('exam', 'question_number')

@admin.register(ExamAssignment)
class ExamAssignmentAdmin(admin.ModelAdmin):
    list_display = ('exam', 'dreva', 'status', 'assigned_date')
    list_filter = ('status', 'assigned_date')
    search_fields = ('exam__title', 'dreva__full_name')
    readonly_fields = ('assigned_date',)
