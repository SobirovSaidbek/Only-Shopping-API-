from django.contrib.auth.models import AbstractUser
from django.db import models

VIA_EMAIL, VIA_PHONE = 'VIA_EMAIL', 'VIA_PHONE',
ORDINARY_USER, ORDINARY_PHONE = 'ORDINARY_USER', 'ORDINARY_PHONE',
NEW, CODE_VERIFIED, DONE, PHOTO = 'NEW', 'DONE', 'PHOTO', 'CODE_VERIFIED',

class UserModel(AbstractUser, BaseModel):