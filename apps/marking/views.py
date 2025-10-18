from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from apps.core.models import UserRole
from apps.exams.models import Exam, ExamAssignment
from apps.drevas.models import Dreva
from .models import ExamResult, QuestionResponse
from .forms import ExamResultForm, QuestionResponseFormSet, ExamResultFilterForm

@login_required
def exam_result_list_view(request):
    """List all exam results for the organization."""
    try:
        user_role = request.user.role
        organization = user_role.organization
    except UserRole.DoesNotExist:
        return redirect('login')
    
    results = ExamResult.objects.filter(
        dreva__organization=organization
    ).select_related('dreva', 'exam')
    
    # Get exams for filter
    exams = Exam.objects.filter(training_session__organization=organization)
    
    # Apply filters
    form = ExamResultFilterForm(request.GET, exams_queryset=exams)
    
    if request.GET.get('exam'):
        results = results.filter(exam_id=request.GET.get('exam'))
    
    if request.GET.get('status'):
        results = results.filter(status=request.GET.get('status'))
    
    if request.GET.get('dreva'):
        dreva_search = request.GET.get('dreva')
        results = results.filter(
            Q(dreva__full_name__icontains=dreva_search) |
            Q(dreva__driver_id__icontains=dreva_search)
        )
    
    # Sort by date
    results = results.order_by('-exam_date')
    
    context = {
        'results': results,
        'form': form,
        'total_results': results.count(),
    }
    return render(request, 'marking/result_list.html', context)

@login_required
def exam_result_detail_view(request, result_id):
    """Display exam result details."""
    try:
        user_role = request.user.role
        organization = user_role.organization
    except UserRole.DoesNotExist:
        return redirect('login')
    
    result = get_object_or_404(
        ExamResult,
        id=result_id,
        dreva__organization=organization
    )
    
    questions = result.exam.examquestion_set.all().order_by('question_number')
    responses = {r.question_id: r for r in result.responses.all()}
    
    context = {
        'result': result,
        'questions': questions,
        'responses': responses,
    }
    return render(request, 'marking/result_detail.html', context)

@login_required
def record_marks_view(request, assignment_id):
    """Record marks for an exam assignment."""
    try:
        user_role = request.user.role
        if not user_role.is_trainer() and not user_role.is_admin():
            return redirect('dashboard')
        organization = user_role.organization
    except UserRole.DoesNotExist:
        return redirect('login')
    
    assignment = get_object_or_404(
        ExamAssignment,
        id=assignment_id,
        exam__training_session__organization=organization
    )
    
    # Get or create exam result
    result, created = ExamResult.objects.get_or_create(
        dreva=assignment.dreva,
        exam=assignment.exam,
        defaults={'total_marks': assignment.exam.max_marks}
    )
    
    if request.method == 'POST':
        form = ExamResultForm(request.POST, request.FILES, instance=result)
        formset = QuestionResponseFormSet(request.POST, instance=result)
        
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            
            # Update assignment status
            assignment.status = 'marked'
            assignment.save()
            
            return redirect('marking:result_detail', result_id=result.id)
    else:
        form = ExamResultForm(instance=result)
        formset = QuestionResponseFormSet(instance=result)
    
    # Create question responses if they don't exist
    questions = assignment.exam.examquestion_set.all().order_by('question_number')
    for question in questions:
        QuestionResponse.objects.get_or_create(
            exam_result=result,
            question=question
        )
    
    # Re-create formset to include new responses
    formset = QuestionResponseFormSet(instance=result)
    
    context = {
        'form': form,
        'formset': formset,
        'assignment': assignment,
        'result': result,
    }
    return render(request, 'marking/record_marks.html', context)

@login_required
def dreva_progress_view(request, dreva_id):
    """Display dreva's overall progress and exam history."""
    try:
        user_role = request.user.role
        organization = user_role.organization
    except UserRole.DoesNotExist:
        return redirect('login')
    
    dreva = get_object_or_404(Dreva, id=dreva_id, organization=organization)
    
    results = ExamResult.objects.filter(dreva=dreva).select_related('exam').order_by('-exam_date')
    assignments = ExamAssignment.objects.filter(dreva=dreva).select_related('exam')
    
    stats = {
        'total_exams': dreva.get_total_exams(),
        'passed_exams': dreva.get_passed_exams(),
        'failed_exams': dreva.get_failed_exams(),
        'average_score': dreva.get_average_score(),
        'pending_exams': assignments.filter(status='pending').count(),
        'completed_exams': assignments.filter(status__in=['completed', 'marked']).count(),
    }
    
    context = {
        'dreva': dreva,
        'results': results,
        'assignments': assignments,
        'stats': stats,
    }
    return render(request, 'marking/dreva_progress.html', context)
