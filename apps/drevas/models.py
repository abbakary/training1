from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.core.models import Organization

class Dreva(models.Model):
    """Model for truck drivers (Drevas)."""
    STATUS_CHOICES = [
        ('in_training', _('In Training')),
        ('passed', _('Passed')),
        ('failed', _('Failed')),
        ('suspended', _('Suspended')),
    ]
    
    full_name = models.CharField(max_length=255)
    driver_id = models.CharField(max_length=50, unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='drevas')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='in_training')
    profile_photo = models.ImageField(upload_to='drevas/photos/', blank=True, null=True)
    date_enrolled = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date_enrolled']
        verbose_name = _('Dreva')
        verbose_name_plural = _('Drevas')
        unique_together = ('driver_id', 'organization')
        indexes = [
            models.Index(fields=['driver_id']),
            models.Index(fields=['organization']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.full_name} ({self.driver_id})"

    def get_total_exams(self):
        """Get total number of exams taken."""
        return self.examresult_set.count()

    def get_passed_exams(self):
        """Get number of passed exams."""
        return self.examresult_set.filter(status='passed').count()

    def get_failed_exams(self):
        """Get number of failed exams."""
        return self.examresult_set.filter(status='failed').count()

    def get_average_score(self):
        """Get average exam score."""
        results = self.examresult_set.all()
        if results.exists():
            total = sum(r.obtained_marks for r in results)
            return round(total / results.count(), 2)
        return 0


class TrainingSession(models.Model):
    """Model for training sessions/batches."""
    name = models.CharField(max_length=255)
    period = models.CharField(max_length=100, blank=True)
    start_date = models.DateField()
    end_date = models.DateField()
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='training_sessions')
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-start_date']
        verbose_name = _('Training Session')
        verbose_name_plural = _('Training Sessions')
        indexes = [
            models.Index(fields=['start_date']),
            models.Index(fields=['organization']),
        ]

    def __str__(self):
        return f"{self.name} ({self.period})"

    def get_enrolled_drevas(self):
        """Get all drevas enrolled in this session."""
        return self.sessionenrollment_set.select_related('dreva')

    def get_total_exams(self):
        """Get total exams in this session."""
        return self.exam_set.count()


class SessionEnrollment(models.Model):
    """Model for dreva enrollment in training sessions."""
    dreva = models.ForeignKey(Dreva, on_delete=models.CASCADE)
    training_session = models.ForeignKey(TrainingSession, on_delete=models.CASCADE, related_name='sessionenrollment_set')
    enrollment_date = models.DateTimeField(auto_now_add=True)
    completion_date = models.DateField(blank=True, null=True)

    class Meta:
        unique_together = ('dreva', 'training_session')
        verbose_name = _('Session Enrollment')
        verbose_name_plural = _('Session Enrollments')

    def __str__(self):
        return f"{self.dreva} - {self.training_session}"
