from django import forms
from django.forms import inlineformset_factory
from .models import Exam, ExamQuestion, ExamAssignment

class ExamForm(forms.ModelForm):
    """Form for creating/updating exams."""
    class Meta:
        model = Exam
        fields = ['title', 'subject', 'training_session', 'max_marks', 'duration_minutes', 'passing_percentage', 'description']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'subject': forms.TextInput(attrs={'class': 'form-control'}),
            'training_session': forms.Select(attrs={'class': 'form-control'}),
            'max_marks': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'duration_minutes': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'passing_percentage': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'max': '100'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class ExamQuestionForm(forms.ModelForm):
    """Form for exam questions."""
    class Meta:
        model = ExamQuestion
        fields = ['question_number', 'question_text', 'question_type', 'marks', 'options', 'correct_answer']
        widgets = {
            'question_number': forms.NumberInput(attrs={'class': 'form-control'}),
            'question_text': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'question_type': forms.Select(attrs={'class': 'form-control'}),
            'marks': forms.NumberInput(attrs={'class': 'form-control'}),
            'options': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'correct_answer': forms.TextInput(attrs={'class': 'form-control'}),
        }

ExamQuestionFormSet = inlineformset_factory(Exam, ExamQuestion, form=ExamQuestionForm, extra=1)

class ExamAssignmentForm(forms.ModelForm):
    """Form for assigning exams to drevas."""
    class Meta:
        model = ExamAssignment
        fields = ['dreva', 'due_date']
        widgets = {
            'dreva': forms.Select(attrs={'class': 'form-control'}),
            'due_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

class BulkExamAssignmentForm(forms.Form):
    """Form for bulk assigning exams to multiple drevas."""
    drevas = forms.ModelMultipleChoiceField(
        queryset=None,
        widget=forms.CheckboxSelectMultiple,
        label="Select Drevas"
    )
    due_date = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        required=False
    )
    
    def __init__(self, *args, **kwargs):
        drevas_queryset = kwargs.pop('drevas_queryset', None)
        super().__init__(*args, **kwargs)
        if drevas_queryset:
            self.fields['drevas'].queryset = drevas_queryset
