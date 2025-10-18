from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.db.models import Q
from django.core.files.base import ContentFile
from apps.core.models import UserRole
from apps.drevas.models import Dreva, TrainingSession
from .models import Exam, ExamQuestion, ExamAssignment
from .forms import ExamForm, ExamQuestionFormSet, ExamAssignmentForm, BulkExamAssignmentForm
from .utils import generate_exam_paper_pdf

@login_required
def exam_list_view(request):
    """List all exams for the organization."""
    try:
        user_role = request.user.role
        organization = user_role.organization
    except UserRole.DoesNotExist:
        return redirect('core:login')
    
    exams = Exam.objects.filter(training_session__organization=organization)
    
    # Filter by session
    session_id = request.GET.get('session')
    if session_id:
        exams = exams.filter(training_session_id=session_id)
    
    # Search
    search = request.GET.get('search')
    if search:
        exams = exams.filter(Q(title__icontains=search) | Q(subject__icontains=search))
    
    sessions = TrainingSession.objects.filter(organization=organization)
    
    context = {
        'exams': exams,
        'sessions': sessions,
        'selected_session': session_id,
    }
    return render(request, 'exams/exam_list.html', context)

@login_required
def exam_detail_view(request, exam_id):
    """Display exam details."""
    try:
        user_role = request.user.role
        organization = user_role.organization
    except UserRole.DoesNotExist:
        return redirect('core:login')
    
    exam = get_object_or_404(Exam, id=exam_id, training_session__organization=organization)
    questions = ExamQuestion.objects.filter(exam=exam).order_by('question_number')
    assignments = ExamAssignment.objects.filter(exam=exam).select_related('dreva')
    
    context = {
        'exam': exam,
        'questions': questions,
        'assignments': assignments,
        'total_assignments': assignments.count(),
    }
    return render(request, 'exams/exam_detail.html', context)

@login_required
def exam_create_view(request):
    """Create a new exam."""
    try:
        user_role = request.user.role
        if not user_role.is_trainer() and not user_role.is_admin():
            return redirect('core:dashboard')
        organization = user_role.organization
    except UserRole.DoesNotExist:
        return redirect('core:login')
    
    if request.method == 'POST':
        form = ExamForm(request.POST)
        formset = ExamQuestionFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            exam = form.save()
            formset.instance = exam
            formset.save()
            return redirect('exams:exam_detail', exam_id=exam.id)
    else:
        form = ExamForm()
        form.fields['training_session'].queryset = TrainingSession.objects.filter(
            organization=organization
        )
        formset = ExamQuestionFormSet()
    
    context = {
        'form': form,
        'formset': formset,
        'action': 'Create'
    }
    return render(request, 'exams/exam_form.html', context)

@login_required
def exam_assign_view(request, exam_id):
    """Assign exam to drevas."""
    try:
        user_role = request.user.role
        if not user_role.is_trainer() and not user_role.is_admin():
            return redirect('core:dashboard')
        organization = user_role.organization
    except UserRole.DoesNotExist:
        return redirect('core:login')
    
    exam = get_object_or_404(Exam, id=exam_id, training_session__organization=organization)
    
    # Get drevas from the training session
    drevas = Dreva.objects.filter(
        organization=organization,
        sessionenrollment__training_session=exam.training_session
    ).distinct()
    
    if request.method == 'POST':
        form = BulkExamAssignmentForm(request.POST, drevas_queryset=drevas)
        if form.is_valid():
            for dreva in form.cleaned_data['drevas']:
                ExamAssignment.objects.get_or_create(
                    exam=exam,
                    dreva=dreva,
                    defaults={'due_date': form.cleaned_data.get('due_date')}
                )
            return redirect('exams:exam_detail', exam_id=exam.id)
    else:
        form = BulkExamAssignmentForm(drevas_queryset=drevas)
    
    context = {
        'exam': exam,
        'form': form,
    }
    return render(request, 'exams/exam_assign.html', context)

@login_required
def generate_exam_paper_view(request, assignment_id):
    """Generate PDF exam paper for a dreva."""
    try:
        user_role = request.user.role
        organization = user_role.organization
    except UserRole.DoesNotExist:
        return redirect('core:login')
    
    assignment = get_object_or_404(
        ExamAssignment,
        id=assignment_id,
        exam__training_session__organization=organization
    )
    
    pdf_bytes = generate_exam_paper_pdf(assignment)

    # Save PDF to assignment if not already saved or if regeneration is desired
    filename = f"exam_{assignment.dreva.driver_id}_{assignment.exam.id}.pdf"
    assignment.exam_paper_pdf.save(filename, ContentFile(pdf_bytes), save=True)

    response = HttpResponse(pdf_bytes, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response
