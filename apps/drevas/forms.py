from django import forms
from .models import Dreva, TrainingSession, SessionEnrollment

class DrevaForm(forms.ModelForm):
    """Form for creating/updating drevas."""
    class Meta:
        model = Dreva
        fields = ['full_name', 'driver_id', 'phone', 'email', 'organization', 'status', 'profile_photo']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'driver_id': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'organization': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'profile_photo': forms.FileInput(attrs={'class': 'form-control'}),
        }

class DrevaSearchForm(forms.Form):
    """Form for searching drevas."""
    search_query = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by name, ID or email'
        })
    )
    organization = forms.ModelChoiceField(
        queryset=None,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    status = forms.ChoiceField(
        choices=[('', 'All Status')] + Dreva.STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    def __init__(self, *args, **kwargs):
        organization = kwargs.pop('organization', None)
        super().__init__(*args, **kwargs)
        if organization:
            self.fields['organization'].queryset = TrainingSession.objects.filter(
                organization=organization
            ).values_list('organization', flat=True).distinct()

class TrainingSessionForm(forms.ModelForm):
    """Form for creating/updating training sessions."""
    class Meta:
        model = TrainingSession
        fields = ['name', 'period', 'start_date', 'end_date', 'organization', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'period': forms.TextInput(attrs={'class': 'form-control'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'organization': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class SessionEnrollmentForm(forms.ModelForm):
    """Form for session enrollment."""
    class Meta:
        model = SessionEnrollment
        fields = ['dreva', 'training_session']
        widgets = {
            'dreva': forms.Select(attrs={'class': 'form-control'}),
            'training_session': forms.Select(attrs={'class': 'form-control'}),
        }
