from django.contrib import admin
from .models import Project


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['projectName', 'organization','projectCode', 'projectSubCode','projectManager','addedby','created_at']