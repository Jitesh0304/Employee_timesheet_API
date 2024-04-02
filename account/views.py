from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from account.serializers import CustomTokenObtainPairSerializer, CustomTokenRefreshSerializer, \
            EmployeeRegistrationSerializer,EmployeeLoginSerializer, EmployeeProfileSerializer, EmployeeChangePassword, \
            SendPasswordResetEmailSerializer, EmployeePasswordResetSerializer, EmployeeRegistrationByAdminSerializer, \
            CostCenterSerializer
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from .models import Employee, CostCenter
from django.shortcuts import render
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.utils import timezone
from rest_framework.pagination import PageNumberPagination
from .custom_auth import AdminPermission

# Create your views here.


       ## home page
def homepage(request):
    return render(request, 'account/home.html')




class CostCenterView(APIView):
    permission_classes = [IsAuthenticated, AdminPermission]

    def post(self, request, format=None):
        try:
            user = request.user
            serializer = CostCenterSerializer(data= request.data, context={'request':request})
            if serializer.is_valid():
                if CostCenter.objects.filter(name= serializer.validated_data['name'],
                                              number=serializer.validated_data['number']).exists():
                    return Response({'msg':'Cost center having same name and number is alredy exists'}, 
                                    status=status.HTTP_400_BAD_REQUEST)
                serializer.save()
                return Response({'msg':'New cost-center data saved ...'}, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'msg':str(e)}, status=status.HTTP_400_BAD_REQUEST)


    def get(self, request, format=None):
        try:
            user = request.user
            all_cost_centrs = CostCenter.objects.filter(organization= user.organization)
            # serializer = CostCenterSerializer(all_cost_centrs, many=True)
            # print(serializer.data)
            cost_center_data = {data.name:data.number for data in all_cost_centrs}
            return Response({'msg':cost_center_data}, status= status.HTTP_200_OK)
        except Exception as e:
            return Response({'msg':str(e)}, status=status.HTTP_400_BAD_REQUEST)



    ## generate new token during login time
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
        ## send user data by a post request
    def post(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user = serializer.user
                # Check if the user is verified
        # if not user.is_verified:
        #     return Response({'msg': 'User is not verified'}, status=status.HTTP_400_BAD_REQUEST)
            user = Employee.objects.get(empID = user)
                ## take the token from the serializer
            token = serializer.validated_data
                ## create refresh_token
            refresh_token = RefreshToken.for_user(user)
                ## add user details if required
            response_data = {
                'access': str(token['access']),
                'refresh': str(refresh_token),
                'is_manager': user.is_manager,
                'is_employee': user.is_employee,
                'is_admin': user.is_admin,
            }
            user.last_login = timezone.now()
            user.save()
            return Response(response_data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'msg':str(e)}, status=status.HTTP_400_BAD_REQUEST)


        ## regenerate the access token using refresh token
class CustomTokenRefreshView(TokenRefreshView):
    serializer_class = CustomTokenRefreshSerializer
    def post(self, request, *args, **kwargs):               ## use this or not .. you will get result
        data = super().post(request, *args, **kwargs)
        return data



    # create new user 
class EmployeeRegistrationView(APIView):
    def post(self, request, format =None):
        try:
            serializer = EmployeeRegistrationSerializer(data = request.data)
            if serializer.is_valid():
                user = serializer.save()
                user.created_at= timezone.now()
                user.save()
                # sent_otp_by_email(serializer.data['email'])
                return Response({'msg': 'Registration Successful...'}, status.HTTP_201_CREATED)
            return Response({'msg': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'msg': str(e)}, status=status.HTTP_400_BAD_REQUEST)





        ## This is for User login
class EmployeeLoginView(APIView):
    def post(self, request, format= None):
        try:
            serializer = EmployeeLoginSerializer(data= request.data)
            if serializer.is_valid():
                
                empID = serializer.data.get('empID')
                password = serializer.data.get('password')
                companyCode = serializer.data.get('companyCode')
                # user_auth = CustomEmployeeAuthentication.authenticate(self, empID= empID, password = password, companyCode=companyCode)

                user_auth = authenticate(empID= empID, password = password)
                if user_auth is not None:
                    if user_auth.companyCode != companyCode:
                        return Response({'msg':'wrong credential'}, status=status.HTTP_404_NOT_FOUND)
                    user = Employee.objects.get(empID= empID, companyCode=companyCode)
                        ## check the user account is verified or not
                    if user.is_verified == True:
                            ## generate the token using serializer class
                        access = CustomTokenObtainPairSerializer.get_token(user)
                            ## generate the refresh token
                        refresh = RefreshToken.for_user(user)
                        token = {
                            'access':str(access.access_token),
                            'refresh':str(refresh),
                            'is_manager': user.is_manager,
                            'is_employee': user.is_employee,
                            'is_admin': user.is_admin
                            }
                        user.last_login = timezone.now()
                        user.save()
                        return Response({'token': token}, status=status.HTTP_200_OK)
                    else:
                        return Response({'msg':'User is not verified'}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response({'msg':'wrong credential'},status=status.HTTP_404_NOT_FOUND)
            else:
                return Response({'msg':serializer.errors}, status= status.HTTP_400_BAD_REQUEST)    
        except Exception as e:
            return Response({'msg': str(e)}, status=status.HTTP_400_BAD_REQUEST)





class EmployeeProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format= None):
        try:
            user = request.user
            serializer = EmployeeProfileSerializer(user, context={"user":user})
            return Response(serializer.data, status= status.HTTP_200_OK)
        except Exception as e:
            return Response({'msg': str(e)}, status=status.HTTP_400_BAD_REQUEST)





class AllEmployeeProfileView(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = PageNumberPagination

    def get(self, request, format= None):
        try:
            user = request.user
            if user.is_admin:
                allUsers = Employee.objects.filter(organization = user.organization, is_verified= True).order_by(
                                                                                                'email', '-created_at')
                serializer = EmployeeProfileSerializer(allUsers, many = True, context={"user":user})
                return Response({'msg':serializer.data}, status= status.HTTP_200_OK)
            else:
                return Response({'msg':'You have no permission to see all Users list'}, status= status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'msg': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    ## pagination
# class AllEmployeeProfileView(APIView):
#     permission_classes = [IsAuthenticated]
#     pagination_class = PageNumberPagination

#     def get(self, request, format= None):
#         try:
#             user = request.user
#             if user.is_manager:
#                 paginator = self.pagination_class()
#                 # paginator.page_size = 2
#                 allUsers = Employee.objects.filter(organization = user.organization, is_verified= True).order_by(
#                                                                                                 'email', '-created_at')
#                 result_page = paginator.paginate_queryset(allUsers, request)
#                 serializer = EmployeeProfileSerializer(result_page, many = True, context={"user":user})
#                 return paginator.get_paginated_response(serializer.data)
#             else:
#                 return Response({'msg':'You have no permission to see all Users list'}, status= status.HTTP_400_BAD_REQUEST)
#         except Exception as e:
#             return Response({'msg': str(e)}, status=status.HTTP_400_BAD_REQUEST)




            ## this is for password change
class EmployeeChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, format= None):
        try:
            serializer = EmployeeChangePassword(data = request.data, context ={'user':request.user})
            if serializer.is_valid():
                return Response({'msg':'Password Changed Successfully'}, status.HTTP_200_OK)
            return Response({'msg':serializer.errors}, status= status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'msg': str(e)}, status=status.HTTP_400_BAD_REQUEST)





class SendPasswordResetEmailView(APIView):
    def post(self, request, format= None):
        try:
            serializer = SendPasswordResetEmailSerializer(data = request.data)
            if serializer.is_valid():
                return Response({'msg':'Password Reset OTP has been sent to your Email. Please check your Email'},
                                status= status.HTTP_200_OK)
            else:
                return Response({'msg':serializer.errors}, status= status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'msg': str(e)}, status=status.HTTP_400_BAD_REQUEST)





class EmployeePasswordResetView(APIView):
    def post(self, request, format= None):
        try:
            serializer = EmployeePasswordResetSerializer(data= request.data)

            if serializer.is_valid():
                
                return Response({'msg':'Password reset successfull'}, status= status.HTTP_200_OK)
            else:
                return Response({'msg':serializer.errors}, status= status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'msg': str(e)}, status=status.HTTP_400_BAD_REQUEST)






class EmployeeRegistrationByAdminView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format =None):
        try:
            user = request.user
            ## check the request user is manager or not
            if  user.is_manager:
                serializer = EmployeeRegistrationByAdminSerializer(data = request.data, context={'request':request})
                if serializer.is_valid():
                        ## create new user
                    new_user = serializer.save()
                    print(serializer.validated_data['is_manager'])
                    new_user.is_manager = serializer.validated_data['is_manager']
                    new_user.created_at= timezone.now()
                    new_user.save()
                    return Response({'msg':'Registarion Successful...'}, status.HTTP_201_CREATED)
                else:
                    return Response({'msg':serializer.errors}, status= status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'msg':"You have no permission...."}, status= status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'msg':str(e)}, status= status.HTTP_400_BAD_REQUEST)




class DeleteEmployeeView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, empid, format=None):
        try:
            user = self.request.user
            if  user.is_manager:
                    try:
                        employee_data = Employee.objects.get(empID=empid, organization=user.organization)
                    except Exception as e:
                        return Response({'msg': f'User with {empid} this name does not exist'}, status=status.HTTP_400_BAD_REQUEST)
                    employee_data.delete()
                    return Response({'msg': 'User has been deleted successfully'}, status=status.HTTP_200_OK)
            else:
                return Response({'msg': 'You have no permission to delete a user'}, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({'msg': str(e)}, status=status.HTTP_400_BAD_REQUEST)

