# Generated by Django 4.1.5 on 2023-03-08 20:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contracts_v2', '0003_rename_character_id_evecontractentitycodechallenge_entity_id_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='evecontractentityreponsibility',
            name='title',
            field=models.CharField(max_length=255, unique=True),
        ),
    ]
