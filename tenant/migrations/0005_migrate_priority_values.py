# Migration to update priority values from old format to P1-P4
from django.db import migrations


def update_priority_values(apps, schema_editor):
    """Update existing priority values to P1-P4 format"""
    SLATarget = apps.get_model('tenant', 'SLATarget')
    
    # Mapping of old priority values to new P1-P4 format
    priority_mapping = {
        'urgent': 'P1',
        'critical': 'P1',
        'high': 'P2',
        'medium': 'P3',
        'normal': 'P3',
        'low': 'P4',
    }
    
    for target in SLATarget.objects.all():
        old_priority = target.priority.lower()
        if old_priority in priority_mapping:
            target.priority = priority_mapping[old_priority]
            target.save()


def reverse_priority_values(apps, schema_editor):
    """Reverse migration - convert P1-P4 back to old format"""
    SLATarget = apps.get_model('tenant', 'SLATarget')
    
    # Reverse mapping
    reverse_mapping = {
        'P1': 'urgent',
        'P2': 'high',
        'P3': 'medium',
        'P4': 'low',
    }
    
    for target in SLATarget.objects.all():
        if target.priority in reverse_mapping:
            target.priority = reverse_mapping[target.priority]
            target.save()


class Migration(migrations.Migration):

    dependencies = [
        ('tenant', '0004_businesshoursx_include_weekends_and_more'),
    ]

    operations = [
        migrations.RunPython(update_priority_values, reverse_priority_values),
    ]
