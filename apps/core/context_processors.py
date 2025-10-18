from .models import UserRole


def user_context(request):
    user_role = None
    organization = None
    user = getattr(request, 'user', None)
    if user and user.is_authenticated:
        try:
            user_role = user.role
            organization = user_role.organization
        except UserRole.DoesNotExist:
            user_role = None
            organization = None
    return {
        'user_role': user_role,
        'organization': organization,
    }
