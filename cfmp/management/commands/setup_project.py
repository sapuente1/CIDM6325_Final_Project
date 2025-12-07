"""
Django management command for automated project setup.
"""

from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command
from django.contrib.auth import get_user_model
from django.db import transaction
import os


class Command(BaseCommand):
    help = 'Setup CFMP project for development'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--with-data',
            action='store_true',
            help='Load sample data for development',
        )
        parser.add_argument(
            '--superuser-username',
            default='admin',
            help='Username for superuser account (default: admin)',
        )
        parser.add_argument(
            '--superuser-email',
            default='admin@example.com',
            help='Email for superuser account (default: admin@example.com)',
        )
        parser.add_argument(
            '--skip-migrations',
            action='store_true',
            help='Skip running database migrations',
        )
        parser.add_argument(
            '--skip-static',
            action='store_true',
            help='Skip collecting static files',
        )
    
    def handle(self, *args, **options):
        """Main command handler."""
        self.stdout.write(
            self.style.SUCCESS('🚀 Setting up CFMP project...')
        )
        
        try:
            # Create logs directory if it doesn't exist
            self._create_logs_directory()
            
            # Run migrations
            if not options['skip_migrations']:
                self._run_migrations()
            
            # Collect static files
            if not options['skip_static']:
                self._collect_static_files()
            
            # Create superuser
            self._create_superuser(
                options['superuser_username'],
                options['superuser_email']
            )
            
            # Load sample data if requested
            if options['with_data']:
                self._load_sample_data()
            
            # Run system checks
            self._run_system_checks()
            
            self.stdout.write(
                self.style.SUCCESS('✅ Project setup completed successfully!')
            )
            self.stdout.write('🌟 Start the development server with: python manage.py runserver')
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Setup failed: {str(e)}')
            )
            raise CommandError(f'Project setup failed: {str(e)}')
    
    def _create_logs_directory(self):
        """Create logs directory if it doesn't exist."""
        from django.conf import settings
        logs_dir = os.path.join(settings.BASE_DIR, 'logs')
        
        if not os.path.exists(logs_dir):
            os.makedirs(logs_dir)
            self.stdout.write('📁 Created logs directory')
        else:
            self.stdout.write('📁 Logs directory already exists')
    
    def _run_migrations(self):
        """Run database migrations."""
        self.stdout.write('🗄️  Running database migrations...')
        try:
            call_command('makemigrations', verbosity=0, interactive=False)
            call_command('migrate', verbosity=0, interactive=False)
            self.stdout.write('✅ Database migrations completed')
        except Exception as e:
            raise CommandError(f'Migration failed: {str(e)}')
    
    def _collect_static_files(self):
        """Collect static files."""
        self.stdout.write('📦 Collecting static files...')
        try:
            call_command('collectstatic', verbosity=0, interactive=False)
            self.stdout.write('✅ Static files collected')
        except Exception as e:
            self.stdout.write(
                self.style.WARNING(f'⚠️  Static files collection failed: {str(e)}')
            )
    
    def _create_superuser(self, username: str, email: str):
        """Create superuser account if it doesn't exist."""
        User = get_user_model()
        
        try:
            with transaction.atomic():
                if User.objects.filter(username=username).exists():
                    self.stdout.write(f'👤 Superuser "{username}" already exists')
                    return
                
                # Try to create superuser with a default password
                user = User.objects.create_superuser(
                    username=username,
                    email=email,
                    password='admin123'  # Default development password
                )
                
                self.stdout.write(
                    self.style.SUCCESS(f'👤 Created superuser: {username}')
                )
                self.stdout.write(
                    self.style.WARNING('🔐 Default password: admin123 (change in production!)')
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.WARNING(f'⚠️  Superuser creation failed: {str(e)}')
            )
    
    def _load_sample_data(self):
        """Load sample data for development."""
        self.stdout.write('📊 Loading sample data...')
        
        try:
            # Import here to avoid circular imports
            from donations.models import Donation
            from pantries.models import Pantry
            from django.contrib.auth import get_user_model
            
            User = get_user_model()
            
            # Create sample users if they don't exist
            self._create_sample_users(User)
            
            # Create sample pantries
            self._create_sample_pantries()
            
            # Create sample donations
            self._create_sample_donations()
            
            self.stdout.write('✅ Sample data loaded')
            
        except Exception as e:
            self.stdout.write(
                self.style.WARNING(f'⚠️  Sample data loading failed: {str(e)}')
            )
    
    def _create_sample_users(self, User):
        """Create sample users for development."""
        sample_users = [
            {'username': 'donor1', 'email': 'donor1@example.com', 'first_name': 'John', 'last_name': 'Donor'},
            {'username': 'pantry1', 'email': 'pantry1@example.com', 'first_name': 'Jane', 'last_name': 'Manager'},
        ]
        
        for user_data in sample_users:
            if not User.objects.filter(username=user_data['username']).exists():
                User.objects.create_user(
                    password='testpass123',
                    **user_data
                )
                self.stdout.write(f'👤 Created sample user: {user_data["username"]}')
    
    def _create_sample_pantries(self):
        """Create sample pantries for development."""
        from pantries.models import Pantry
        
        sample_pantries = [
            {
                'name': 'Downtown Food Bank',
                'address': '123 Main St, Anytown, ST 12345',
                'contact_email': 'info@downtownfoodbank.org',
                'phone_number': '(555) 123-4567',
                'description': 'Serving the downtown community since 1985.'
            },
            {
                'name': 'Community Kitchen',
                'address': '456 Oak Ave, Anytown, ST 12345',
                'contact_email': 'help@communitykitchen.org', 
                'phone_number': '(555) 987-6543',
                'description': 'Hot meals and food assistance for families in need.'
            }
        ]
        
        for pantry_data in sample_pantries:
            pantry, created = Pantry.objects.get_or_create(
                name=pantry_data['name'],
                defaults=pantry_data
            )
            if created:
                self.stdout.write(f'🏪 Created sample pantry: {pantry.name}')
    
    def _create_sample_donations(self):
        """Create sample donations for development."""
        from donations.models import Donation
        from pantries.models import Pantry
        from django.contrib.auth import get_user_model
        
        User = get_user_model()
        
        # Get sample data
        pantry = Pantry.objects.first()
        donor = User.objects.filter(username='donor1').first()
        
        if pantry and donor:
            sample_donations = [
                {
                    'donor': donor,
                    'pantry': pantry,
                    'food_type': 'Canned Goods',
                    'quantity': 50,
                    'unit': 'cans',
                    'description': 'Mixed canned vegetables and fruits',
                    'pickup_date': '2024-12-15',
                    'status': 'confirmed'
                },
                {
                    'donor': donor,
                    'pantry': pantry,
                    'food_type': 'Dairy',
                    'quantity': 20,
                    'unit': 'gallons',
                    'description': 'Fresh milk from local dairy',
                    'pickup_date': '2024-12-16',
                    'status': 'pending'
                }
            ]
            
            for donation_data in sample_donations:
                donation, created = Donation.objects.get_or_create(
                    donor=donation_data['donor'],
                    pantry=donation_data['pantry'],
                    food_type=donation_data['food_type'],
                    defaults=donation_data
                )
                if created:
                    self.stdout.write(f'🍎 Created sample donation: {donation.food_type}')
    
    def _run_system_checks(self):
        """Run Django system checks to verify setup."""
        self.stdout.write('🔍 Running system checks...')
        try:
            call_command('check', verbosity=0)
            self.stdout.write('✅ System checks passed')
        except Exception as e:
            self.stdout.write(
                self.style.WARNING(f'⚠️  System checks failed: {str(e)}')
            )