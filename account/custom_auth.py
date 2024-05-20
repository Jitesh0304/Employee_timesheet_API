from django.contrib.auth import get_user_model
from rest_framework import authentication
from django.contrib.auth.backends import BaseBackend
from rest_framework.permissions import BasePermission
from rest_framework.exceptions import PermissionDenied

# from rest_framework.authentication import BaseAuthentication
# from rest_framework.exceptions import AuthenticationFailed
# import jwt
# from django.conf import settings


class AdminPermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if user.role.id == 1:
            return True
        else:
            # return False
            raise PermissionDenied("You do not have permission... Only admin has permission")


class ManagerPermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if user.role.id in [1,2]:
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






# class JWTAuthentication(BaseAuthentication):
#     def authenticate(self, request):
#         token = self.get_token_from_header(request)
#         if token is None:
#             return None

#         try:
#             payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
#             user = User.objects.get(id=payload['user_id'])
#             return (user, None)
#         except jwt.ExpiredSignatureError:
#             raise AuthenticationFailed('Token has expired')
#         except jwt.InvalidTokenError:
#             raise AuthenticationFailed('Invalid token')
#         except User.DoesNotExist:
#             raise AuthenticationFailed('User not found')

#     def get_token_from_header(self, request):
#         auth_header = request.headers.get('Authorization')
#         if auth_header is None:
#             return None

#         parts = auth_header.split()
#         if parts[0].lower() != 'bearer' or len(parts) != 2:
#             return None

#         return parts[1]