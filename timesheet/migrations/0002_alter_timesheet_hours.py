# Generated by Django 5.0.4 on 2024-05-15 11:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('timesheet', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='timesheet',
            name='hours',
            field=models.FloatField(blank=True, null=True),
        ),
    ]
