# Generated by Django 5.2.3 on 2025-06-13 06:26

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodgram', '0002_load_initial_data'),
    ]

    operations = [
        migrations.AddField(
            model_name='recipe',
            name='date_posted',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
