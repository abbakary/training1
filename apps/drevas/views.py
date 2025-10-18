from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import JsonResponse
from apps.core.models import UserRole
from apps.marking.models import ExamResult
from .models import Dreva, TrainingSession, SessionEnrollment
from .forms import DrevaForm, DrevaSearchForm, TrainingSessionForm, SessionEnrollmentForm

@login_required
def dreva_list_view(request):
    """List all drevas for the organization."""
    try:
        user_role = request.user.role
        organization = user_role.organization
    except UserRole.DoesNotExist:
        return redirect('login')
    
    drevas = Dreva.objects.filter(organization=organization)
    form = DrevaSearchForm(request.GET, organization=organization)
    
    if request.GET.get('search_query'):
        query = request.GET.get('search_query')
        drevas = drevas.filter(
            Q(full_name__icontains=query) |
            Q(driver_id__icontains=query) |
            Q(email__icontains=query)
        )
    
    if request.GET.get('status'):
        drevas = drevas.filter(status=request.GET.get('status'))
    
    context = {
        'drevas': drevas,
        'form': form,
        'total_count': drevas.count(),
    }
    return render(request, 'drevas/dreva_list.html', context)

@login_required
def dreva_detail_view(request, dreva_id):
    """Display dreva profile and exam history."""
    try:
        user_role = request.user.role
        organization = user_role.organization
    except UserRole.DoesNotExist:
        return redirect('login')
    
    dreva = get_object_or_404(Dreva, id=dreva_id, organization=organization)
    exam_results = ExamResult.objects.filter(dreva=dreva).select_related('exam')
    sessions = SessionEnrollment.objects.filter(dreva=dreva).select_related('training_session')
    
    statistics = {
        'total_exams': dreva.get_total_exams(),
        'passed_exams': dreva.get_passed_exams(),
        'failed_exams': dreva.get_failed_exams(),
        'average_score': dreva.get_average_score(),
    }
    
    context = {
        'dreva': dreva,
        'exam_results': exam_results,
        'sessions': sessions,
        'statistics': statistics,
    }
    return render(request, 'drevas/dreva_detail.html', context)

@login_required
def dreva_create_view(request):
    """Create a new dreva."""
    try:
        user_role = request.user.role
        if not user_role.is_admin():
            return redirect('core:dashboard')
        organization = user_role.organization
    except UserRole.DoesNotExist:
        return redirect('login')
    
    if request.method == 'POST':
        form = DrevaForm(request.POST, request.FILES)
        if form.is_valid():
            dreva = form.save(commit=False)
            dreva.organization = organization
            dreva.save()
            return redirect('drevas:dreva_detail', dreva_id=dreva.id)
    else:
        form = DrevaForm()
        form.fields['organization'].initial = organization
    
    context = {'form': form, 'action': 'Create'}
    return render(request, 'drevas/dreva_form.html', context)

@login_required
def dreva_edit_view(request, dreva_id):
    """Edit dreva information."""
    try:
        user_role = request.user.role
        if not user_role.is_admin():
            return redirect('core:dashboard')
        organization = user_role.organization
    except UserRole.DoesNotExist:
        return redirect('login')
    
    dreva = get_object_or_404(Dreva, id=dreva_id, organization=organization)
    
    if request.method == 'POST':
        form = DrevaForm(request.POST, request.FILES, instance=dreva)
        if form.is_valid():
            form.save()
            return redirect('drevas:dreva_detail', dreva_id=dreva.id)
    else:
        form = DrevaForm(instance=dreva)
    
    context = {'form': form, 'dreva': dreva, 'action': 'Edit'}
    return render(request, 'drevas/dreva_form.html', context)

@login_required
def training_session_list_view(request):
    """List all training sessions."""
    try:
        user_role = request.user.role
        organization = user_role.organization
    except UserRole.DoesNotExist:
        return redirect('login')
    
    sessions = TrainingSession.objects.filter(organization=organization)
    context = {'sessions': sessions}
    return render(request, 'drevas/session_list.html', context)

@login_required
def training_session_detail_view(request, session_id):
    """Display training session details."""
    try:
        user_role = request.user.role
        organization = user_role.organization
    except UserRole.DoesNotExist:
        return redirect('login')
    
    session = get_object_or_404(TrainingSession, id=session_id, organization=organization)
    enrollments = SessionEnrollment.objects.filter(training_session=session).select_related('dreva')
    exams = session.exam_set.all()
    
    context = {
        'session': session,
        'enrollments': enrollments,
        'exams': exams,
        'total_drevas': enrollments.count(),
    }
    return render(request, 'drevas/session_detail.html', context)

@login_required
def training_session_create_view(request):
    """Create a new training session."""
    try:
        user_role = request.user.role
        if not user_role.is_admin():
            return redirect('core:dashboard')
        organization = user_role.organization
    except UserRole.DoesNotExist:
        return redirect('login')
    
    if request.method == 'POST':
        form = TrainingSessionForm(request.POST)
        if form.is_valid():
            session = form.save(commit=False)
            session.organization = organization
            session.save()
            return redirect('drevas:session_detail', session_id=session.id)
    else:
        form = TrainingSessionForm()
        form.fields['organization'].initial = organization
    
    context = {'form': form, 'action': 'Create'}
    return render(request, 'drevas/session_form.html', context)
