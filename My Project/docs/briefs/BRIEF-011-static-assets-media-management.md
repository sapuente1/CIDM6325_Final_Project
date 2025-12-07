# BRIEF-011: Static Assets and Media Management Implementation

**Date**: 2025-12-07  
**ADR Reference**: ADR-011-static-assets-media-management  
**Sprint**: Frontend Enhancement  
**Priority**: High  

## Goal

Implement comprehensive static asset management and media file handling for CFMP, including custom CSS styling, JavaScript functionality, image assets, and production-ready file serving capabilities.

## Scope (Single Implementation)

### Files to Create/Modify:
- `static/css/cfmp.css` - Main application stylesheet
- `static/css/components/` - Component-specific styles  
- `static/js/cfmp.js` - Main application JavaScript
- `static/js/components/` - Feature-specific JavaScript modules
- `static/img/` - Image assets and placeholders
- `cfmp/settings/base.py` - Static/media configuration
- `cfmp/urls.py` - Media URL serving in development
- Template files - Asset loading integration

### Non-Goals:
- Cloud storage integration (future enhancement)
- Advanced image optimization tools
- Complex build pipeline (keeping it Django-native)

## Standards

### Code Quality:
- Follow Django static files best practices
- Use CSS custom properties (CSS variables) for theming
- Modern JavaScript (ES6+) with proper error handling
- Responsive design with mobile-first approach
- Accessibility compliance (WCAG 2.1 AA)

### File Organization:
- Logical directory structure by asset type
- Component-based CSS architecture
- Modular JavaScript with clear separation of concerns
- Optimized image formats and sizes

### Security:
- File upload validation and restrictions
- CSRF protection for AJAX requests
- Content Security Policy considerations
- Safe file permissions

## Implementation Tasks

### Phase 1: Static File Infrastructure
1. **Create directory structure** under `static/`:
   - `css/` (main styles + components)
   - `js/` (main scripts + components) 
   - `img/` (logos, icons, placeholders)
   - `fonts/` (custom typography if needed)

2. **Configure Django settings** in `cfmp/settings/base.py`:
   - `STATIC_URL`, `STATIC_ROOT`, `STATICFILES_DIRS`
   - `MEDIA_URL`, `MEDIA_ROOT` 
   - File upload limits and permissions
   - WhiteNoise configuration for production

3. **Add media URL serving** in `cfmp/urls.py` for development

### Phase 2: CSS Implementation
1. **Create main stylesheet** (`static/css/cfmp.css`):
   - CSS custom properties for CFMP color palette
   - Typography and spacing variables
   - Global styles and utilities
   - Bootstrap customizations and overrides

2. **Build component stylesheets**:
   - `components/navbar.css` - Navigation styling
   - `components/cards.css` - Donation card enhancements
   - `components/forms.css` - Form styling improvements
   - `components/alerts.css` - Message and notification styles

3. **Responsive design patterns**:
   - Mobile-first media queries
   - Flexible grid layouts
   - Touch-friendly interfaces

### Phase 3: JavaScript Implementation
1. **Create main application script** (`static/js/cfmp.js`):
   - CFMP class with initialization
   - CSRF token setup for AJAX
   - Form validation enhancements
   - Search functionality
   - Modal handling
   - Time ago utilities

2. **Build feature modules**:
   - `components/donation-search.js` - Real-time search
   - `components/claim-modal.js` - Donation claiming workflow
   - `components/form-validation.js` - Client-side validation
   - `components/image-upload.js` - File upload enhancements

### Phase 4: Image and Media Assets
1. **Create image assets**:
   - CFMP logo (PNG and SVG formats)
   - Favicon and app icons
   - Placeholder images for donations
   - Food category icons
   - UI enhancement graphics

2. **Media file handling**:
   - Update donation model with photo field
   - File upload validation
   - Image processing and optimization
   - Placeholder fallbacks

### Phase 5: Template Integration
1. **Update base template**:
   - Static asset loading with `{% load static %}`
   - Preload critical CSS/JS
   - Favicon and meta tags
   - Proper asset organization

2. **Component templates**:
   - Update navigation with logo
   - Enhance cards with styling hooks
   - Form improvements with validation
   - Image display components

3. **Performance optimizations**:
   - Critical CSS inlining
   - Async JavaScript loading
   - Image lazy loading

## Acceptance Criteria

### CSS/Styling:
- [ ] CFMP brand colors and typography implemented
- [ ] Responsive design works on mobile/tablet/desktop
- [ ] Component styles enhance readability and UX
- [ ] Bootstrap customizations maintain consistency
- [ ] Loading states and animations provide feedback

### JavaScript:
- [ ] Real-time search without page refresh
- [ ] Form validation with immediate feedback
- [ ] AJAX interactions with proper CSRF handling
- [ ] Modal workflows for donation claiming
- [ ] Progressive enhancement (works without JS)

### Media Handling:
- [ ] Image upload with drag-and-drop
- [ ] File type and size validation
- [ ] Automatic image resizing/optimization
- [ ] Placeholder images for missing content
- [ ] Secure file permissions and storage

### Performance:
- [ ] Static files compress and cache properly
- [ ] Images optimized for web delivery
- [ ] JavaScript loads without blocking rendering
- [ ] CSS critical path optimized
- [ ] Development vs production asset handling

### Accessibility:
- [ ] Proper ARIA labels and roles
- [ ] Keyboard navigation support
- [ ] Screen reader compatibility
- [ ] Color contrast meets WCAG standards
- [ ] Focus management in dynamic content

## Prompts for AI Implementation

### Initial Setup:
"Create the complete static asset directory structure with main CSS and JavaScript files following the CFMP design system. Include Django settings configuration for static and media files with WhiteNoise support."

### CSS Development:
"Implement the CFMP design system with CSS custom properties, component-based architecture, and Bootstrap customizations. Focus on professional branding, responsive layouts, and accessibility compliance."

### JavaScript Enhancement:
"Build the main CFMP JavaScript application class with modules for search, form validation, modal handling, and AJAX interactions. Ensure progressive enhancement and proper error handling."

### Media Integration:
"Add comprehensive media file handling including image upload, validation, processing, and secure storage. Create placeholder assets and optimize for web delivery."

### Template Integration:
"Update all Django templates to properly load static assets, implement the design system, and provide optimal performance with preloading and async loading strategies."

## Dependencies

### Python Packages:
- `whitenoise` - Static file serving
- `pillow` - Image processing
- `django-cleanup` - Orphaned file cleanup

### External Assets:
- Bootstrap 5.3.0 (CDN)
- Bootstrap Icons (CDN)
- HTMX for dynamic interactions

### Development Tools:
- Django `collectstatic` command
- Browser developer tools for testing
- Image optimization tools

## Rollback Plan

If implementation issues occur:
1. **CSS Problems**: Comment out custom styles, fall back to Bootstrap defaults
2. **JavaScript Errors**: Disable custom JS, maintain basic functionality
3. **Media Issues**: Remove file upload fields, use text-only donations
4. **Performance Issues**: Disable compression, use simple static file serving

## Testing Strategy

### Manual Testing:
- Cross-browser compatibility (Chrome, Firefox, Safari, Edge)
- Mobile responsiveness on actual devices
- File upload workflows with various formats
- Network throttling for performance testing

### Automated Testing:
- Django template tests for asset loading
- JavaScript unit tests for utility functions
- Integration tests for AJAX workflows
- Performance benchmarking with Django Debug Toolbar

## Success Metrics

- **Visual Polish**: Professional appearance with consistent branding
- **Performance**: < 2s page load times on 3G networks
- **Accessibility**: WCAG 2.1 AA compliance score > 95%
- **User Experience**: Smooth interactions without jarring transitions
- **Maintainability**: Clear code organization and documentation

This implementation will transform CFMP from a functional prototype into a polished, production-ready application with professional styling, enhanced interactivity, and comprehensive media handling capabilities.