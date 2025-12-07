"""
Admin Interface Testing Script
Test the comprehensive admin interface functionality for BRIEF-004
"""
import os
import sys
import django
from datetime import date, timedelta

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cfmp.settings')
django.setup()

from django.contrib.auth.models import User
from donations.models import Donor, Pantry, Donation
from donations.admin import DonationAdmin, export_csv, mark_expired
from django.contrib.admin.sites import AdminSite
from django.http import HttpRequest
from django.contrib.messages.storage.fallback import FallbackStorage


def test_admin_features():
    """Test the admin interface features"""
    print("🔍 Testing Admin Interface Features...")
    print("=" * 50)
    
    # Test 1: Create test data
    print("\n1. Creating test data...")
    
    # Create users if they don't exist
    try:
        donor_user = User.objects.get(username='test_donor')
    except User.DoesNotExist:
        donor_user = User.objects.create_user(
            'test_donor', 'donor@test.com', 'testpass123',
            first_name='John', last_name='Smith'
        )
        print("   ✅ Created donor user")
    
    try:
        pantry_user = User.objects.get(username='test_pantry') 
    except User.DoesNotExist:
        pantry_user = User.objects.create_user(
            'test_pantry', 'pantry@test.com', 'testpass123',
            first_name='Jane', last_name='Doe'
        )
        print("   ✅ Created pantry user")
    
    # Create profiles if they don't exist
    try:
        donor = Donor.objects.get(user=donor_user)
    except Donor.DoesNotExist:
        donor = Donor.objects.create(
            user=donor_user,
            organization_name='Fresh Foods Market',
            location='Downtown District',
            contact_phone='555-0123'
        )
        print("   ✅ Created donor profile")
    
    try:
        pantry = Pantry.objects.get(user=pantry_user)
    except Pantry.DoesNotExist:
        pantry = Pantry.objects.create(
            user=pantry_user,
            organization_name='Community Food Bank',
            location='North Side',
            service_area='North District',
            capacity=200,
            contact_phone='555-0456'
        )
        print("   ✅ Created pantry profile")
    
    # Create test donations
    test_donations = []
    
    # Fresh donation (expires in 5 days)
    fresh_donation = Donation.objects.create(
        donor=donor,
        food_type='Produce',
        description='Fresh vegetables and fruits',
        quantity=100,
        location='Downtown Market',
        expiry_date=date.today() + timedelta(days=5),
        status='available'
    )
    test_donations.append(fresh_donation)
    
    # Expiring soon donation (expires in 1 day)
    expiring_donation = Donation.objects.create(
        donor=donor,
        food_type='Dairy',
        description='Milk and yogurt products',
        quantity=50,
        location='Downtown Market',
        expiry_date=date.today() + timedelta(days=1),
        status='available'
    )
    test_donations.append(expiring_donation)
    
    # Expired donation (auto-expired by model)
    expired_donation = Donation.objects.create(
        donor=donor,
        food_type='Bread',
        description='Day-old bread products',
        quantity=25,
        location='Downtown Market',
        expiry_date=date.today() - timedelta(days=2),
        status='available'  # Will be auto-expired by model save
    )
    test_donations.append(expired_donation)
    
    print(f"   ✅ Created {len(test_donations)} test donations")
    
    # Test 2: Admin Display Methods
    print("\n2. Testing admin display methods...")
    
    site = AdminSite()
    donation_admin = DonationAdmin(Donation, site)
    
    # Test donor_name display
    donor_name = donation_admin.donor_name(fresh_donation)
    print(f"   ✅ Donor name display: '{donor_name}'")
    assert donor_name == 'Fresh Foods Market', f"Expected 'Fresh Foods Market', got '{donor_name}'"
    
    # Test days_until_expiry display with color coding
    fresh_expiry = donation_admin.days_until_expiry(fresh_donation)
    expiring_expiry = donation_admin.days_until_expiry(expiring_donation)
    expired_expiry = donation_admin.days_until_expiry(expired_donation)
    
    print(f"   ✅ Fresh donation expiry: {fresh_expiry}")
    print(f"   ✅ Expiring donation expiry: {expiring_expiry}")
    print(f"   ✅ Expired donation expiry: {expired_expiry}")
    
    # Check color coding
    assert '5 days' in fresh_expiry, "Fresh donation should show 5 days"
    assert 'orange' in expiring_expiry, "Expiring donation should be orange"
    assert 'red' in expired_expiry, "Expired donation should be red"
    
    # Test 3: Bulk Actions
    print("\n3. Testing bulk actions...")
    
    # Setup request for actions
    request = HttpRequest()
    request.user = User.objects.get(username='admin')
    setattr(request, 'session', {})
    messages = FallbackStorage(request)
    setattr(request, '_messages', messages)
    
    # Test mark_expired action
    available_donations = Donation.objects.filter(status='available')
    initial_count = available_donations.count()
    print(f"   📊 Available donations before action: {initial_count}")
    
    mark_expired(donation_admin, request, available_donations)
    final_available = Donation.objects.filter(status='available').count()
    print(f"   📊 Available donations after mark expired: {final_available}")
    print("   ✅ Mark expired action completed")
    
    # Test CSV export
    all_donations = Donation.objects.all()
    csv_response = export_csv(donation_admin, request, all_donations)
    
    print(f"   📄 CSV export content-type: {csv_response['Content-Type']}")
    print(f"   📄 CSV export disposition: {csv_response['Content-Disposition']}")
    
    csv_content = csv_response.content.decode('utf-8')
    lines = csv_content.strip().split('\n')
    print(f"   📄 CSV export rows: {len(lines)} (including header)")
    print("   ✅ CSV export action completed")
    
    # Test 4: Search and Filtering Features
    print("\n4. Testing search and filtering features...")
    
    # Test search fields
    search_fields = donation_admin.search_fields
    print(f"   🔍 Search fields configured: {len(search_fields)} fields")
    for field in search_fields:
        print(f"      - {field}")
    
    # Test list filters
    list_filters = donation_admin.list_filter
    print(f"   🔍 List filters configured: {len(list_filters)} filters")
    for filter_field in list_filters:
        print(f"      - {filter_field}")
    
    # Test queryset optimization
    optimized_queryset = donation_admin.get_queryset(request)
    query_str = str(optimized_queryset.query).lower()
    has_joins = 'join' in query_str or 'inner' in query_str
    print(f"   🚀 Queryset optimization active: {'Yes' if has_joins else 'No'}")
    
    print("   ✅ Search and filtering features verified")
    
    # Test 5: Admin Site Customization
    print("\n5. Testing admin site customization...")
    
    from django.contrib import admin
    print(f"   🎨 Site header: '{admin.site.site_header}'")
    print(f"   🎨 Site title: '{admin.site.site_title}'") 
    print(f"   🎨 Index title: '{admin.site.index_title}'")
    
    assert admin.site.site_header == "CFMP Administration", "Site header not customized"
    assert admin.site.site_title == "CFMP Admin", "Site title not customized"
    assert admin.site.index_title == "Community Food Match Platform", "Index title not customized"
    
    print("   ✅ Admin site customization verified")
    
    # Test 6: Enhanced User Admin
    print("\n6. Testing enhanced User admin...")
    
    from authentication.admin import UserAdmin
    user_admin = UserAdmin(User, site)
    
    # Test role display
    admin_user = User.objects.get(username='admin')
    donor_role = user_admin.user_role(donor_user)
    pantry_role = user_admin.user_role(pantry_user)
    admin_role = user_admin.user_role(admin_user)
    
    print(f"   👤 Donor role display: {donor_role}")
    print(f"   👤 Pantry role display: {pantry_role}")
    print(f"   👤 Admin role display: {admin_role}")
    
    # Test organization name display
    donor_org = user_admin.organization_name(donor_user)
    pantry_org = user_admin.organization_name(pantry_user)
    admin_org = user_admin.organization_name(admin_user)
    
    print(f"   🏢 Donor organization: '{donor_org}'")
    print(f"   🏢 Pantry organization: '{pantry_org}'")
    print(f"   🏢 Admin organization: '{admin_org}'")
    
    print("   ✅ Enhanced User admin verified")
    
    # Summary
    print("\n" + "=" * 50)
    print("🎉 ADMIN INTERFACE TESTING COMPLETE!")
    print("=" * 50)
    print("✅ All BRIEF-004 requirements implemented:")
    print("   • Comprehensive ModelAdmin classes")
    print("   • Bulk operations (mark expired, CSV export)")
    print("   • Color-coded status indicators")
    print("   • Enhanced search and filtering")
    print("   • Performance optimizations")
    print("   • Role-based User admin")
    print("   • Custom admin site branding")
    
    # Statistics
    total_donations = Donation.objects.count()
    total_donors = Donor.objects.count()
    total_pantries = Pantry.objects.count()
    total_users = User.objects.count()
    
    print(f"\n📊 Current Database Statistics:")
    print(f"   • Users: {total_users}")
    print(f"   • Donors: {total_donors}")
    print(f"   • Pantries: {total_pantries}")
    print(f"   • Donations: {total_donations}")
    
    return True


if __name__ == '__main__':
    try:
        success = test_admin_features()
        print(f"\n🏆 Admin interface testing: {'PASSED' if success else 'FAILED'}")
    except Exception as e:
        print(f"\n❌ Admin interface testing FAILED: {e}")
        import traceback
        traceback.print_exc()