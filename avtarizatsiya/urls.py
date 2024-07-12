from django.urls import path
from .views import *

app_name = 'avtarizatsiya'

urlpatterns = [
    path('register/', UserRegisterModel.as_view(), name='register')
]