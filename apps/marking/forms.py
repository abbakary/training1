from django import forms
from django.forms import inlineformset_factory
from .models import ExamResult, QuestionResponse

class ExamResultForm(forms.ModelForm):
    """Form for recording exam marks."""
    class Meta:
        model = ExamResult
        fields = ['obtained_marks', 'exam_date', 'marked_by', 'remarks', 'marked_exam_pdf']
        widgets = {
            'obtained_marks': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'max': '100'
            }),
            'exam_date': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'marked_by': forms.TextInput(attrs={'class': 'form-control'}),
            'remarks': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'marked_exam_pdf': forms.FileInput(attrs={'class': 'form-control'}),
        }

class QuestionResponseForm(forms.ModelForm):
    """Form for recording question responses and marks."""
    class Meta:
        model = QuestionResponse
        fields = ['marks_awarded', 'comments']
        widgets = {
            'marks_awarded': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0'
            }),
            'comments': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2
            }),
        }

QuestionResponseFormSet = inlineformset_factory(
    ExamResult,
    QuestionResponse,
    form=QuestionResponseForm,
    extra=0,
    can_delete=False
)

class ExamResultFilterForm(forms.Form):
    """Form for filtering exam results."""
    exam = forms.ModelChoiceField(
        queryset=None,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Exam'
    )
    status = forms.ChoiceField(
        choices=[('', 'All Status')] + ExamResult.STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Status'
    )
    dreva = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by driver name or ID'
        }),
        label='Driver'
    )
    
    def __init__(self, *args, **kwargs):
        exams_queryset = kwargs.pop('exams_queryset', None)
        super().__init__(*args, **kwargs)
        if exams_queryset:
            self.fields['exam'].queryset = exams_queryset
