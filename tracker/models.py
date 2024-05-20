from django.db import models
from account.models import Department, Employee
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


class DepartmentTracker(models.Model):
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='department_tracker')
    message = models.TextField()
    status = models.CharField(max_length=20, blank=True, null=True) ## NotSeen,  ManagerSeen,   AdminSeen
    track_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "Department_tracker"
        verbose_name_plural = "Department Trackers"

    def __str__(self) -> str:
        return f"{self.id}"



class LeaveAppication(models.Model):
    HALF_DAY_CHOICES = (
        ("first_half", "First Half"),
        ("second_half", "Second Half"),
        )
    LEAVE_TYPE = (
        ("paid_leave", "paid_leave"),
        ("loss_of_paid_leave", "loss_of_paid_leave"),
        )
    start_date = models.DateField()
    start_half = models.CharField(max_length=20, choices=HALF_DAY_CHOICES)
    end_date = models.DateField()
    end_half = models.CharField(max_length=20, choices=HALF_DAY_CHOICES)
    message = models.TextField()
    status = models.CharField(max_length=30)    ## NotSeen
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="leave_appli_employee")
    applied_date = models.DateTimeField(auto_now_add=True)
    total_days = models.FloatField(blank=True, null=True)
    leave_type = models.CharField(max_length=30, choices=LEAVE_TYPE)
    approver = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="leave_approver")


    class Meta:
        db_table = "Leave_Appication"
        verbose_name_plural = "Leave Appications"

    def __str__(self) -> str:
        return f"{self.id}"


    def clean(self):
        # Call the parent class's clean method to maintain other validations.
        super().clean()

        if self.start_date > self.end_date:
            raise ValidationError(_("The start date cannot be later than the end date."))
        num_total_date = (self.end_date - self.start_date).days
        if num_total_date < 1:
            if self.end_date == self.start_date:
                if self.end_half == self.start_half:
                    num_total_date = 0.5
                else:
                    num_total_date = 1
        self.total_days = num_total_date

        # if self.start_date == self.end_date:
        #     if self.start_half == "second_half" and self.end_half == "first_half":
        #         raise ValidationError(_("For the same day, 'start_half' cannot be 'second_half' while 'end_half' is 'first_half'."))



    # def save(self, *args, **kwargs):
    #     num_total_date = (self.end_date - self.start_date).days
    #     if num_total_date < 0:
    #         raise ValidationError("Start date must be before or equal to end date")
    #     if num_total_date < 1:
    #         if self.end_date == self.start_date:
    #             if self.end_half == self.start_half:
    #                 num_total_date = 0.5
    #             else:
    #                 num_total_date = 1
    #     self.total_days = num_total_date
    #     super().save(*args, **kwargs)  # Call the "real" save() method.