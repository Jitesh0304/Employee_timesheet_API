from django.db import models
from projectdata.models import Project
from account.models import Employee
from django.utils import timezone




class Timesheet(models.Model):
    # class All_choice:
    #     def __init__(self):
    #         self.choices = {
    #                 "Submit": "Submit",
    #                 "NotSubmit": "NotSubmit"
    #         }
    # status = models.CharField(max_length=50, choices= All_choice().choices)
    status_choices = (
            ("Submit", "Submit"),
            ("NotSubmit", "NotSubmit")
    )
    location_choices = (
            ("WFH","WFH"),
            ("OnSite", "OnSite"),
            ("Office","Office")
    )
    day = models.CharField(max_length=50)
    date = models.DateField()
    status = models.CharField(max_length=50, choices= status_choices, null=True, blank=True)
    hours = models.FloatField(null=True, blank=True)
    organization = models.CharField(max_length= 100, null=True, blank=True)
    project_code = models.CharField(max_length= 100, null=True, blank=True)
    project_subcode = models.CharField(max_length= 100, null=True, blank=True)
    project_name = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True, related_name="project_related_name")
    employee = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True, related_name="employee_related")
    bill = models.CharField(max_length= 100, null=True, blank=True)
    location = models.CharField(max_length= 100, choices= location_choices)
    comment = models.CharField(max_length= 300, null=True, blank=True)
    submit = models.BooleanField(default=False)
    manager_approve = models.BooleanField(default=False)
    admin_approve = models.BooleanField(default=False)

    def __str__(self) -> str:
        return str(self.id)





class WeeklyReport(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True, related_name="employee_report")
    week_start_date = models.DateField()
    week_end_date = models.DateField()
    submit_timesheet = models.ManyToManyField(Timesheet, blank=True, related_name="week_submited_timesheet")
    submit = models.BooleanField(default=False)
    managerApprove = models.BooleanField(default=False)
    adminApprove = models.BooleanField(default=False)
#     approve = models.BooleanField(default=False)
    submit_date = models.DateField(null=True, blank=True)
    approve_data = models.JSONField(default=list, null=True, blank=True)
    reject_data = models.JSONField(default=list, null=True, blank=True)

    def __str__(self) -> str:
        return str(self.id)