from django.urls import path
from .views import *

app_name = 'avtarizatsiya'

urlpatterns = [
    # URl Register User
    path('register/', UserRegisterModel.as_view(), name='register'),
    path('verify/', UserVerifyCodeViewAPI.as_view(), name='verify'),
    path('verify/resend/', UserResendVerificationCodeView.as_view(), name='verify-resend'),
    path('login/', UserLoginViewAPI.as_view(), name='login'),
    path('update/', UserUpdateAPIView.as_view(), name='update'),
    path('forget/password/', UserForgotPasswordView.as_view(), name='forgot-password'),
    path('refresh/token/', UserRefreshTokenView.as_view(), name='refresh-token'),
    path('logout/', UserLogoutView.as_view(), name='logout')
]