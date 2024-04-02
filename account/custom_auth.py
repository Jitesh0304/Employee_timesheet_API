from django.contrib.auth import get_user_model
from rest_framework import authentication
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth.backends import BaseBackend
from rest_framework.permissions import BasePermission
from rest_framework.exceptions import PermissionDenied


class AdminPermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if user.is_admin:
            return True
        else:
            # return False
            raise PermissionDenied("You do not have permission... Only admin has permission")


class ManagerPermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if user.is_manager:
            return True
        else:
            # return False
            raise PermissionDenied("You do not have permission.... Only manager has permission")


User = get_user_model()


class CustomEmployeeAuthentication(BaseBackend):
    # def authenticate(self, request, emplID=None, companycode=None, password=None):
    def authenticate(self, empID=None, companyCode=None, password=None):
        if empID is None or companyCode is None or password is None:
            return None
        try:
            # Query for user using emplID and companyCode
            user = User.objects.get(empID=empID , companyCode=companyCode)
        except User.DoesNotExist:
            return None

        # If user is found, verify password
        if user.check_password(password):
            return user
        else:
            return None




# class CustomAuthentication(authentication.BaseAuthentication):
#     def authenticate(self, request):
#         # username = request.META.get('HTTP_X_USERNAME')
#         empl_id = request.data.get('emplID')
#         company_code = request.data.get('companyCode')
#         password = request.data.get('password')

#         if not empl_id or not company_code or not password:
#             return None
#         try:
#             user = User.objects.get(empl_id=empl_id, company_code=company_code)
#         except User.DoesNotExist:
#             # raise AuthenticationFailed('Invalid credentials.')
#             return None

#         if not user.check_password(password):
#             # raise AuthenticationFailed('Invalid credentials.')
#             return None

#         return (user, None)