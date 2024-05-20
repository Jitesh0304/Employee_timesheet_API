from rest_framework import serializers
from account.models import Employee, CostCenter, Department, Organization, OfficeBranch, CompanyCode, EmployeeRole
from account.utils import reset_pass_otp_email, main_email#department_change_email
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer 
from rest_framework_simplejwt.tokens import RefreshToken 
import jwt, asyncio
from decouple import config
from django.utils import timezone
from tracker.models import DepartmentTracker




class CostCenterSerializer(serializers.ModelSerializer):
    class Meta:
        model = CostCenter
        fields = "__all__"

    def update(self, instance, validated_data):
        # return super().update(instance, validated_data)
        instance.name = validated_data.get('name', instance.name)
        instance.number = validated_data.get('number', instance.number)
        instance.description = validated_data.get('description', instance.description)
        instance.save()
        return instance



class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = "__all__"


    def update(self, instance, validated_data):
        # return super().update(instance, validated_data)
        instance.name = validated_data.get('name', instance.name)
        instance.description = validated_data.get('description', instance.description)
        instance.save()
        return instance




class EmployeeRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeRole
        fields = "__all__"

    def update(self, instance, validated_data):
        # return super().update(instance, validated_data)
        instance.roleName = validated_data.get('roleName', instance.roleName)
        instance.description = validated_data.get('description', instance.description)
        instance.save()
        return instance



class CompanyCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyCode
        fields = "__all__"


    def update(self, instance, validated_data):
        # return super().update(instance, validated_data)
        instance.code = validated_data.get('code', instance.code)
        instance.description = validated_data.get('description', instance.description)
        instance.save()
        return instance



class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = "__all__"


    def update(self, instance, validated_data):
        # return super().update(instance, validated_data)
        instance.name = validated_data.get('name', instance.name)
        instance.save()
        return instance




class OfficeBranchSerializer(serializers.ModelSerializer):
    class Meta:
        model = OfficeBranch
        fields = "__all__"


    def update(self, instance, validated_data):
        # return super().update(instance, validated_data)
        instance.location = validated_data.get('location', instance.location)
        instance.description = validated_data.get('description', instance.description)
        instance.save()
        return instance






    ## custom token generator
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
        ## send the user data to get the token
    def get_token(cls, user):
            ## check the user is verify or not
        if user is not None and user.is_verified:
                ## generate token for the user.. it will give you refresh and access token
            token = super().get_token(user)
            token['name'] = user.name
            token['email'] = user.email
            token['organization'] = user.organization.name
            return token
        else:
            raise serializers.ValidationError('You are not verified')
   


class CustomTokenRefreshSerializer(TokenRefreshSerializer):
    def validate(self, attrs):
        ## call super() to get the access token and refresh token
        data = super().validate(attrs)
        refresh_token = RefreshToken(attrs['refresh'])
        ## take the user email from the refresh token
        email = refresh_token.payload.get('email')
        try:
            ## take the user details from the database
            user = Employee.objects.get(email = email)
            ## decode the generated jwt token
            decodeJTW = jwt.decode(str(data['access']), config('DJANGO_SECRET_KEY'), algorithms=["HS256"])
                # add payload here
            decodeJTW['name'] = str(user.name)
            decodeJTW['email'] = str(user.email)
            decodeJTW['organization'] = str(user.organization.name)
            ## encode the modified jwt token
            encoded = jwt.encode(decodeJTW, config('DJANGO_SECRET_KEY'), algorithm="HS256")
            ## replace the access token with the modified one
            data['access'] = encoded
            data['role'] = user.role.roleName
            user.last_login = timezone.now()
            user.save()
            ## return the newly generated token
            return data
        except:
            return data




        ## user registration 
class EmployeeRegistrationSerializer(serializers.ModelSerializer):
        ## password field is write only
    password2 = serializers.CharField(required=True,style = {'input_type':'password'}, write_only =True)
    class Meta:
        model =Employee
        fields = ['email','name','organization','empID','department','companyCode', 'costcenter',
                  'role','password','password2','doj', 'branch']
        extra_kwargs = {
            'password':{'write_only':True},            ## password => write_only field
        }

            ## validate both passwords are same or not
    def validate(self, data):
        password = data.get('password')
        password2 = data.get('password2')
        if password != password2:
            raise serializers.ValidationError('Password and Confirm password does not match.....')
        if len(password) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters long....")
        return data

                ## if the validation is successfull then create that 
    def create(self, validate_data):
        return Employee.objects.create_user(**validate_data)





                ## This is for login page
class EmployeeLoginSerializer(serializers.ModelSerializer):
    empID = serializers.CharField(max_length = 100)
    companyCode = serializers.CharField(max_length = 20)
    class Meta:
        model = Employee
        fields = ['companyCode','empID','password']




            ## this is for perticular user profile 
class EmployeeProfileSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format="%Y-%m-%d")

    organization = OrganizationSerializer()
    department = DepartmentSerializer()
    branch = OfficeBranchSerializer()
    companyCode = CompanyCodeSerializer()
    costcenter = CostCenterSerializer()
    role = EmployeeRoleSerializer()
    """Define the name of the related organization for serialization"""
    # organization_name = serializers.SerializerMethodField()
    # department_name = serializers.SerializerMethodField()
    # branch_name = serializers.SerializerMethodField()
    # companyCode_name = serializers.SerializerMethodField()
    # costcenter_name = serializers.SerializerMethodField()
    # role_name = serializers.SerializerMethodField()

    """
    StringRelatedField to get string representations from related models (this relies on the __str__() method).
    """
    # department_name = serializers.StringRelatedField(source='department')
    # branch_name = serializers.StringRelatedField(source='branch')
    # companyCode_name = serializers.StringRelatedField(source='companyCode')
    # costcenter_name = serializers.StringRelatedField(source='costcenter')
    # role_name = serializers.StringRelatedField(source='role')

    class Meta:
        model = Employee
        # fields = ['email','name','organization_name','empID','department_name','companyCode_name','costcenter_name',
        #           'role_name','created_at','doj','branch_name',]
        fields = ['email','name','organization','empID','department','companyCode','costcenter',
                  'role','created_at','doj','branch',]

    """
    def get_organization_name(self, obj):
        # print(obj)
        # return obj.organization.name
        data ={
            'id':obj.organization.id,
            'name':obj.organization.name
        }
        return data
    
    def get_department_name(self, obj):
        return obj.department.name
    
    def get_branch_name(self, obj):
        return obj.branch.location
    
    def get_companyCode_name(self, obj):
        return obj.companyCode.code
    
    def get_costcenter_name(self, obj):
        return obj.costcenter.name
    
    def get_role_name(self, obj):
        return obj.role.roleName
    """




            ## this is for password change
class EmployeeChangePassword(serializers.Serializer):
    password = serializers.CharField(max_length= 255, style= {'input_type':'password'}, write_only =True)
    password2 = serializers.CharField(max_length= 255, style= {'input_type':'password'}, write_only =True)
    class Meta:
        fields = ['password','password2']

        ## validate both passwords are same or not
    def validate(self, data):
        password = data.get('password')
        password2 = data.get('password2')
            ## take the user data from context send from views class
        user = self.context.get('user')
        if password != password2:
            raise serializers.ValidationError('Password and Confirm password does not match')
        if len(password) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters long....")
            ## set the new password in user account
        user.set_password(password)
        # print(user.check_password())
        user.save()
        return data




            ## this is for forgot password
class SendPasswordResetEmailSerializer(serializers.Serializer):
        ## for forgot password .. user email is required
    empID = serializers.CharField(max_length =255)
    class Meta:
        fileds = ['empID']

        ## validate the email ... check any user present with this email or not
    def validate(self, data):
        empID = data.get('empID')
        if Employee.objects.filter(empID= empID, is_verified= True).exists():
            user = Employee.objects.get(empID= empID)
                ## call the custom forgot password function and sent the otp to the user account
            reset_pass_otp_email(user.email)
            return "Successful"
        else:
            raise serializers.ValidationError('You are not a Registered user or you have not verified your account...')



            ## this is for reset password
class EmployeePasswordResetSerializer(serializers.Serializer):
        ## for reset password these fields are required
    empID = serializers.CharField(max_length= 100)
    password = serializers.CharField(max_length= 255, style= {'input_type':'password'}, write_only=True)
    password2 = serializers.CharField(max_length= 255, style= {'input_type':'password'}, write_only=True)
    otp = serializers.CharField()
    class Meta:
        fields = ['empID','password','password2','otp']

        ## validate the user details 
    def validate(self, data):
        try:
            empID = data.get('empID')
            password = data.get('password')
            password2 = data.get('password2')
            otp = data.get('otp')
            user = Employee.objects.get(empID=empID, is_verified=False)
            if password != password2:
                raise serializers.ValidationError('Password and Confirm password does not match')
            if len(password) < 8:
                raise serializers.ValidationError("Password must be at least 8 characters long....")
            if user.otp != otp:
                raise serializers.ValidationError('Wrong OTP')
            if user.otp == otp:
                ## if everything is verified make the user verified
                user.is_verified = True
                ## save the new password in user account
                user.set_password(password)
                user.save()
                return data
        except Employee.DoesNotExist:
            raise serializers.ValidationError('No user is present with this email.. Or your account is verified')
        except Exception as e:
            raise serializers.ValidationError(str(e))




        ## manager can create user account
class EmployeeRegistrationByAdminSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(required=True,style = {'input_type':'password'}, write_only =True)
    class Meta:
        model =Employee
        fields = ['email','name','organization','empID','department','companyCode', 'costcenter',
                  'role','password','password2','doj', 'branch']
        extra_kwargs = {
            'password':{'write_only':True},            ## password => write_only field
        }

            ## validate both passwords are same or not
    def validate(self, data):
        password = data.get('password')
        password2 = data.get('password2')
        if password != password2:
            raise serializers.ValidationError('Password and Confirm password does not match.....')
        if len(password) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters long....")
        # if 'is_manager'in data:
        #     data['is_manager'] = False
        return data

                ## if the validation is successfull then create that 
    def create(self, validate_data):
        return Employee.objects.create_user(**validate_data)




class AdminUpdateEmployeeProfileSerializer(serializers.ModelSerializer):
    empID = serializers.CharField(max_length=20)
    email = serializers.EmailField(max_length=255, required=False)
    message = serializers.CharField(max_length= 200, required=False)
    class Meta:
        model =Employee
        fields = ['email','name','organization','empID','department','companyCode', 'costcenter',
                  'role','doj', 'branch', 'dol', 'message']


            ## validate both passwords are same or not
    def validate(self, data):
        user = self.context.get('request').user
        employee_data = self.context.get('employee_data')

        if 'department' in data:
            dept = data.get('department')
            if dept != employee_data.department:
                dept_manager = dept.employee_department.filter(role__id=2).first()
                if dept_manager:
                    if 'message' not in data:
                        email_message = None
                    else:
                        email_message = data.get('message')
                    # department_change_email(receiver= dept_manager.email, changed_by=user.email, change_employee= employee_data.email,
                    #                         from_department=employee_data.department.name, to_department= dept.name,
                    #                         comments=email_message)
                    asyncio.run(main_email(receiver= dept_manager.email, changed_by=user.email, change_employee= employee_data.email,
                                            from_department=employee_data.department.name, to_department= dept.name,
                                            comments=email_message))
                    message = f"{user.email} moved {employee_data.email} from the {employee_data.department.name} department to {dept.name} department.."
                    DepartmentTracker.objects.create(department=dept, message=message, status="NotSeen")
                else:
                    message = f"{user.email} moved {employee_data.email} from the {employee_data.department.name} department to {dept.name} department.."
                    DepartmentTracker.objects.create(department=dept, message=message, status="NotSeen")
        return data


    def update(self, instance, validated_data):
        old_department = instance.department
        # return super().update(instance, validated_data)
        instance.email = validated_data.get('email', instance.email)
        instance.name = validated_data.get('name', instance.name)
        instance.organization = validated_data.get('organization', instance.organization)
        instance.empID = validated_data.get('empID', instance.empID)
        instance.department = validated_data.get('department', instance.department)
        instance.companyCode = validated_data.get('companyCode', instance.companyCode)
        instance.costcenter = validated_data.get('costcenter', instance.costcenter)
        instance.role = validated_data.get('role', instance.role)
        instance.doj = validated_data.get('doj', instance.doj)
        instance.dol = validated_data.get('dol', instance.dol)
        instance.branch = validated_data.get('branch', instance.branch)
        instance.save()

        # new_department = instance.department
        # if old_department != new_department:
        #     user = self.context.get('request').user
        #     comments = validated_data.get('message', "No message...")
        #     # Create DepartmentTracker
        #     message = f"{user.email} moved {instance.email} from {old_department.name} to {new_department.name}"
        #     DepartmentTracker.objects.create(department=new_department, message=message, status="NotSeen")

        return instance