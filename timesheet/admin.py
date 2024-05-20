from django.contrib import admin
from .models import Timesheet, Status



@admin.register(Timesheet)
class TimesheetAdmin(admin.ModelAdmin):
    list_display = ['id','date','status', 'hours','project', 'projectsubcode', 'project_subcode_activity','year_week',
                    'employee','employee_costcenter','bill', 'comment','location']


@admin.register(Status)
class StatusAdmin(admin.ModelAdmin):
    list_display = ['id', 'statusName']