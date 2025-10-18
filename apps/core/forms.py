from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from .models import Organization, UserRole

class LoginForm(AuthenticationForm):
    """Custom login form."""
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Username or Email'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password'
        })
    )

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        if username and password:
            try:
                # If an email is entered, map it to the corresponding username
                if '@' in username and not User.objects.filter(username=username).exists():
                    user_obj = User.objects.get(email__iexact=username)
                    self.cleaned_data['username'] = user_obj.username
            except User.DoesNotExist:
                pass
        return super().clean()

class OrganizationForm(forms.ModelForm):
    """Form for creating/updating organizations."""
    class Meta:
        model = Organization
        fields = ['name', 'address', 'phone', 'email']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }
