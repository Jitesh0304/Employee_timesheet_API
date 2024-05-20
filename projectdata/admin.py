from django.contrib import admin
from .models import Project, ProjectSubcode, ProjectSubcodeActivity


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['projectID','projectName', 'projectCode', 'projectManager', 'projectAddedby','created_at', 'complete']


@admin.register(ProjectSubcode)
class ProjectCodeAdmin(admin.ModelAdmin):
    list_display = ['id','project', 'projectSubcode', 'description']


@admin.register(ProjectSubcodeActivity)
class ProjectSubcodeActivityAdmin(admin.ModelAdmin):
    list_display = ['id','projectsubcode', 'name', 'activityCode', 'description']