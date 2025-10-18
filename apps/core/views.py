from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from apps.drevas.models import Dreva, TrainingSession
from apps.exams.models import Exam, ExamAssignment
from apps.marking.models import ExamResult
from .forms import LoginForm
from .models import Organization, UserRole

@require_http_methods(["GET", "POST"])
def login_view(request):
    """User login view."""
    if request.user.is_authenticated:
        return redirect('core:dashboard')
    
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('core:dashboard')
    else:
        form = LoginForm()
    
    context = {'form': form}
    return render(request, 'core/login.html', context)

@login_required
def logout_view(request):
    """User logout view."""
    logout(request)
    return redirect('core:login')

@login_required
def dashboard_view(request):
    """Main dashboard view."""
    try:
        user_role = request.user.role
    except UserRole.DoesNotExist:
        return redirect('login')
    
    organization = user_role.organization
    
    context = {
        'user_role': user_role,
        'organization': organization,
    }
    
    if user_role.is_admin():
        # Admin dashboard
        context.update({
            'total_drevas': Dreva.objects.filter(organization=organization).count(),
            'total_sessions': TrainingSession.objects.filter(organization=organization).count(),
            'total_exams': Exam.objects.filter(training_session__organization=organization).count(),
            'total_results': ExamResult.objects.filter(dreva__organization=organization).count(),
            'pending_results': ExamResult.objects.filter(
                dreva__organization=organization,
                status='pending'
            ).count(),
            'recent_drevas': Dreva.objects.filter(organization=organization)[:5],
            'recent_results': ExamResult.objects.filter(
                dreva__organization=organization
            ).select_related('dreva', 'exam')[:5],
        })
    elif user_role.is_trainer():
        # Trainer dashboard
        context.update({
            'pending_exams': ExamAssignment.objects.filter(
                exam__training_session__organization=organization,
                status='completed'
            ).count(),
            'marked_exams': ExamResult.objects.filter(
                dreva__organization=organization,
                status__in=['passed', 'failed']
            ).count(),
            'recent_assignments': ExamAssignment.objects.filter(
                exam__training_session__organization=organization
            ).select_related('exam', 'dreva')[:5],
        })
    
    return render(request, 'core/dashboard.html', context)

@login_required
def organization_list_view(request):
    """List all organizations (admin only)."""
    try:
        user_role = request.user.role
        if not user_role.is_admin():
            return redirect('core:dashboard')
    except UserRole.DoesNotExist:
        return redirect('login')
    
    organizations = Organization.objects.all()
    context = {'organizations': organizations}
    return render(request, 'core/organization_list.html', context)
