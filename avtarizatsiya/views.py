from django.shortcuts import render
from django.utils import timezone
from rest_framework.generics import CreateAPIView, UpdateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from avtarizatsiya.models import ConfirmationModel, CODE_VERIFIED, VIA_EMAIL, VIA_PHONE
from avtarizatsiya.serializers import *
from helper.devices_check import send_code_email, send_code_phone


class UserRegisterModel(CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer
    model = UserModel


class UserLoginViewAPI(TokenObtainPairView):
    serializer_class = UserLoginSerializer


class UserLogoutView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = LogoutSerializer

    def post(self, request, *args, **kwargs):
        refresh = self.request.data['refresh']

        token = RefreshToken(token=refresh)
        token.blacklist()
        response = {
            'success': True,
            'message': 'Logout successful User'
        }
        return Response(response, status=status.HTTP_200_OK)


class UserRefreshTokenView(TokenRefreshView):
    serializer_class = TokenRefreshSerializer


class UserForgotPasswordView(APIView):
    permission_classes = [AllowAny]
    serializer_class = UserForgetPasswordSerializer

    def post(self, request, *args, **kwargs):
        serializer = UserForgetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            email_phone_number = serializer.validated_data['email_phone_number']
            user = serializer.validated_data['user']
            if email_phone_number.endswith('@gmail.com'):
                new_code = user.create_verification_code(VIA_EMAIL)
                send_code_email(user.email, new_code)

            else:
                new_code = user.create_verification_code(VIA_PHONE)
                send_code_phone(user.phone_number, new_code)

            response = {
                'success': True,
                'message': 'User code sent successfully',
                'access_token': user.token()['access_token']
            }

            return Response(response, status=status.HTTP_200_OK)

        else:
            response = {
                'success': False,
                'message': 'There is an input error'
            }

            return Response(response, status=status.HTTP_400_BAD_REQUEST)


class UserVerifyCodeViewAPI(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = self.request.user
        code = request.data.get('code')

        verification_code = ConfirmationModel.objects.filter(
            code=code, is_confirmed=False, user_id=user.id,
            expiration_time_gte=timezone.now()
        )
        if not verification_code.exists():
            response = {
                'success': False,
                'message': 'Your verification code is None.'
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        ConfirmationModel.objects.update(is_confirmed=True)
        user.auth_status = CODE_VERIFIED
        user.save()

        response = {
            'success': True,
            'message': 'You are successfully logged in.',
            'auth_status': user.auth_status
        }

        return Response(response, status=status.HTTP_200_OK)


class UserResendVerificationCodeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = self.request.user
        verification_code = ConfirmationModel.objects.filter(
            is_confirmed=False, user_id=user.id,
            expiration_time_gte=timezone.now()
        )
        if verification_code.exists():
            response = {
                'success': False,
                'message': 'You Have already verified'
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        self.send_code()

        response = {
            'success': True,
            'message': 'New Code is sent'
        }

        return Response(response, status=status.HTTP_200_OK)

    def send_code(self):
        user = self.request.user
        new_code = user.create_verification_code(verify_type=user.auth_type)
        if user.auth_type == VIA_EMAIL:
            send_code_email(user.email, new_code)

        else:
            send_code_phone(user.phone_number, new_code)


class UserUpdateAPIView(UpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UpdateUserSerializer

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        super(UserUpdateAPIView, self).update(request, *args, **kwargs)
        response = {
            'success': True,
            'message': 'You User Updated Successfully',
            'auth_status': self.request.user.auth_status
        }
        return Response(response, status=status.HTTP_202_ACCEPTED)