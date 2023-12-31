# Generated by Django 4.1.5 on 2023-03-12 00:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contracts_v2', '0007_evecontractexpectation'),
    ]

    operations = [
        migrations.AddField(
            model_name='evecontractexpectation',
            name='entities',
            field=models.ManyToManyField(blank=True, related_name='expectations', to='contracts_v2.evecontractentity'),
        ),
        migrations.AlterUniqueTogether(
            name='evecontractexpectation',
            unique_together={('ship_name', 'type')},
        ),
    ]
