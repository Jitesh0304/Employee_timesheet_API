from django.contrib import admin
from .models import DepartmentTracker, LeaveAppication



@admin.register(LeaveAppication)
class LeaveAppicationAdmin(admin.ModelAdmin):
    list_display = ['id','start_date','start_half', 'end_date','end_half', 'message', 'status','employee', 'applied_date',
                    'total_days','leave_type']


@admin.register(DepartmentTracker)
class DepartmentTrackerAdmin(admin.ModelAdmin):
    list_display = ['id', 'department', 'message', 'status', 'track_time']