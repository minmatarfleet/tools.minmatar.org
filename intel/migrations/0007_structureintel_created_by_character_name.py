# Generated by Django 4.1.5 on 2023-10-13 10:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('intel', '0006_structureintelcampaign_corporation_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='structureintel',
            name='created_by_character_name',
            field=models.CharField(default='BearThatCares', max_length=255),
            preserve_default=False,
        ),
    ]
