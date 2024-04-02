from rest_framework import serializers
from account.models import Employee, CostCenter
from account.utils import reset_pass_otp_email
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer 
from rest_framework_simplejwt.tokens import RefreshToken 
import jwt
from decouple import config
from django.utils import timezone





class CostCenterSerializer(serializers.ModelSerializer):
    class Meta:
        model = CostCenter
        fields = "__all__"

    def validate(self, attrs):
        user = self.context['request'].user
        attrs['organization'] = user.organization
        return attrs



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
            token['organization'] = user.organization
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
            decodeJTW['organization'] = str(user.organization)
            ## encode the modified jwt token
            encoded = jwt.encode(decodeJTW, config('DJANGO_SECRET_KEY'), algorithm="HS256")
            ## replace the access token with the modified one
            data['access'] = encoded
            data['is_manager']= user.is_manager
            data['is_employee']= user.is_employee
            data['is_admin']= user.is_admin
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
        fields = ['email','name','organization','empID','department','companyCode', 'cost_center',
                  'is_employee', 'is_manager','password','password2',]
        extra_kwargs = {
            'password':{'write_only':True},            ## password => write_only field
        }

            ## validate both passwords are same or not
    def validate(self, data):
        password = data.get('password')
        password2 = data.get('password2')
        annotationType = data.get('annotationType')
        if password != password2:
            raise serializers.ValidationError('Password and Confirm password does not match.....')
        if len(password) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters long....")
        if 'is_manager'in data:
            data['is_manager'] = False
        return data

                ## if the validation is successfull then create that 
    def create(self, validate_data):
        return Employee.objects.create_user(**validate_data)





                ## This is for login page
class EmployeeLoginSerializer(serializers.ModelSerializer):
    empID = serializers.CharField(max_length = 100)
    class Meta:
        model = Employee
        fields = ['companyCode','empID','password']




            ## this is for perticular user profile 
class EmployeeProfileSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format="%d/%m/%Y ")
    class Meta:
        model = Employee
        fields = ['email','name','organization','empID','department','companyCode', 'cost_center',
                  'is_employee', 'is_manager','created_at']
    
    # def to_representation(self, instance):
    #     user = self.context.get('user')
    #     data = super().to_representation(instance)
    #     if not user.is_manager:
    #         data.pop("checked_at")
    #     return data


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
        fields = ['email','name','organization','empID','department','companyCode', 'cost_center',
                  'is_employee', 'is_manager','password','password2']
        extra_kwargs = {
            'password':{'write_only':True},            ## password => write_only field
        }

            ## validate both passwords are same or not
    def validate(self, data):
        password = data.get('password')
        password2 = data.get('password2')
        annotationType = data.get('annotationType')
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


