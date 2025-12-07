# ADR-001: Data Model Design for CFMP

**Date**: 2025-12-07  
**Status**: Proposed  
**Related PRD**: Section 6 (FR-003), Section 4 (Custom QuerySets)

## Context

The Community Food Match Platform requires a data model that supports efficient donation matching between food donors and pantries. Key requirements include:

- Custom QuerySet methods for filtering (`near_expiry()`, `available()`)
- Location-based matching with privacy considerations
- Role-based access (donors, pantries, admins)
- Audit trail for donation lifecycle
- Support for bulk operations in Django Admin

## Decision Drivers

- **Performance**: Need efficient queries for time-sensitive donation matching
- **Privacy**: Balance location precision with user privacy requirements
- **Scalability**: Support for 500 concurrent users and growing donation volume
- **Maintainability**: Clear relationships and Django best practices
- **Business Logic**: Support expiry prioritization and claiming workflow

## Options Considered

### A) Simple Flat Model
```python
class Donation:
    donor = ForeignKey(User)
    pantry_claimer = ForeignKey(User, null=True)  # claimed by
    food_type = CharField()
    quantity = IntegerField()
    expiry_date = DateField()
    location_city = CharField()
    status = CharField(choices=STATUS_CHOICES)
```

**Pros**: Simple, easy to understand  
**Cons**: No separation of concerns, limited location flexibility, mixing user roles

### B) Role-Based Model with Separate Entities
```python
class Donor(Model):
    user = OneToOneField(User)
    organization_name = CharField()
    contact_info = JSONField()
    location = CharField()

class Pantry(Model):
    user = OneToOneField(User)
    organization_name = CharField()
    capacity = IntegerField()
    location = CharField()
    service_area = CharField()

class Donation(Model):
    donor = ForeignKey(Donor)
    claimed_by = ForeignKey(Pantry, null=True)
    food_items = JSONField()  # flexible food descriptions
    total_quantity = DecimalField()
    expiry_date = DateTimeField()
    location = CharField()
    status = CharField(choices=STATUS_CHOICES)
    created_at = DateTimeField(auto_now_add=True)
    claimed_at = DateTimeField(null=True)
```

**Pros**: Clear separation, extensible, supports business logic  
**Cons**: More complex joins, additional tables

## Decision

**We choose Option B (Role-Based Model)** because:

1. **Clear Separation**: Donor and Pantry roles have different attributes and behaviors
2. **Extensibility**: Easy to add role-specific features (capacity tracking, service areas)
3. **QuerySet Optimization**: Custom managers can optimize joins and filtering
4. **Business Logic Support**: Natural place for role-specific business methods
5. **Django Admin**: ModelAdmin can provide role-specific interfaces

## Implementation Details

### Custom Manager/QuerySet Methods
```python
class DonationQuerySet(models.QuerySet):
    def available(self):
        return self.filter(status='available', expiry_date__gte=timezone.now())
    
    def near_expiry(self, hours=24):
        cutoff = timezone.now() + timedelta(hours=hours)
        return self.available().filter(expiry_date__lte=cutoff)
    
    def by_location(self, city):
        return self.filter(location__icontains=city)

class DonationManager(models.Manager):
    def get_queryset(self):
        return DonationQuerySet(self.model, using=self._db)
    
    def available(self):
        return self.get_queryset().available()
    
    def urgent(self):
        return self.get_queryset().near_expiry(hours=12)
```

### Location Strategy
- **MVP**: City-level granularity stored as CharField
- **Privacy**: No coordinates or precise addresses
- **Matching**: Text-based filtering with `icontains` lookup
- **Future**: Consider postal code prefixes for better matching

## Consequences

**Positive**:
- Clear data model supports all PRD functional requirements
- Custom QuerySets enable efficient filtering as specified in FR-003
- Role separation supports authentication requirements in FR-005
- Extensible design accommodates Phase 2 features

**Negative**:
- Additional complexity requires proper foreign key management
- More database joins may impact performance (mitigated by select_related)
- Location text matching less precise than geographic queries

**Risks**:
- Location matching accuracy depends on consistent city name entry
- JSON fields for food_items may complicate searching (consider separate model in future)

## Validation Plan

- Create Django TestCase for all QuerySet methods
- Performance testing with 1000+ donation records
- Admin interface testing for bulk operations
- Location matching accuracy testing with real city names

## Rollback Plan

- Database migrations are reversible
- If performance issues arise, can optimize with database indexes
- Location strategy can be enhanced without model changes (CharField supports future coordinate storage)