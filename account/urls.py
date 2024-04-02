from django.urls import path, include
from .views import CustomTokenObtainPairView, CustomTokenRefreshView, EmployeeRegistrationView, EmployeeLoginView, \
        EmployeeProfileView, AllEmployeeProfileView, EmployeeChangePasswordView, SendPasswordResetEmailView, \
        EmployeePasswordResetView, EmployeeRegistrationByAdminView, DeleteEmployeeView, CostCenterView
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
    path('changepassword/', EmployeeChangePasswordView.as_view(), name= 'changepassword'),
    path('send_reset_password_email/', SendPasswordResetEmailView.as_view(), name= 'send_reset_password_email'),
    path('reset_password/', EmployeePasswordResetView.as_view(), name= 'reset_password'),
    path('deleteuser/<str:empid>/', DeleteEmployeeView.as_view(), name= 'deleteuser'),
    path('costcenter/', CostCenterView.as_view(), name= 'costcenter'),
]


