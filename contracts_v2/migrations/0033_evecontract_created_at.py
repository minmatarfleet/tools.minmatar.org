# Generated by Django 4.0.10 on 2023-09-11 20:56

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('contracts_v2', '0032_remove_evecontractentity_active'),
    ]

    operations = [
        migrations.AddField(
            model_name='evecontract',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
