from django.contrib.auth import authenticate
from django.db.models import Q
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from avtarizatsiya.models import UserModel, VIA_EMAIL, VIA_PHONE, DONE, PHOTO
from helper.devices_check import check_email_or_phone_number, send_code_email, send_code_phone


class RegisterSerializer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        super(RegisterSerializer, self).__init__(*args, **kwargs)
        self.fields['email_phone_number'] = serializers.CharField(max_length=128, required=False)

    uuid = serializers.IntegerField(read_only=True)
    auth_type = serializers.CharField(read_only=True, required=False)
    auth_status = serializers.CharField(read_only=True, required=False)

    class Meta:
        model = UserModel
        fields = ['uuid', 'auth_type', 'auth_status']

    def validate(self, data):
        data = self.auth_validate(data=data)
        return data

    def create(self, validated_data):
        user = super(RegisterSerializer, self).create(validated_data)
        code = user.create_verify_code(user.auth_type)

        if user.auth_type == VIA_EMAIL:
            send_code_email(user.email, code)
        else:
            send_code_phone(phone_number=user.phone_number, code=code)
        user.save()
        return user


    @staticmethod
    def auth_validate(data):
        user_input = str(data['email_phone_number']).lower()
        if user_input.endswith('@gmail.com'):
            data = {
                'email': user_input,
                'auth_type': VIA_EMAIL
            }
        elif user_input.startswith("+"):
            data = {
                'phone_number': user_input,
                'auth_type': VIA_PHONE
            }
        else:
            data = {
                'success': False,
                'message': "Please enter a valid phone number or email"
            }
            raise serializers.ValidationError(data)
        return data

    def to_representation(self, instance):
        data = super(RegisterSerializer, self).to_representation(instance)
        data['access_token'] = instance.token()['access_token']
        return data


class UpdateUserSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(write_only=True, required=False)
    last_name = serializers.CharField(write_only=True, required=False)
    username = serializers.CharField(write_only=True, required=False)
    password = serializers.CharField(write_only=True, required=False)
    confirm_password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = UserModel
        fields = ['first_name', 'last_name', 'username', 'password', 'confirm_password']

    def validate(self, attrs):
        password = attrs.get('password')
        confirm_password = attrs.get('confirm_password')

        if password != confirm_password:
            response = {
                'status': False,
                'message': 'check that the passwords are the same'
            }

            raise serializers.ValidationError(response)

        return attrs

    def validate_username(self, username):
        if UserModel.objects.filter(username=username).exists():
            response = {
                'status': False,
                'message': 'Such a username exists'
            }

            raise serializers.ValidationError(response)
        return username

    def update(self, instance, validated_data):
        instance.username = validated_data.get('username', instance.username)
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.password = validated_data.get('password', instance.password)

        if validated_data.get('password'):
            instance.set_password(validated_data.get('password'))
            instance.auth_status = DONE
            instance.save()

        return instance


class UserLoginSerializer(TokenObtainPairSerializer):
    def __init__(self, *args, **kwargs):
        super(UserLoginSerializer, self).__init__(*args, **kwargs)
        self.fields['username'] = serializers.CharField(max_length=100, required=False)
        self.fields['userinput'] = serializers.CharField(max_length=100, required=False)

    def validate(self, attrs):
        response = {
            'status': False
        }
        userinput = attrs.get('userinput')
        if userinput.endswith('+'):
            user = UserModel.objects.filter(phone_number=userinput).first()
        elif userinput.startswith('@gmail.com'):
            user = UserModel.objects.filter(email=userinput).first()
        else:
            user = UserModel.objects.filter(username=userinput).first()

        if user is None:
            response['message'] = 'Invalid username or phone number or email address'
            raise serializers.ValidationError(response)

        auth_user = authenticate(username=user.username, password=attrs.get('password'))
        if auth_user is None:
            response['message'] = 'Invalid username or password'
            raise serializers.ValidationError(response)

        response = {
            'status': True,
            'access_token': auth_user.token()['access_token'],
            'refresh_token': auth_user.token()['refresh_token']
        }

        return response


class LogoutSerializer(serializers.Serializer):
    refresh_token = serializers.CharField()


class UserForgetPasswordSerializer(serializers.Serializer):
    email_phone_number = serializers.CharField(write_only=True, required=True)

    def validate(self, attrs):
        email_phone_number = attrs.get('email_phone_number')
        response ={'status': False}
        if not email_phone_number:
            response['message'] = 'Email phone number is requirmed'
            raise serializers.ValidationError(response)

        user = UserModel.objects.filter(Q(email=email_phone_number) | Q(phone_number=email_phone_number)).first()
        if not user.exists():
            response['message'] = 'User already exists'
            raise serializers.ValidationError(response)

        attrs['user'] = user.first()
        return attrs