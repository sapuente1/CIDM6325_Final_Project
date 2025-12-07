# BRIEF: Enhance Donation Models with Business Logic

**Date**: 2025-12-07  
**Related ADR**: ADR-012 Data Management and Business Logic  
**PRD Section**: Section 3 (Core Functionality), Section 4 (Business Logic), Section 5 (Data Management)

## Goal

Implement comprehensive business logic, data validation, and management features for the CFMP donation system following the patterns established in ADR-012.

## Scope (Single Implementation)

### Files to Modify/Create:
- `donations/models.py` - Enhanced models with business logic
- `donations/managers.py` - Custom managers and querysets (NEW)
- `donations/validators.py` - Model validators (NEW)
- `donations/analytics.py` - Analytics service (NEW)
- `donations/management/commands/process_expired_donations.py` - Expiry processing (NEW)
- `donations/management/commands/cleanup_old_data.py` - Data cleanup (NEW)
- Update migration files as needed

### Non-Goals:
- UI changes (keep existing templates)
- Authentication system changes
- New views or URLs

## Standards

- **Django ORM**: Use custom managers and querysets for business logic
- **Validation**: Model-level validation with custom validators
- **Transactions**: Use atomic transactions for business operations
- **Performance**: Add database indexes for common queries
- **Testing**: Include comprehensive tests for business logic

## Implementation Tasks

### 1. Enhanced Donation Model

**Objective**: Replace basic Donation model with rich domain model including business logic, custom managers, and validation.

**Key Features**:
- UUID primary keys for security
- Custom DonationManager with business queries
- Business methods: `claim()`, `fulfill()`, `expire()`, `cancel()`
- Status transition validation
- Property methods for calculated fields
- Database indexes for performance

**Validation Rules**:
- Expiry date must be in future
- Positive quantities only
- Valid status transitions only
- Business rule enforcement

### 2. Enhanced Donor and Pantry Models

**Objective**: Add business logic and analytics capabilities to user models.

**Key Features**:
- Custom querysets for filtering and aggregation
- Statistics methods for reporting
- Capacity management for pantries
- Business validation rules

### 3. Management Commands

**Objective**: Create automated data management commands.

**Commands**:
- `process_expired_donations` - Expire old donations automatically
- `cleanup_old_data` - Remove old fulfilled/expired records

### 4. Analytics Service

**Objective**: Centralized analytics for business intelligence.

**Features**:
- Platform statistics
- Claim rate analysis
- Geographic distribution
- Food type analytics
- Performance metrics

### 5. Validators

**Objective**: Reusable validation functions.

**Validators**:
- Future date validation
- Phone number validation
- Positive quantity validation
- Business rule validation

## Prompts for AI Implementation

### Phase 1: Core Model Enhancement

```
Update the Donation model in donations/models.py to implement the enhanced version from ADR-012. Include:

1. UUID primary key
2. Enhanced field definitions with choices
3. Custom DonationQuerySet with business queries (available, expiring_soon, expired, etc.)
4. Custom DonationManager with business methods
5. Business logic methods: claim(), fulfill(), expire(), cancel()
6. Model validation in clean() method
7. Property methods for calculated fields
8. Database indexes in Meta class
9. Proper __str__ and get_absolute_url methods

Ensure all business logic follows Django best practices and includes proper error handling.
```

### Phase 2: Enhanced User Models

```
Update Donor and Pantry models in donations/models.py to add:

1. Custom querysets for business filtering
2. Statistics methods (get_donation_stats, get_claim_stats)
3. Business validation methods
4. Enhanced field definitions
5. Database indexes for performance
6. Proper relationships with Donation model

Maintain backward compatibility with existing data structure.
```

### Phase 3: Validators and Utilities

```
Create donations/validators.py with reusable validation functions:

1. validate_future_date
2. validate_reasonable_expiry  
3. validate_phone_number
4. validate_positive_quantity

Create donations/analytics.py with DonationAnalytics class containing:

1. Platform statistics methods
2. Claim rate calculations
3. Geographic and food type distributions
4. Performance metrics
5. Donor leaderboards

Use Django ORM aggregation and annotation features effectively.
```

### Phase 4: Management Commands

```
Create management commands in donations/management/commands/:

1. process_expired_donations.py - Command to expire old donations with dry-run option
2. cleanup_old_data.py - Command to clean old fulfilled/expired records

Include proper argument parsing, error handling, and informative output. Follow Django management command best practices.
```

### Phase 5: Database Migration

```
Generate and review Django migrations for the model changes:

1. Run makemigrations to create migration files
2. Review migrations for data safety
3. Add any custom migration operations needed
4. Test migrations on development database

Ensure migrations handle existing data properly and don't cause data loss.
```

## Acceptance Criteria

### Model Functionality
- [x] Donations can be claimed, fulfilled, expired, and cancelled through business methods
- [x] Status transitions are validated according to business rules
- [x] Custom querysets provide efficient filtering (available, expiring_soon, etc.)
- [x] Model validation prevents invalid data entry
- [x] Analytics methods return accurate statistics

### Data Integrity
- [x] All business operations use atomic transactions
- [x] Model validation prevents invalid state transitions
- [x] Database constraints enforce data integrity
- [x] Existing data remains compatible

### Performance
- [x] Database indexes support common query patterns
- [x] Custom managers optimize frequent operations
- [x] Analytics queries use proper aggregation
- [x] No N+1 query problems in business methods

### Management Commands
- [x] Commands execute without errors
- [x] Dry-run mode works correctly
- [x] Proper logging and error handling
- [x] Commands are schedulable via cron/task scheduler

## Testing Requirements

Create comprehensive tests in `donations/tests/test_models.py`:

```python
class DonationBusinessLogicTests(TestCase):
    def test_claim_donation_success(self):
        # Test successful claiming
        
    def test_claim_expired_donation_fails(self):
        # Test business rule validation
        
    def test_status_transition_validation(self):
        # Test state machine validation
        
    def test_custom_querysets(self):
        # Test manager methods
        
    def test_analytics_calculations(self):
        # Test analytics accuracy
```

## Validation Steps

1. **Model Tests**: All business logic unit tests pass
2. **Migration Safety**: Migrations apply cleanly without data loss
3. **Performance**: Query count remains reasonable for common operations
4. **Integration**: Existing views and templates continue to work
5. **Management Commands**: Commands execute successfully in development

## Rollback Plan

If issues arise:
1. Revert to previous migration
2. Restore from database backup if needed
3. Use git to revert model changes
4. Disable new management commands in production

## Implementation Notes

- **Phase Implementation**: Implement in phases to minimize risk
- **Backward Compatibility**: Ensure existing code continues to work
- **Testing**: Test each phase thoroughly before proceeding
- **Performance**: Monitor query performance after implementation
- **Documentation**: Update docstrings and comments for new functionality

This brief provides a comprehensive roadmap for implementing the enhanced donation management system while maintaining system stability and following Django best practices.