# Generated by Django 5.0.6 on 2024-05-27 14:10

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('account', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Project',
            fields=[
                ('projectID', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('projectName', models.CharField(max_length=20, unique=True)),
                ('projectCode', models.CharField(max_length=4, unique=True)),
                ('complete', models.BooleanField(default=False)),
                ('created_at', models.DateField(auto_now_add=True)),
                ('organization', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='project_organization', to='account.organization')),
                ('projectAddedby', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='project_added_by', to=settings.AUTH_USER_MODEL)),
                ('projectManager', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='project_manager', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'Projects',
                'db_table': 'Aspl_Project',
            },
        ),
        migrations.CreateModel(
            name='ProjectSubcode',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('projectSubcode', models.CharField(max_length=4)),
                ('description', models.CharField(max_length=100, null=True)),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='project_subcode', to='projectdata.project')),
            ],
            options={
                'verbose_name_plural': 'projectSubcodes',
                'db_table': 'Aspl_projectSubcode',
                'unique_together': {('project', 'projectSubcode')},
            },
        ),
        migrations.CreateModel(
            name='ProjectSubcodeActivity',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30)),
                ('activityCode', models.CharField(max_length=10)),
                ('description', models.CharField(max_length=100, null=True)),
                ('projectsubcode', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='project_subcode_activity', to='projectdata.projectsubcode')),
            ],
            options={
                'verbose_name_plural': 'ProjectSubcode_Activities',
                'db_table': 'Aspl_ProjectSubcode_Activity',
                'unique_together': {('projectsubcode', 'activityCode')},
            },
        ),
    ]
