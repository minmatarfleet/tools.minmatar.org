# Generated by Django 4.1.5 on 2023-09-11 21:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fleets', '0028_merge_20230713_1321'),
    ]

    operations = [
        migrations.AddField(
            model_name='evefleet',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
    ]
