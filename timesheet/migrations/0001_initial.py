# Generated by Django 5.0.1 on 2024-02-28 06:44

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('projectdata', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Timesheet',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('day', models.CharField(max_length=50)),
                ('date', models.DateField()),
                ('status', models.CharField(blank=True, choices=[('Submit', 'Submit'), ('NotSubmit', 'NotSubmit')], max_length=50, null=True)),
                ('hours', models.FloatField(blank=True, null=True)),
                ('organization', models.CharField(blank=True, max_length=100, null=True)),
                ('project_code', models.CharField(blank=True, max_length=100, null=True)),
                ('project_subcode', models.CharField(blank=True, max_length=100, null=True)),
                ('bill', models.CharField(blank=True, max_length=100, null=True)),
                ('location', models.CharField(choices=[('WFH', 'WFH'), ('OnSite', 'OnSite'), ('Office', 'Office')], max_length=100)),
                ('comment', models.CharField(blank=True, max_length=300, null=True)),
                ('submit', models.BooleanField(default=False)),
                ('approve', models.BooleanField(default=False)),
                ('employee', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='employee_related', to=settings.AUTH_USER_MODEL)),
                ('project_name', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='project_related_name', to='projectdata.project')),
            ],
        ),
        migrations.CreateModel(
            name='WeeklyReport',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('week_start_date', models.DateField()),
                ('week_end_date', models.DateField()),
                ('submit', models.BooleanField(default=False)),
                ('approve', models.BooleanField(default=False)),
                ('submit_date', models.DateField(blank=True, null=True)),
                ('approve_date', models.DateField(blank=True, null=True)),
                ('reject_date', models.DateField(blank=True, null=True)),
                ('employee', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='employee_report', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
