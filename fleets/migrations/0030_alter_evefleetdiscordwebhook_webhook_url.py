# Generated by Django 4.1.5 on 2023-10-09 18:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fleets', '0029_evefleet_description'),
    ]

    operations = [
        migrations.AlterField(
            model_name='evefleetdiscordwebhook',
            name='webhook_url',
            field=models.CharField(blank=True, max_length=255, unique=True),
        ),
    ]
