from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

class Organization(models.Model):
    """Model for transport companies or training organizations."""
    name = models.CharField(max_length=255, unique=True)
    address = models.TextField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = _('Organization')
        verbose_name_plural = _('Organizations')

    def __str__(self):
        return self.name


class UserRole(models.Model):
    """Model for user roles (Admin, Trainer, Viewer)."""
    ROLE_CHOICES = [
        ('admin', _('Administrator')),
        ('trainer', _('Trainer')),
        ('viewer', _('Viewer')),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='role')
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, null=True, blank=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='viewer')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('User Role')
        verbose_name_plural = _('User Roles')

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.get_role_display()}"

    def is_admin(self):
        return self.role == 'admin'

    def is_trainer(self):
        return self.role == 'trainer'

    def is_viewer(self):
        return self.role == 'viewer'
