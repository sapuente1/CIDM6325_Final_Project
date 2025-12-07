"""
Management command to analyze donation metrics and generate reports
"""
import json
from datetime import timedelta
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from django.db.models import Count, Q
from donations.models import Donation


class Command(BaseCommand):
    help = 'Analyze donation metrics and generate report'
    
    def add_arguments(self, parser):
        parser.add_argument('--days', type=int, default=7, help='Number of days to analyze')
        parser.add_argument(
            '--format', 
            choices=['text', 'json'], 
            default='text', 
            help='Output format'
        )
        parser.add_argument(
            '--output', 
            type=str, 
            help='Output file path (optional)'
        )
    
    def handle(self, *args, **options):
        days = options['days']
        output_format = options['format']
        output_file = options.get('output')
        
        if days <= 0:
            raise CommandError('Days must be a positive integer')
        
        start_date = timezone.now() - timedelta(days=days)
        
        # Calculate metrics
        metrics_data = self._calculate_metrics(start_date, days)
        
        # Generate report
        if output_format == 'json':
            report = self._generate_json_report(metrics_data)
        else:
            report = self._generate_text_report(metrics_data)
        
        # Output report
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(report)
            self.stdout.write(f"Report saved to: {output_file}")
        else:
            self.stdout.write(report)
    
    def _calculate_metrics(self, start_date, days):
        """Calculate donation metrics for the specified period"""
        donations = Donation.objects.filter(created_at__gte=start_date)
        
        total_donations = donations.count()
        claimed_donations = donations.filter(status='claimed').count()
        expired_donations = donations.filter(status='expired').count()
        available_donations = donations.filter(status='available').count()
        fulfilled_donations = donations.filter(status='fulfilled').count()
        
        claim_rate = (claimed_donations / total_donations * 100) if total_donations > 0 else 0
        fulfillment_rate = (fulfilled_donations / total_donations * 100) if total_donations > 0 else 0
        
        # Food type breakdown
        food_type_stats = donations.values('food_type').annotate(
            count=Count('id'),
            claimed_count=Count('id', filter=Q(status='claimed')),
            expired_count=Count('id', filter=Q(status='expired'))
        ).order_by('-count')
        
        # Location stats
        location_stats = donations.values('location').annotate(
            count=Count('id')
        ).order_by('-count')[:10]  # Top 10 locations
        
        # Time to claim analysis (for claimed donations)
        claimed_donations_qs = donations.filter(status='claimed', claimed_at__isnull=False)
        avg_time_to_claim = None
        if claimed_donations_qs.exists():
            time_deltas = [
                (d.claimed_at - d.created_at).total_seconds() / 3600  # Convert to hours
                for d in claimed_donations_qs.select_related()
                if d.claimed_at and d.created_at
            ]
            if time_deltas:
                avg_time_to_claim = sum(time_deltas) / len(time_deltas)
        
        return {
            'period_days': days,
            'start_date': start_date.date().isoformat(),
            'end_date': timezone.now().date().isoformat(),
            'total_donations': total_donations,
            'available_donations': available_donations,
            'claimed_donations': claimed_donations,
            'expired_donations': expired_donations,
            'fulfilled_donations': fulfilled_donations,
            'claim_rate': round(claim_rate, 1),
            'fulfillment_rate': round(fulfillment_rate, 1),
            'avg_time_to_claim_hours': round(avg_time_to_claim, 1) if avg_time_to_claim else None,
            'food_type_stats': list(food_type_stats),
            'location_stats': list(location_stats),
            'target_claim_rate': 80.0,
            'meets_target': claim_rate >= 80.0
        }
    
    def _generate_text_report(self, data):
        """Generate human-readable text report"""
        report = []
        report.append(f"\n{'='*60}")
        report.append(f" CFMP Metrics Report (Last {data['period_days']} days)")
        report.append(f"{'='*60}")
        report.append(f"Period: {data['start_date']} to {data['end_date']}")
        report.append("")
        
        # Overall Statistics
        report.append("📊 OVERALL STATISTICS")
        report.append("-" * 30)
        report.append(f"Total Donations: {data['total_donations']}")
        report.append(f"Available Donations: {data['available_donations']}")
        report.append(f"Claimed Donations: {data['claimed_donations']}")
        report.append(f"Fulfilled Donations: {data['fulfilled_donations']}")
        report.append(f"Expired Donations: {data['expired_donations']}")
        report.append("")
        
        # Key Metrics
        report.append("🎯 KEY METRICS")
        report.append("-" * 30)
        report.append(f"Claim Rate: {data['claim_rate']}%")
        report.append(f"Fulfillment Rate: {data['fulfillment_rate']}%")
        report.append(f"Target Claim Rate: {data['target_claim_rate']}%")
        
        if data['avg_time_to_claim_hours']:
            report.append(f"Average Time to Claim: {data['avg_time_to_claim_hours']} hours")
        
        # Target Assessment
        if data['meets_target']:
            report.append("✅ MEETING CLAIM RATE TARGET")
        else:
            report.append("⚠️  BELOW CLAIM RATE TARGET")
            deficit = data['target_claim_rate'] - data['claim_rate']
            report.append(f"   Need to improve by {deficit:.1f} percentage points")
        
        report.append("")
        
        # Food Type Breakdown
        if data['food_type_stats']:
            report.append("🍎 FOOD TYPE BREAKDOWN")
            report.append("-" * 30)
            for stat in data['food_type_stats'][:5]:  # Top 5
                food_type = stat['food_type']
                total = stat['count']
                claimed = stat['claimed_count']
                claim_rate = (claimed / total * 100) if total > 0 else 0
                report.append(f"{food_type}: {total} donations ({claim_rate:.1f}% claimed)")
            report.append("")
        
        # Location Analysis
        if data['location_stats']:
            report.append("📍 TOP LOCATIONS")
            report.append("-" * 30)
            for stat in data['location_stats'][:5]:  # Top 5
                location = stat['location']
                count = stat['count']
                report.append(f"{location}: {count} donations")
        
        report.append("\n" + "="*60)
        
        return "\n".join(report)
    
    def _generate_json_report(self, data):
        """Generate JSON format report"""
        return json.dumps(data, indent=2, ensure_ascii=False)