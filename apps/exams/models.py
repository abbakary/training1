from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.drevas.models import Dreva, TrainingSession

class Exam(models.Model):
    """Model for exams."""
    title = models.CharField(max_length=255)
    subject = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True, null=True)
    training_session = models.ForeignKey(TrainingSession, on_delete=models.CASCADE, related_name='exam_set')
    max_marks = models.IntegerField(default=100)
    duration_minutes = models.IntegerField(default=60)
    passing_percentage = models.IntegerField(default=40)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = _('Exam')
        verbose_name_plural = _('Exams')
        indexes = [
            models.Index(fields=['training_session']),
        ]

    def __str__(self):
        return f"{self.title} - {self.training_session}"

    def get_question_count(self):
        """Get total number of questions."""
        return self.examquestion_set.count()

    def get_total_marks(self):
        """Get total marks from all questions."""
        questions = self.examquestion_set.all()
        if questions.exists():
            return sum(q.marks for q in questions)
        return 0


class ExamQuestion(models.Model):
    """Model for exam questions."""
    QUESTION_TYPE_CHOICES = [
        ('short_answer', _('Short Answer')),
        ('essay', _('Essay')),
        ('mcq', _('Multiple Choice')),
        ('true_false', _('True/False')),
    ]
    
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='examquestion_set')
    question_number = models.IntegerField()
    question_text = models.TextField()
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPE_CHOICES, default='short_answer')
    marks = models.IntegerField(default=1)
    options = models.JSONField(null=True, blank=True, help_text="For MCQ: ['A', 'B', 'C', 'D']")
    correct_answer = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['question_number']
        verbose_name = _('Exam Question')
        verbose_name_plural = _('Exam Questions')
        unique_together = ('exam', 'question_number')

    def __str__(self):
        return f"{self.exam} - Q{self.question_number}"


class ExamAssignment(models.Model):
    """Model for assigning exams to drevas."""
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='examassignment_set')
    dreva = models.ForeignKey(Dreva, on_delete=models.CASCADE, related_name='examassignment_set')
    assigned_date = models.DateTimeField(auto_now_add=True)
    due_date = models.DateField(blank=True, null=True)
    exam_paper_pdf = models.FileField(upload_to='exam_papers/', blank=True, null=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', _('Pending')),
            ('completed', _('Completed')),
            ('marked', _('Marked')),
        ],
        default='pending'
    )

    class Meta:
        unique_together = ('exam', 'dreva')
        verbose_name = _('Exam Assignment')
        verbose_name_plural = _('Exam Assignments')

    def __str__(self):
        return f"{self.exam} - {self.dreva}"
