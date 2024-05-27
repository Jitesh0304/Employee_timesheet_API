from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from account.serializers import CustomTokenObtainPairSerializer, CustomTokenRefreshSerializer, \
            EmployeeRegistrationSerializer,EmployeeLoginSerializer, EmployeeProfileSerializer, EmployeeChangePassword, \
            SendPasswordResetEmailSerializer, EmployeePasswordResetSerializer, EmployeeRegistrationByAdminSerializer, \
            CostCenterSerializer, DepartmentSerializer, EmployeeRoleSerializer, CompanyCodeSerializer, OrganizationSerializer, \
            OfficeBranchSerializer, AdminUpdateEmployeeProfileSerializer
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from .models import Employee, CostCenter, Department, EmployeeRole, CompanyCode, Organization, OfficeBranch
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.utils import timezone
from rest_framework.pagination import PageNumberPagination
from .custom_auth import AdminPermission, ManagerPermission





       ## home page
def homepage(request):
    return render(request, 'account/home.html')



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
                'role': user.role.roleName
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
            all_cost_centrs = CostCenter.objects.all()
            # serializer = CostCenterSerializer(all_cost_centrs, many=True)
            # print(serializer.data)
            cost_center_data = {data.name:data.number for data in all_cost_centrs}
            return Response({'msg':cost_center_data}, status= status.HTTP_200_OK)
        except Exception as e:
            return Response({'msg':str(e)}, status=status.HTTP_400_BAD_REQUEST)


    def patch(self, request, pk, format=None):
        try:
            try:
                cost_center_data = CostCenter.objects.get(id = pk)
            except Exception:
                return Response({'msg':'Coscenter does not exist with this ID'}, status=status.HTTP_400_BAD_REQUEST)
            serializer = CostCenterSerializer(cost_center_data, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({'msg':'Costacenter data updated ...'}, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'msg':str(e)}, status=status.HTTP_400_BAD_REQUEST)




class DepartmentView(APIView):
    permission_classes = [IsAuthenticated, AdminPermission]

    def post(self, request, format=None):
        try:
            user = request.user
            serializer = DepartmentSerializer(data= request.data, context={'request':request})
            if serializer.is_valid():
                serializer.save()
                return Response({'msg':'New deprtment data saved ...'}, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'msg':str(e)}, status=status.HTTP_400_BAD_REQUEST)


    def get(self, request, format=None):
        try:
            user = request.user
            all_department = Department.objects.all()
            department_data = {data.id:data.name for data in all_department}
            return Response({'msg':department_data}, status= status.HTTP_200_OK)
        except Exception as e:
            return Response({'msg':str(e)}, status=status.HTTP_400_BAD_REQUEST)


    def patch(self, request, pk, format=None):
        try:
            try:
                department_data = Department.objects.get(id = pk)
            except Exception:
                return Response({'msg':'Department does not exist with this ID'}, status=status.HTTP_400_BAD_REQUEST)
            serializer = DepartmentSerializer(department_data, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({'msg':'Department data updated ...'}, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'msg':str(e)}, status=status.HTTP_400_BAD_REQUEST)



class EmployeeRoleView(APIView):
    permission_classes = [IsAuthenticated, AdminPermission]

    def post(self, request, format=None):
        try:
            user = request.user
            serializer = EmployeeRoleSerializer(data= request.data, context={'request':request})
            if serializer.is_valid():
                serializer.save()
                return Response({'msg':'New role saved ...'}, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'msg':str(e)}, status=status.HTTP_400_BAD_REQUEST)


    def get(self, request, format=None):
        try:
            user = request.user
            all_roles = EmployeeRole.objects.all()
            role_data = {data.id:data.roleName for data in all_roles}
            return Response({'msg':role_data}, status= status.HTTP_200_OK)
        except Exception as e:
            return Response({'msg':str(e)}, status=status.HTTP_400_BAD_REQUEST)


    def patch(self, request, pk, format=None):
        try:
            try:
                employeeRole_data = EmployeeRole.objects.get(id = pk)
            except Exception:
                return Response({'msg':'EmployeeRole does not exist with this ID'}, status=status.HTTP_400_BAD_REQUEST)
            serializer = EmployeeRoleSerializer(employeeRole_data, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({'msg':'EmployeeRole data updated ...'}, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'msg':str(e)}, status=status.HTTP_400_BAD_REQUEST)



class CompanyCodeView(APIView):
    permission_classes = [IsAuthenticated, AdminPermission]

    def post(self, request, format=None):
        try:
            user = request.user
            serializer = CompanyCodeSerializer(data= request.data, context={'request':request})
            if serializer.is_valid():
                serializer.save()
                return Response({'msg':'New companycode saved ...'}, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'msg':str(e)}, status=status.HTTP_400_BAD_REQUEST)



    def get(self, request, format=None):
        try:
            user = request.user
            all_codes = CompanyCode.objects.all()
            code_data = {data.id:data.code for data in all_codes}
            return Response({'msg':code_data}, status= status.HTTP_200_OK)
        except Exception as e:
            return Response({'msg':str(e)}, status=status.HTTP_400_BAD_REQUEST)


    def patch(self, request, pk, format=None):
        try:
            try:
                companyCode_data = CompanyCode.objects.get(id = pk)
            except Exception:
                return Response({'msg':'CompanyCode does not exist with this ID'}, status=status.HTTP_400_BAD_REQUEST)
            serializer = CompanyCodeSerializer(companyCode_data, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({'msg':'CompanyCode data updated ...'}, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'msg':str(e)}, status=status.HTTP_400_BAD_REQUEST)



class OrganizationView(APIView):
    permission_classes = [IsAuthenticated, AdminPermission]

    def post(self, request, format=None):
        try:
            user = request.user
            serializer = OrganizationSerializer(data= request.data, context={'request':request})
            if serializer.is_valid():
                serializer.save()
                return Response({'msg':'New organization saved ...'}, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'msg':str(e)}, status=status.HTTP_400_BAD_REQUEST)



    def get(self, request, format=None):
        try:
            user = request.user
            all_orgs = Organization.objects.all()
            orgs_data = {data.id:data.name for data in all_orgs}
            return Response({'msg':orgs_data}, status= status.HTTP_200_OK)
        except Exception as e:
            return Response({'msg':str(e)}, status=status.HTTP_400_BAD_REQUEST)


    def patch(self, request, pk, format=None):
        try:
            try:
                organization_data = Organization.objects.get(id = pk)
            except Exception:
                return Response({'msg':'Organization does not exist with this ID'}, status=status.HTTP_400_BAD_REQUEST)
            serializer = OrganizationSerializer(organization_data, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({'msg':'Organization data updated ...'}, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'msg':str(e)}, status=status.HTTP_400_BAD_REQUEST)




class OfficeBranchView(APIView):
    permission_classes = [IsAuthenticated, AdminPermission]

    def post(self, request, format=None):
        try:
            user = request.user
            serializer = OfficeBranchSerializer(data= request.data, context={'request':request})
            if serializer.is_valid():
                serializer.save()
                return Response({'msg':'New branch saved ...'}, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'msg':str(e)}, status=status.HTTP_400_BAD_REQUEST)



    def get(self, request, format=None):
        try:
            user = request.user
            all_branchs = OfficeBranch.objects.all()
            branch_data = {data.id:data.location for data in all_branchs}
            return Response({'msg': branch_data}, status= status.HTTP_200_OK)
        except Exception as e:
            return Response({'msg':str(e)}, status=status.HTTP_400_BAD_REQUEST)


    def patch(self, request, pk, format=None):
        try:
            try:
                officeBranch_data = OfficeBranch.objects.get(id = pk)
            except Exception:
                return Response({'msg':'OfficeBranch does not exist with this ID'}, status=status.HTTP_400_BAD_REQUEST)
            serializer = OfficeBranchSerializer(officeBranch_data, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({'msg':'OfficeBranch data updated ...'}, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'msg':str(e)}, status=status.HTTP_400_BAD_REQUEST)




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
                    if user_auth.companyCode.code != companyCode:
                        return Response({'msg':'wrong credential'}, status=status.HTTP_404_NOT_FOUND)
                        ## check the user account is verified or not
                    if user_auth.is_verified == True:
                            ## generate the token using serializer class
                        access = CustomTokenObtainPairSerializer.get_token(user_auth)
                            ## generate the refresh token
                        refresh = RefreshToken.for_user(user_auth)
                        token = {
                            'access':str(access.access_token),
                            'refresh':str(refresh),
                            'role': user_auth.role.roleName
                            }
                        user_auth.last_login = timezone.now()
                        user_auth.save()
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
    permission_classes = [IsAuthenticated, ManagerPermission]
    pagination_class = PageNumberPagination

    def get(self, request, empid=None, format= None):
        try:
            user = request.user
            if empid:
                try:
                    userdata = Employee.objects.get(empID= empid)
                except Exception:
                    return Response({'msg': 'User with this employee ID does not exist ..'}, status=status.HTTP_400_BAD_REQUEST)

                serializer = EmployeeProfileSerializer(userdata, context={"user":user})
                return Response({'msg':serializer.data}, status= status.HTTP_200_OK)
            
            allUsers = Employee.objects.filter(is_verified= True).order_by('-created_at').values(
                'empID','name', 'department__name').exclude(empID=user.empID)
            # serializer = EmployeeProfileSerializer(allUsers, many = True, context={"user":user})
            return Response({'msg':allUsers}, status= status.HTTP_200_OK)
        except Exception as e:
            return Response({'msg': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    ## pagination
# class AllEmployeeProfileView(APIView):
#     permission_classes = [IsAuthenticated]
#     pagination_class = PageNumberPagination

#     def get(self, request, format= None):
#         try:
#             user = request.user
#             if user.role.id == 2:
#                 paginator = self.pagination_class()
#                 # paginator.page_size = 2
#                 allUsers = Employee.objects.filter(is_verified= True).order_by(
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
    permission_classes = [IsAuthenticated, AdminPermission]

    def post(self, request, format =None):
        try:
            user = request.user
            ## check the request user is manager or not
            serializer = EmployeeRegistrationByAdminSerializer(data = request.data, context={'request':request})
            if serializer.is_valid():
                    ## create new user
                new_user = serializer.save()
                new_user.created_at= timezone.now()
                new_user.save()
                return Response({'msg':'Registarion Successful...'}, status.HTTP_201_CREATED)
            else:
                return Response({'msg':serializer.errors}, status= status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'msg':str(e)}, status= status.HTTP_400_BAD_REQUEST)



class AdminUpdateEmployeeProfileView(APIView):
    permission_classes = [IsAuthenticated, AdminPermission]

    def patch(self, request, empid, format =None):
        try:
            user = request.user
            try:
                emp_data = Employee.objects.get(empID = empid)
                emp_data.user_permission.add()
            except Exception:
                return Response({'msg':'Employee does not exist with the given empID'}, status= status.HTTP_400_BAD_REQUEST)
            serializer = AdminUpdateEmployeeProfileSerializer(emp_data, data = request.data, 
                                                              context={'employee_data':emp_data, 'request':request}, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({'msg':'Employee data updated successful...'}, status.HTTP_202_ACCEPTED)
            return Response({'msg':serializer.errors}, status= status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'msg':str(e)}, status= status.HTTP_400_BAD_REQUEST)




class DeleteEmployeeView(APIView):
    permission_classes = [IsAuthenticated, AdminPermission]

    def delete(self, request, empid, format=None):
        try:
            user = self.request.user
            try:
                employee_data = Employee.objects.get(empID=empid)
            except Exception as e:
                return Response({'msg': f'User with {empid} this name does not exist'}, status=status.HTTP_400_BAD_REQUEST)
            employee_data.delete()
            return Response({'msg': 'User has been deleted successfully'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'msg': str(e)}, status=status.HTTP_400_BAD_REQUEST)


