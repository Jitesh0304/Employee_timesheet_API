from django.db import models
from account.models import Employee


class Project(models.Model):
    projectName = models.CharField(max_length=100, primary_key=True)
    projectCode = models.CharField(max_length=100, unique=True)
    # projectSubCode = models.CharField(max_length=100, unique=True)
    projectSubCode = models.JSONField(default=list)
    projectManager = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, related_name="project_manager")
    addedby = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True, related_name="project_added_by")
    complete = models.BooleanField(default=False)
    organization = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateField(blank=True, null=True)



    def __str__(self) -> str:
        return self.projectName