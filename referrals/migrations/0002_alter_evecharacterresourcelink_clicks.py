# Generated by Django 4.1.5 on 2023-02-02 16:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('referrals', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='evecharacterresourcelink',
            name='clicks',
            field=models.IntegerField(default=0),
        ),
    ]
