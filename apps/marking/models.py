from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from apps.drevas.models import Dreva
from apps.exams.models import Exam

class ExamResult(models.Model):
    """Model for exam results and marks."""
    STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('passed', _('Passed')),
        ('failed', _('Failed')),
    ]
    
    dreva = models.ForeignKey(Dreva, on_delete=models.CASCADE, related_name='examresult_set')
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='examresult_set')
    obtained_marks = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        blank=True,
        null=True
    )
    total_marks = models.IntegerField(default=100)
    percentage = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    exam_date = models.DateTimeField(blank=True, null=True)
    marking_date = models.DateTimeField(blank=True, null=True)
    marked_by = models.CharField(max_length=255, blank=True, null=True)
    remarks = models.TextField(blank=True, null=True)
    marked_exam_pdf = models.FileField(upload_to='marked_exams/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-exam_date']
        verbose_name = _('Exam Result')
        verbose_name_plural = _('Exam Results')
        unique_together = ('dreva', 'exam')
        indexes = [
            models.Index(fields=['dreva', 'exam']),
            models.Index(fields=['status']),
            models.Index(fields=['exam_date']),
        ]

    def __str__(self):
        return f"{self.dreva} - {self.exam}: {self.obtained_marks}/{self.total_marks}"

    def save(self, *args, **kwargs):
        """Override save to calculate percentage and status."""
        if self.obtained_marks is not None and self.total_marks:
            self.percentage = (self.obtained_marks / self.total_marks) * 100
            passing_marks = (self.exam.passing_percentage / 100) * self.total_marks
            self.status = 'passed' if self.obtained_marks >= passing_marks else 'failed'
        super().save(*args, **kwargs)
        
        # Update dreva status based on exam results
        self._update_dreva_status()

    def _update_dreva_status(self):
        """Update dreva status based on exam results."""
        total_exams = self.dreva.get_total_exams()
        passed_exams = self.dreva.get_passed_exams()
        
        if total_exams > 0:
            if passed_exams == total_exams:
                self.dreva.status = 'passed'
            elif self.dreva.get_failed_exams() > 0:
                if passed_exams > 0:
                    self.dreva.status = 'in_training'
                else:
                    self.dreva.status = 'failed'
            self.dreva.save()


class QuestionResponse(models.Model):
    """Model for storing answers to exam questions."""
    exam_result = models.ForeignKey(ExamResult, on_delete=models.CASCADE, related_name='responses')
    question = models.ForeignKey('exams.ExamQuestion', on_delete=models.CASCADE)
    answer_text = models.TextField()
    marks_awarded = models.IntegerField(blank=True, null=True)
    comments = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ('exam_result', 'question')
        verbose_name = _('Question Response')
        verbose_name_plural = _('Question Responses')

    def __str__(self):
        return f"{self.exam_result} - Q{self.question.question_number}"
