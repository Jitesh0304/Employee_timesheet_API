
# from rest_framework.authentication import BaseAuthentication
# from rest_framework.exceptions import AuthenticationFailed
# from django.contrib.auth.models import User
# import jwt
# from django.conf import settings


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
