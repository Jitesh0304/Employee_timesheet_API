# Generated by Django 4.1.11 on 2024-02-29 19:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('timesheet', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='weeklyreport',
            name='submit_timesheet',
            field=models.ManyToManyField(blank=True, related_name='week_submited_timesheet', to='timesheet.timesheet'),
        ),
    ]
