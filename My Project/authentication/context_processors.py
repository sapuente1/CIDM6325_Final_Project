def user_role_context(request):
    """Add user role information to all template contexts"""
    if not request.user.is_authenticated:
        return {
            'is_donor': False,
            'is_pantry': False,
            'is_admin': False,
            'user_role': None,
            'user_organization': None,
        }
    
    user = request.user
    context = {
        'is_donor': hasattr(user, 'donor'),
        'is_pantry': hasattr(user, 'pantry'),
        'is_admin': user.is_staff,
    }
    
    # Add role-specific information
    if context['is_donor']:
        context['user_role'] = 'donor'
        context['user_organization'] = user.donor.organization_name
    elif context['is_pantry']:
        context['user_role'] = 'pantry'
        context['user_organization'] = user.pantry.organization_name
    elif context['is_admin']:
        context['user_role'] = 'admin'
        context['user_organization'] = 'Administrator'
    else:
        context['user_role'] = 'unknown'
        context['user_organization'] = user.get_full_name() or user.username
    
    return context