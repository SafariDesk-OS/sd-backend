# Generated migration for adding include_weekends field to SLAConfiguration

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tenant', '0003_alter_slatarget_first_response_time_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='slaconfiguration',
            name='include_weekends',
            field=models.BooleanField(default=False, help_text='Include weekends (Saturday & Sunday) in SLA time calculations. When disabled, weekends are automatically excluded regardless of individual day settings.'),
        ),
    ]
