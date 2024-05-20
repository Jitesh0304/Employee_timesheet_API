from django.db import models
from account.models import Employee, Organization



class Project(models.Model):
    projectID = models.BigAutoField(auto_created=True, serialize=False, primary_key=True)
    projectName = models.CharField(max_length=20, unique=True)
    projectCode = models.CharField(max_length=4, unique=True)
    projectManager = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, related_name="project_manager")
    projectAddedby = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True, related_name="project_added_by")
    organization = models.ForeignKey(Organization, on_delete=models.PROTECT, related_name='project_organization')
    complete = models.BooleanField(default=False)
    created_at = models.DateField(auto_now_add=True)


    class Meta:
        db_table = "Aspl_Project"
        # ordering = ["projectID"]
        verbose_name_plural = "Projects"


    def __str__(self) -> str:
        return f"{self.projectName}_{self.projectCode}"



class ProjectSubcode(models.Model):
    project = models.ForeignKey(Project, on_delete=models.PROTECT, related_name='project_subcode')
    projectSubcode = models.CharField(max_length=4)
    description = models.CharField(max_length=100, null=True)
    class Meta:
        unique_together = ('project', 'projectSubcode')
        db_table = "Aspl_projectSubcode"
        verbose_name_plural = "projectSubcodes"


    def __str__(self) -> str:
        return f"{self.project.pk}_{self.projectSubcode}"



class ProjectSubcodeActivity(models.Model):
    projectsubcode = models.ForeignKey(ProjectSubcode, on_delete=models.PROTECT, related_name='project_subcode_activity')
    name = models.CharField(max_length=30)
    activityCode = models.CharField(max_length=10)
    description = models.CharField(max_length=100, null=True)

    class Meta:
        unique_together = ('projectsubcode', 'activityCode')
        db_table = "Aspl_ProjectSubcode_Activity"
        verbose_name_plural = "ProjectSubcode_Activities"


    def __str__(self) -> str:
        return f"{self.projectsubcode.project.pk}_{self.activityCode}"