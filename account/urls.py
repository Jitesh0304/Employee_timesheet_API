from django.urls import path, include
from .views import CustomTokenObtainPairView, CustomTokenRefreshView, EmployeeRegistrationView, EmployeeLoginView, \
        EmployeeProfileView, AllEmployeeProfileView, EmployeeChangePasswordView, SendPasswordResetEmailView, \
        EmployeePasswordResetView, EmployeeRegistrationByAdminView, DeleteEmployeeView, CostCenterView, DepartmentView, \
        EmployeeRoleView, CompanyCodeView, OrganizationView, OfficeBranchView, AdminUpdateEmployeeProfileView
from rest_framework_simplejwt.views import TokenVerifyView 


urlpatterns = [
    path('gettoken/',CustomTokenObtainPairView.as_view(), name= 'token_pair'),
    path('refreshtoken/', CustomTokenRefreshView.as_view(), name= 'token_resfresh'),
    path('verifytoken/',TokenVerifyView.as_view(), name= 'token_verify'),
    path('register/', EmployeeRegistrationView.as_view(), name='register'),
    path('registerby/', EmployeeRegistrationByAdminView.as_view(), name='registerby'),
    path('login/', EmployeeLoginView.as_view(), name= 'login'),
    path('profile/', EmployeeProfileView.as_view(), name= 'profile'),
    path('allprofile/', AllEmployeeProfileView.as_view(), name= 'allprofile'),
    path('userprofile/<str:empid>/', AllEmployeeProfileView.as_view(), name= 'allprofile'),
    path('changepassword/', EmployeeChangePasswordView.as_view(), name= 'changepassword'),
    path('send_reset_password_email/', SendPasswordResetEmailView.as_view(), name= 'send_reset_password_email'),
    path('reset_password/', EmployeePasswordResetView.as_view(), name= 'reset_password'),
    path('deleteuser/<str:empid>/', DeleteEmployeeView.as_view(), name= 'deleteuser'),
    path('employeupdate/<str:empid>/', AdminUpdateEmployeeProfileView.as_view(), name='employeupdate'),

    path('costcenter/', CostCenterView.as_view(), name= 'costcenter'),
    path('costcenterupdate/<int:pk>/', CostCenterView.as_view(), name= 'costcenterupdate'),
    path('department/', DepartmentView.as_view(), name= 'department'),
    path('departmentupdate/<int:pk>/', DepartmentView.as_view(), name= 'departmentupdate'),
    path('role/', EmployeeRoleView.as_view(), name= 'role'),
    path('roleupdate/<int:pk>/', EmployeeRoleView.as_view(), name= 'roleupdate'),
    path('companycode/', CompanyCodeView.as_view(), name= 'companycode'),
    path('companycodeupdate/<int:pk>/', CompanyCodeView.as_view(), name= 'companycodeupdate'),
    path('org/', OrganizationView.as_view(), name= 'org'),
    path('orgupdate/<int:pk>/', OrganizationView.as_view(), name= 'orgupdate'),
    path('branch/', OfficeBranchView.as_view(), name= 'branch'),
    path('branchupdate/<int:pk>/', OfficeBranchView.as_view(), name= 'branchupdate'),
]


