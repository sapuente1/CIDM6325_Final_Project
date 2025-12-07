# Community Food Management Platform (CFMP)

**CIDM 6325 - Fall 2025 Final Project**

A Django-based platform connecting food donors with community pantries to reduce food waste and address food insecurity.

## Project Overview

The Community Food Management Platform enables:
- **Food Donors** (restaurants, grocery stores, individuals) to post available food donations
- **Community Pantries** to browse, claim, and collect food donations
- **Real-time tracking** of donation status and logistics
- **Administrative oversight** through Django's admin interface

## Technical Implementation

### Django Framework Components (Matt Layman's "Understand Django")

This project demonstrates comprehensive Django knowledge across all 20 chapters:

- ✅ **Complete BASELINE**: All 20 required components implemented
- ✅ **GOOD Features**: 8 components (exceeds requirement of 4)  
- ✅ **BETTER Features**: 3 components (exceeds requirement of 2)
- ✅ **BEST Features**: 1 component (meets requirement of 1)

### Key Features

#### Authentication & Authorization
- Role-based registration (Donor vs Pantry)
- Custom permission mixins for view-level access control
- Secure login/logout with role-based redirects

#### Data Management
- Complex donation lifecycle (available → claimed → fulfilled)
- Location-based filtering and search
- Expiry date tracking and validation
- Business metrics and analytics

#### Professional UI/UX
- Bootstrap 5.3 with responsive design
- Professional navbar and form styling
- Mobile-optimized interface
- Business-template inspired design

#### Production Features
- Health monitoring endpoints
- Comprehensive logging with JSON formatting
- Environment-based configuration
- Admin interface with bulk actions and CSV export

## Project Structure

```
CFMP Django Project/        # Root directory
├── cfmp/                  # Project settings and configuration
├── donations/             # Core donations app
├── authentication/       # User authentication app
├── monitoring/           # Health checks and metrics
├── pantries/            # Pantry management app
├── templates/           # HTML templates
├── static/              # CSS, JS, images
├── media/               # User uploads
├── docs/                # Project documentation and ADRs
├── manage.py            # Django management script
├── Procfile             # Railway deployment configuration
├── railway.toml         # Railway build configuration
└── requirements.txt     # Python dependencies
```

## Quick Start

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Setup Database**
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```

3. **Run Development Server**
   ```bash
   python manage.py runserver
   ```

4. **Access Application**
   - Main site: http://127.0.0.1:8000/
   - Admin: http://127.0.0.1:8000/admin/
   - Health check: http://127.0.0.1:8000/monitoring/health/

## Documentation

- **[Implementation Analysis](RUBRIC_IMPLEMENTATION_ANALYSIS.md)** - Detailed component breakdown
- **[Completion Checklist](CHECKLIST_COMPLETION.md)** - Progress tracking
- **[Final Project Rubric](FinalProjectRubric.MD)** - Assignment requirements
- **[Railway Deployment Guide](RAILWAY_DEPLOYMENT_GUIDE.md)** - Deployment instructions

## Technology Stack

- **Backend**: Django 5.2, Python 3.12
- **Database**: SQLite (development), PostgreSQL ready
- **Frontend**: Bootstrap 5.3, Custom CSS
- **Development**: VS Code, Ruff formatting, Pyright type checking

## Course Integration

This project fulfills the requirements for CIDM 6325 by implementing all concepts from Matt Layman's "Understand Django" framework:

- **Chapter 1-20**: Complete coverage of Django fundamentals through advanced topics
- **Professional Development**: Code quality, testing, documentation standards
- **Real-world Application**: Addresses genuine community need (food waste/security)

## About the Developer

**Steven Puente** - CIDM 6325 Fall 2025  
West Texas A&M University

---

*This project demonstrates comprehensive Django web development skills and serves as a portfolio piece showcasing full-stack development capabilities.*