# Generated by Django 4.1.5 on 2023-03-20 01:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fleets', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='evefitting',
            name='latest_version',
            field=models.CharField(default='', max_length=255),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='evedoctrine',
            name='fittings',
            field=models.ManyToManyField(blank=True, to='fleets.evefitting'),
        ),
        migrations.AlterField(
            model_name='evefitting',
            name='latest_price',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=36),
        ),
    ]
