from django.contrib import admin
from .models import Timesheet, WeeklyReport



@admin.register(Timesheet)
class TimesheetAdmin(admin.ModelAdmin):
    list_display = ['id','day', 'date','status', 'hours','organization','project_code','project_subcode', 'project_name',
                    'employee','bill','location','comment','submit','manager_approve','admin_approve']



@admin.register(WeeklyReport)
class WeeklyReportAdmin(admin.ModelAdmin):
    ##  filter_horizontal = ('submit_timesheet',)  # Use filter_horizontal for a visually appealing interface for many-to-many fields
    ##  raw_id_fields = ('submit_timesheet',)  # Use raw_id_fields for many-to-many fields with a large number of items
    list_display = ['id','employee', 'week_start_date','week_end_date', 'submit','managerApprove','submit_date',
                    'display_timesheet_list', 'adminApprove', 'approve_data','reject_data']
    

    def display_timesheet_list(self, obj):
        # id_list = []
        # for onedata in obj.submit_timesheet.all():
        #     id_list.append(onedata.id)
        return list(obj.submit_timesheet.values_list('id', flat=True))
    
    display_timesheet_list.short_description = 'Timesheet IDs list'