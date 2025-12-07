# BRIEF-006: Deployment and Environment Strategy Implementation

## Goal
Implement a comprehensive deployment and environment management strategy for CFMP based on ADR-006, enabling secure production deployment with proper secret management and environment separation.

## Scope (Single PR)
**Files to Create/Modify:**
- `cfmp/settings/__init__.py` - Environment-based settings loader
- `cfmp/settings/base.py` - Common Django settings
- `cfmp/settings/development.py` - Development-specific settings
- `cfmp/settings/production.py` - Production-specific settings  
- `manage.py` - Update for environment-based settings
- `.env.example` - Template for environment variables
- `deploy.sh` - Production deployment script
- `Procfile` - Platform deployment configuration
- `requirements.txt` - Update dependencies if needed

**Non-goals:**
- Actual platform deployment (focus on configuration)
- Database migration from existing SQLite
- SSL certificate setup

## Standards
- **Commits**: Conventional style (feat/fix/docs/refactor/chore)
- **Security**: No secrets in code; environment variables only
- **Django**: Follow Django deployment best practices
- **Academic**: Demonstrate deployment concepts from rubric baseline tier

## Acceptance Criteria

### Environment Management
- [x] Split settings architecture (base, development, production)
- [x] Environment variable management for secrets (SECRET_KEY, DB credentials)
- [x] Automatic environment detection via DJANGO_ENVIRONMENT
- [x] Development uses SQLite, production supports PostgreSQL
- [x] Static file serving configured with WhiteNoise

### Security Configuration
- [x] Production settings with DEBUG=False
- [x] Proper ALLOWED_HOSTS configuration
- [x] CSRF and XSS protection enabled
- [x] HTTPS settings ready for deployment
- [x] Secure cookie settings for production

### Development Efficiency  
- [x] Easy local development setup with sensible defaults
- [x] Console email backend for development
- [x] Local memory cache for development
- [x] Optional Django Debug Toolbar integration

### Production Readiness
- [x] PostgreSQL database configuration
- [x] Redis cache configuration  
- [x] SMTP email backend configuration
- [x] Static file compression and serving
- [x] Performance and security optimizations

### Deployment Support
- [x] Deployment script for production setup
- [x] Platform-specific configurations (Heroku, Railway)
- [x] Health check integration with monitoring system
- [x] Environment variable documentation

## Technical Implementation Details

### Settings Architecture
```
cfmp/settings/
├── __init__.py       # Environment detection and loading
├── base.py          # Common settings shared across environments
├── development.py   # Local development overrides
└── production.py    # Production security and performance settings
```

### Environment Variable Strategy
- **Development**: Optional .env file with sensible defaults
- **Production**: Required environment variables for all secrets
- **Secret Management**: No secrets committed to version control
- **Documentation**: .env.example template with all required variables

### Database Strategy
- **Development**: SQLite for simplicity and portability
- **Production**: PostgreSQL with environment-based configuration
- **Migration**: Seamless transition via Django ORM abstraction

### Static Files Strategy
- **Development**: Django's built-in static file serving
- **Production**: WhiteNoise for efficient static file serving
- **Compression**: Manifest static files storage for cache busting

### Security Implementation
- **Secret Key**: Environment variable with fallback for development
- **Debug Mode**: Controlled via environment, never True in production
- **HTTPS**: Ready-to-enable settings for SSL deployment
- **Headers**: Security headers configured for production

## Prompts for Copilot

### Phase 1: Settings Architecture
"Create Django split settings architecture with base, development, and production configurations. Base settings should include all common Django configuration including installed apps (django apps, crispy_forms, crispy_bootstrap5, donations, accounts, monitoring), middleware with MetricsMiddleware, and basic database/static file configuration. Development should use SQLite and console email. Production should use PostgreSQL, Redis cache, and SMTP email with environment variables."

### Phase 2: Environment Management  
"Update manage.py to use environment-based settings loading. Create settings/__init__.py that detects DJANGO_ENVIRONMENT variable and imports appropriate settings. Default to development if not specified. Ensure proper error handling for missing environment variables in production."

### Phase 3: Security Configuration
"Configure production security settings including DEBUG=False, secure cookies, HTTPS headers, CSRF protection, and XSS filtering. Add WhiteNoise for static file serving. Create environment variable configuration for SECRET_KEY, ALLOWED_HOSTS, and database credentials."

### Phase 4: Deployment Support
"Create deployment artifacts including .env.example template, deploy.sh script for production setup, and Procfile for platform deployment. Include comprehensive environment variable documentation and platform-specific deployment notes."

### Phase 5: Integration Testing
"Test settings loading in both development and production modes. Verify environment variable handling, static file collection, and database configuration. Ensure monitoring health checks work in both environments."

## Migration Strategy

### From Current Single Settings
1. **Backup**: Current settings.py → settings/base.py foundation
2. **Split**: Extract environment-specific configurations
3. **Test**: Verify development environment works unchanged
4. **Document**: Environment variable requirements
5. **Validate**: Production settings without deployment

### Database Transition
- **Development**: Continue using existing SQLite database
- **Production**: Ready for PostgreSQL when deploying
- **No Data Loss**: Existing development data preserved

### Static Files Transition
- **Development**: No changes to static file workflow
- **Production**: WhiteNoise handles static file serving
- **Collectstatic**: Required for production deployment

## Testing Strategy

### Settings Testing
```python
# Test environment detection
DJANGO_ENVIRONMENT=development python manage.py check
DJANGO_ENVIRONMENT=production python manage.py check --deploy

# Test static file collection
python manage.py collectstatic --dry-run

# Test monitoring integration
python manage.py test monitoring
```

### Environment Variable Testing
```python
# Test missing production variables
unset SECRET_KEY && DJANGO_ENVIRONMENT=production python manage.py check

# Test development defaults
unset SECRET_KEY && python manage.py check
```

### Deployment Testing
```bash
# Test deployment script
chmod +x deploy.sh
./deploy.sh --dry-run

# Test platform configurations
# (Platform-specific validation)
```

## Acceptance Validation

### Development Environment
- [x] `python manage.py runserver` works without changes
- [x] SQLite database continues working
- [x] Static files serve correctly
- [x] Debug toolbar accessible (if installed)
- [x] Console email backend active

### Production Configuration
- [x] `python manage.py check --deploy` passes
- [x] Environment variables properly configured
- [x] Static file collection works
- [x] Database configuration validates
- [x] Security settings enabled

### Monitoring Integration
- [x] Health checks work in both environments
- [x] Metrics middleware integrated
- [x] Logging configuration proper
- [x] No monitoring functionality broken

### Documentation Quality
- [x] Environment variables documented
- [x] Deployment process explained
- [x] Platform-specific notes included
- [x] Security checklist provided

## Rollback Plan

### If Settings Split Fails
1. **Immediate**: Revert to single settings.py from git
2. **Restore**: Copy current settings to settings.py
3. **Test**: Verify development server starts
4. **Fix**: Address any broken imports or configurations

### If Environment Variables Break
1. **Fallback**: Use development defaults for all settings
2. **Debug**: Check environment variable loading
3. **Validate**: Test each setting individually
4. **Document**: Update .env.example with working values

## Security Considerations

### Secret Management
- **Never Commit**: Secrets, API keys, or passwords
- **Environment Only**: All sensitive configuration via env vars
- **Rotation Ready**: Easy to change secrets via environment
- **Documentation**: Clear requirements for each environment

### Production Security
- **HTTPS Ready**: SSL settings prepared for deployment
- **Headers**: Security headers properly configured
- **CSRF**: Protection enabled and tested
- **XSS**: Filtering active in production

This brief provides comprehensive guidance for implementing the deployment and environment strategy defined in ADR-006, ensuring secure and maintainable deployment capability for the CFMP platform.