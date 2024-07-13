import random
import uuid
from datetime import timedelta

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from rest_framework_simplejwt.tokens import RefreshToken

from helper.models import BaseModel

VIA_EMAIL, VIA_PHONE = 'VIA_EMAIL', 'VIA_PHONE',
ORDINARY_USER, MANAGER, ADMIN = 'ORDINARY_USER', 'ADMIN', 'MANAGER',
NEW, CODE_VERIFIED, DONE, PHOTO = 'NEW', 'DONE', 'PHOTO', 'CODE_VERIFIED',


class UserModel(AbstractUser, BaseModel):
    AUTH_TYPES = (
        (VIA_EMAIL, VIA_EMAIL),
        (VIA_PHONE, VIA_PHONE)
    )

    AUTH_STATUS = (
        (NEW, NEW),
        (CODE_VERIFIED, CODE_VERIFIED),
        (DONE, DONE),
        (PHOTO, PHOTO)
    )

    USER_ROLES = (
        (ADMIN, ADMIN),
        (MANAGER, MANAGER)
    )


    auth_status = models.CharField(max_length=100, choices=AUTH_STATUS, default=NEW),
    auth_type = models.CharField(max_length=100, choices=AUTH_TYPES, default=VIA_EMAIL)
    user_role = models.CharField(max_length=100, choices=USER_ROLES, default=ORDINARY_USER)

    email = models.EmailField(null=True, blank=True)
    phone_number = models.CharField(max_length=13, null=True, blank=True)
    email_phone_number = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.full_name

    @property
    def full_name(self):
        return (f'{self.first_name}'
                f'{self.last_name}')

    def check_username(self):
        if not self.username:
            username_user = f"Shopping -> {uuid.uuid4()}"
            if UserModel.objects.filter(username=username_user).exists():
                self.check_username()
            self.username = username_user

    def check_pass(self):
        if not self.password:
            self.password = f"Password -> {uuid.uuid4()}"

    def check_email(self):
        self.email = str(self.email).lower()

    def hashing_pass(self):
        if not self.password.startswith('pbkdf2_sha256'):
            self.set_password(self.password)

    def clean(self):
        self.check_username()
        self.check_pass()
        self.check_email()
        self.hashing_pass()

    def save(self, *args, **kwargs):
        if not self.pk:
            self.clean()
        super(UserModel, self).save(*args, **kwargs)

    def create_verify_code(self, verify_type):
        code = random.randint(1, 1000)
        ConfirmationModel.objects.create(code=code, user=self, verify_type=verify_type)
        return code

    def token(self):
        refresh = RefreshToken.for_user(self)
        response = {
            'access_token': str(refresh.access_token),
            'refresh_token': str(refresh)
        }
        return response


EMAIL_EXPIRATION_TIME = 4
PHONE_EXPIRATION_TIME = 2


class ConfirmationModel(BaseModel):
    VERIFY_TYPES = (
        (VIA_EMAIL, VIA_EMAIL),
        (VIA_PHONE, VIA_PHONE)
    )

    verify_type = models.CharField(max_length=128, choices=VERIFY_TYPES, default=VIA_EMAIL)
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE, related_name='verification_codes')
    expiration_time = models.DateField()
    is_confirmed = models.BooleanField(default=False)
    code = models.CharField(max_length=4, default=0000)

    def save(self, *args, **kwargs):
        if not self.pk:
            if self.verify_type == VIA_EMAIL:
                self.expiration_time = timezone.now() + timedelta(minutes=EMAIL_EXPIRATION_TIME)
            else:
                self.expiration_time = timezone.now() + timedelta(minutes=PHONE_EXPIRATION_TIME)
        super(ConfirmationModel, self).save(*args, **kwargs)
