from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.db import connection
from django.core.cache import cache

class Command(BaseCommand):
    help = 'Deploy application with safe migrations and health checks'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--skip-migrate',
            action='store_true',
            help='Skip database migrations',
        )
        parser.add_argument(
            '--skip-static',
            action='store_true',
            help='Skip static file collection',
        )
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting CFMP deployment...'))
        
        # Check database connectivity
        self.stdout.write('Checking database connectivity...')
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            self.stdout.write(self.style.SUCCESS('✓ Database connection successful'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ Database connection failed: {e}'))
            return
        
        # Run migrations unless skipped
        if not options['skip_migrate']:
            self.stdout.write('Running database migrations...')
            try:
                call_command('migrate', '--no-input')
                self.stdout.write(self.style.SUCCESS('✓ Migrations completed'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'✗ Migration failed: {e}'))
                return
        
        # Collect static files unless skipped
        if not options['skip_static']:
            self.stdout.write('Collecting static files...')
            try:
                call_command('collectstatic', '--no-input', '--clear')
                self.stdout.write(self.style.SUCCESS('✓ Static files collected'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'✗ Static file collection failed: {e}'))
                return
        
        # Test cache connectivity
        self.stdout.write('Testing cache connectivity...')
        try:
            cache.set('deploy_test', 'ok', 10)
            if cache.get('deploy_test') == 'ok':
                self.stdout.write(self.style.SUCCESS('✓ Cache connection successful'))
            else:
                self.stdout.write(self.style.WARNING('⚠ Cache test failed'))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'⚠ Cache connection failed: {e}'))
        
        # Run deployment checks
        self.stdout.write('Running deployment checks...')
        try:
            call_command('check', '--deploy')
            self.stdout.write(self.style.SUCCESS('✓ Deployment checks passed'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ Deployment checks failed: {e}'))
            return
        
        self.stdout.write(self.style.SUCCESS('🎉 Deployment completed successfully!'))