from django.contrib import admin
from account.models import Employee, CostCenter
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth import get_user_model

User = get_user_model()

class EmployeeModelAdmin(BaseUserAdmin):
    ## diplay list
    list_display = ('email', 'name', 'empID','organization', 'department','companyCode', 'otp', 'is_verified', 'is_manager', 
                    'is_employee','is_admin', 'is_superuser', 'cost_center','created_at','last_login')
    ## filter list
    list_filter = ('organization','is_manager','is_verified','is_employee','is_admin',)
    ## admin page user create option
    fieldsets = (
        ('User Credentials', {'fields': ('email', 'password','name','is_verified','empID','cost_center',)}),
        ('Organizational info', {'fields': ('organization','department','companyCode',)}),
        ('User Roles', {'fields': ('is_manager','is_employee','is_admin','created_at',)}),
        ('Django Permissions', {'fields': ('is_superuser',)}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'name', 'empID', 'password1', 'password2', 'organization', 'department','companyCode', 
                       'is_verified', 'is_manager', 'is_employee','is_admin','cost_center','created_at',),
        }),
    )


    search_fields = ('email','name','empID','organization','department','companyCode')
    ordering = ('email','empID','created_at')
    filter_horizontal = ()


admin.site.register(User, EmployeeModelAdmin)





@admin.register(CostCenter)
class CostCenterAdmin(admin.ModelAdmin):
    list_display = ['id','name', 'number','organization']

