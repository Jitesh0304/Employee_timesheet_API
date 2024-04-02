from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
from django.utils import timezone

# Create your models here.

class EmployeeManager(BaseUserManager):
    def create_user(self, email, name, empID, organization, department, companyCode, cost_center,
                    is_employee=None, is_manager=None, password=None, password2 = None, ):

        if not email:
            raise ValueError('Users must have an email address')
        if not empID:
            raise ValueError('Users must have an empID')
        if not name:
            raise ValueError('Users must provide his full name')
        if not organization:
            raise ValueError('Users must provide organization name')

        user = self.model(
            email = self.normalize_email(email),
            name = name,
            empID = empID,
            organization = organization,
            department = department,
            companyCode = companyCode,
            is_employee = is_employee,
            is_manager = is_manager,
            cost_center = cost_center,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name,empID, organization, password=None):   
        user = self.create_user(
            email,
            name = name,
            empID = 'Django_Admin',
            organization= organization,
            department = "Superuser",
            companyCode = "Django_Admin",
            password = password,
            is_employee=True,
            is_manager= True,
            cost_center = "Superuser"
        )
        user.is_superuser = True
        user.is_admin = True
        user.created_at = timezone.now()
        user.save(using=self._db)
        return user
    


class Employee(AbstractBaseUser):
    email = models.EmailField(unique=True, max_length=255)
    name = models.CharField(max_length=100, null=True, blank=True)
    empID = models.CharField(max_length=100, primary_key=True)
    organization = models.CharField(max_length=100, blank=False, null= False)
    department = models.CharField(max_length=100, null=True, blank=True)
    companyCode = models.CharField(max_length=100, null=True, blank=True)
    otp = models.CharField(max_length=10, null=True, blank=True, default='')
    is_verified = models.BooleanField(default=True)
    is_manager = models.BooleanField(default=False)
    is_employee = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    cost_center = models.CharField(max_length=200, null=True, blank=True)
    created_at = models.DateTimeField(null=True, blank=True)
    last_login = models.DateTimeField(null=True, blank=True)

    USERNAME_FIELD = 'empID'
    REQUIRED_FIELDS = ['name','organization','email',]

    objects = EmployeeManager()

    def __str__(self):
        return self.name+'_'+self.empID

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        # return True
        return self.is_superuser

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_superuser






class CostCenter(models.Model):
    name = models.CharField(max_length=100)
    number = models.IntegerField()
    organization = models.CharField(max_length=100, blank=True, null= True)