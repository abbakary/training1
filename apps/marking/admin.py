from django.contrib import admin
from .models import ExamResult, QuestionResponse

@admin.register(ExamResult)
class ExamResultAdmin(admin.ModelAdmin):
    list_display = ('dreva', 'exam', 'obtained_marks', 'percentage', 'status', 'exam_date')
    list_filter = ('status', 'exam_date', 'marking_date')
    search_fields = ('dreva__full_name', 'exam__title')
    readonly_fields = ('created_at', 'updated_at', 'percentage')
    fieldsets = (
        ('Basic Information', {
            'fields': ('dreva', 'exam')
        }),
        ('Marks', {
            'fields': ('obtained_marks', 'total_marks', 'percentage', 'status')
        }),
        ('Marking Details', {
            'fields': ('exam_date', 'marking_date', 'marked_by', 'remarks')
        }),
        ('Document', {
            'fields': ('marked_exam_pdf',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(QuestionResponse)
class QuestionResponseAdmin(admin.ModelAdmin):
    list_display = ('exam_result', 'question', 'marks_awarded')
    list_filter = ('exam_result__exam', 'marks_awarded')
    search_fields = ('exam_result__dreva__full_name', 'question__question_text')
    readonly_fields = ('exam_result', 'question')
