# Generated by Django 4.1.5 on 2023-06-24 16:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fleets', '0011_evedoctrine_composition'),
    ]

    operations = [
        migrations.AddField(
            model_name='evedoctrine',
            name='primary',
            field=models.BooleanField(default=False),
        ),
    ]
