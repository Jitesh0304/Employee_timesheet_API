from django.db import models
from projectdata.models import Project, ProjectSubcode, ProjectSubcodeActivity
from account.models import Employee, CostCenter
# from django.utils import timezone



class Status(models.Model):
    statusName = models.CharField(max_length=50, unique=True)   ## Save (1), Submit (2), ManagerReviewed (3), AdminReviewed (4)


    class Meta:
        db_table = "Status"
        verbose_name_plural = "Statuses"

    def __str__(self) -> str:
        return f"{self.id}_{self.statusName}"




class Timesheet(models.Model):
    location_choices = (
            ("WFH","WFH"),
            ("OnSite", "OnSite"),
            ("Office","Office")
    )
    date = models.DateField(db_index=True)
    status = models.ForeignKey(Status, on_delete=models.SET_NULL, null=True, related_name="timesheet_status")
    hours = models.FloatField(null=True, blank=True)
    project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True, related_name="timesheet_project")
    projectsubcode = models.ForeignKey(ProjectSubcode, on_delete=models.SET_NULL, null=True, related_name="timesheet_projectsubcode")
    project_subcode_activity = models.ForeignKey(ProjectSubcodeActivity, on_delete=models.SET_NULL, null=True, 
                                       related_name="timesheet_project_subcode_activity")
    employee = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, related_name="timesheet_employee", db_index=True)
    employee_costcenter = models.ForeignKey(CostCenter, on_delete=models.SET_NULL, null=True, 
                                            related_name="timesheet_emp_costcenter")
    bill = models.BooleanField(blank=True, null=True)
    location = models.CharField(max_length= 50, choices= location_choices)
    year_week = models.CharField(max_length= 30, null=True) ## 2024_20
    comment = models.CharField(max_length= 100, null=True, blank=True)


    class Meta:
        db_table = "Aspl_Timesheet"
        ordering = ["-date"]
        # indexes = [
        #     # models.Index(fields=['employee', 'date']),
        #     models.Index(fields=['employee',], name='employeeID_index'),
        #     models.Index(fields=['date',], name='date_index'),
        # ]

    def __str__(self) -> str:
        return str(self.id)


