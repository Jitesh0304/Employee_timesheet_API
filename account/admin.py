from django.contrib import admin
from account.models import CostCenter, Department, EmployeeRole, CompanyCode, Organization, OfficeBranch
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth import get_user_model

User = get_user_model()

class EmployeeModelAdmin(BaseUserAdmin):
    ## diplay list
    list_display = ('email', 'name', 'empID','organization', 'department','companyCode', 'otp', 'is_verified', 'role', 
                    'is_superuser', 'costcenter','created_at','last_login', 'doj', 'dol', 'branch')
    ## filter list
    list_filter = ('organization','is_verified','role','branch')
    ## admin page user create option
    fieldsets = (
        ('User Credentials', {'fields': ('email', 'password','name','empID','costcenter','is_verified', 'branch',)}),
        ('Organizational info', {'fields': ('organization','department','companyCode','doj', 'dol',)}),
        ('User Roles', {'fields': ('role',)}),
        ('Django Permissions', {'fields': ('is_superuser',)}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'name', 'empID', 'password1', 'password2', 'organization', 'department','companyCode', 'branch',
                       'is_verified', 'role', 'costcenter','doj', 'dol',),
        }),
    )


    search_fields = ('email','name','empID','organization','department','companyCode')
    ordering = ('email','empID','doj')
    filter_horizontal = ()


admin.site.register(User, EmployeeModelAdmin)





@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ['id','name']



@admin.register(CostCenter)
class CostCenterAdmin(admin.ModelAdmin):
    list_display = ['id','name', 'number']



@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['id','name']


@admin.register(EmployeeRole)
class EmployeeRoleAdmin(admin.ModelAdmin):
    list_display = ['id', 'roleName', 'description']


@admin.register(CompanyCode)
class CompanyCodeAdmin(admin.ModelAdmin):
    list_display = ['id','code','description']


@admin.register(OfficeBranch)
class OfficeBranchAdmin(admin.ModelAdmin):
    list_display = ['id', 'location', 'description']