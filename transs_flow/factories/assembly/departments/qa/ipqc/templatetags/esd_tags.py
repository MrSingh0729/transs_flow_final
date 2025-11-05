from django import template
from django.utils import timezone
from datetime import timedelta
from ..models import ESDComplianceChecklist

register = template.Library()

@register.filter
def esd_compliance_status(record):
    """
    Calculate ESD compliance status based on audit fields
    Returns dict with pass_count, fail_count, na_count, and status
    """
    # List of all audit choice fields
    audit_fields = [
        'epa_clothes', 'forbid_wear_out', 'no_accessories', 'clothes_clean',
        'collar_cover', 'all_buttons_closed', 'clothes_length', 'watch_expose',
        'hair_cap', 'slipper_check', 'wristband_check', 'pre_line_check',
        'wrist_touch_skin', 'no_touch_pcba', 'alert_plug_out',
        'trolley_grounding', 'device_grounded', 'grounding_points_tight',
        'ion_fan_distance', 'ion_fan_direction', 'gloves_condition',
        'mat_grounded', 'audit_label_valid', 'esds_box', 'table_no_source',
        'tools_audit', 'temp_humidity', 'tray_voltage'
    ]
    
    pass_count = 0
    fail_count = 0
    na_count = 0
    
    for field_name in audit_fields:
        field_value = getattr(record, field_name, 'NA')
        if field_value == 'PASS':
            pass_count += 1
        elif field_value == 'FAIL':
            fail_count += 1
        elif field_value == 'NA':
            na_count += 1
    
    # Determine overall status
    if fail_count > 0:
        status = 'Non-Compliant'
        status_class = 'status-non-compliant'
        icon = 'fas fa-times-circle'
    elif na_count > pass_count:
        status = 'Partial'
        status_class = 'status-partial'
        icon = 'fas fa-exclamation-circle'
    else:
        status = 'Compliant'
        status_class = 'status-compliant'
        icon = 'fas fa-check-circle'
    
    return {
        'pass_count': pass_count,
        'fail_count': fail_count,
        'na_count': na_count,
        'status': status,
        'status_class': status_class,
        'icon': icon
    }

@register.simple_tag
def esd_stats_dashboard():
    """
    Get ESD stats for dashboard
    """
    today = timezone.now().date()
    week_start = today - timedelta(days=today.weekday())
    
    today_count = ESDComplianceChecklist.objects.filter(date=today).count()
    week_count = ESDComplianceChecklist.objects.filter(date__gte=week_start).count()
    total_count = ESDComplianceChecklist.objects.all().count()
    
    return {
        'today': today_count,
        'week': week_count,
        'total': total_count
    }