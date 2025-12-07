# ADR-002: Django Views Architecture Strategy

**Date**: 2025-12-07  
**Status**: Proposed  
**Related PRD**: Section 6 (FR-001, FR-006), Section 4 (Django CBVs)

## Context

The CFMP requires a views architecture that supports CRUD operations for donations and pantries while maintaining clean, maintainable code. Key requirements include:

- Generic CBVs for all CRUD operations (FR-001)
- Named URL patterns with proper reversing (FR-006)
- Role-based access control
- Form validation integration
- Template consistency across user roles

## Decision Drivers

- **Maintainability**: Consistent patterns reduce cognitive load
- **Django Best Practices**: Leverage framework capabilities effectively
- **Code Reuse**: Minimize duplication across similar operations
- **Performance**: Efficient view implementations
- **Academic Requirements**: Demonstrate mastery of CBV concepts from rubric

## Options Considered

### A) Function-Based Views Only
```python
def create_donation(request):
    if request.method == 'POST':
        form = DonationForm(request.POST)
        if form.is_valid():
            # save logic
            return redirect('donations:detail', pk=donation.pk)
    else:
        form = DonationForm()
    return render(request, 'donations/create.html', {'form': form})
```

**Pros**: Explicit control, familiar pattern  
**Cons**: Repetitive boilerplate, harder to maintain, doesn't meet CBV requirement

### B) Generic CBVs with Mixins
```python
class DonationCreateView(LoginRequiredMixin, CreateView):
    model = Donation
    form_class = DonationForm
    template_name = 'donations/create.html'
    success_url = reverse_lazy('donations:list')
    
    def form_valid(self, form):
        form.instance.donor = self.request.user.donor
        return super().form_valid(form)

class DonationListView(ListView):
    model = Donation
    template_name = 'donations/list.html'
    context_object_name = 'donations'
    paginate_by = 20
    
    def get_queryset(self):
        return Donation.objects.available().select_related('donor')
```

**Pros**: Leverages Django patterns, less boilerplate, automatic CRUD  
**Cons**: Less explicit control, learning curve for customization

### C) Hybrid Approach (CBVs + FBVs)
Use CBVs for standard CRUD, FBVs for complex business logic

**Pros**: Best of both approaches  
**Cons**: Inconsistent patterns, doesn't fully demonstrate CBV mastery

## Decision

**We choose Option B (Generic CBVs with Mixins)** because:

1. **Meets Requirements**: Directly fulfills FR-001 requirement for Generic CBVs
2. **Django Best Practices**: Leverages framework capabilities as intended
3. **Maintainability**: Consistent patterns across all CRUD operations
4. **Academic Value**: Demonstrates mastery of CBV concepts required by rubric
5. **Built-in Features**: Automatic pagination, form handling, and template rendering

## Implementation Strategy

### View Hierarchy
```
donations/
├── views.py
│   ├── DonationListView (ListView)
│   ├── DonationCreateView (CreateView)
│   ├── DonationDetailView (DetailView)
│   ├── DonationUpdateView (UpdateView)
│   └── DonationDeleteView (DeleteView)
└── urls.py (named URL patterns)

pantries/
├── views.py
│   ├── PantryListView
│   ├── PantryCreateView (registration)
│   ├── PantryDetailView (profile)
│   └── PantryUpdateView
└── urls.py
```

### Named URL Strategy
```python
# donations/urls.py
app_name = 'donations'
urlpatterns = [
    path('', DonationListView.as_view(), name='list'),
    path('create/', DonationCreateView.as_view(), name='create'),
    path('<int:pk>/', DonationDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', DonationUpdateView.as_view(), name='update'),
    path('<int:pk>/delete/', DonationDeleteView.as_view(), name='delete'),
]

# Usage in templates: {% url 'donations:create' %}
# Usage in views: reverse('donations:detail', kwargs={'pk': donation.pk})
```

### Common Mixins
```python
class DonorRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return hasattr(self.request.user, 'donor')

class PantryRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return hasattr(self.request.user, 'pantry')
```

## Consequences

**Positive**:
- Consistent CRUD patterns across all models
- Automatic handling of common operations (pagination, form rendering)
- Named URLs enable flexible template and view development
- Mixins provide reusable authorization patterns
- Meets all academic requirements for CBV demonstration

**Negative**:
- Less explicit control over request/response cycle
- Customization requires understanding of CBV method resolution order
- May be overkill for simple views

**Implementation Notes**:
- Use `select_related()` in get_queryset() for performance
- Override `get_context_data()` for additional template context
- Use `form_valid()` for business logic after form validation
- Leverage `success_url` and `reverse_lazy()` for redirects

## Validation Plan

- Create Django TestCase for each CBV using `Client` requests
- Test named URL reversing in both views and templates
- Verify mixin authorization works correctly
- Performance testing with pagination and select_related

## Alternative Considerations

If CBVs prove too limiting for specific business logic:
- Override specific methods (get_queryset, form_valid, etc.)
- Add custom context in get_context_data()
- Use method decorators for additional functionality
- Consider custom mixins for complex authorization logic

This approach provides the flexibility to handle edge cases while maintaining the consistency and academic value of the CBV approach.