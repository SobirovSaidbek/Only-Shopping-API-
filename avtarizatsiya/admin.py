from django.contrib import admin

from avtarizatsiya.models import UserModel, ConfirmationModel


@admin.register(UserModel)
class UserModelAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'username', 'email', 'phone_number', 'created_at', 'updated_at')
    search_fields = ('first_name', 'last_name', 'username', 'email',)
    list_filter = ('created_at', 'username')


@admin.register(ConfirmationModel)
class ConfirmationAdmin(admin.ModelAdmin):
    list_display = ('code', 'created_at', 'updated_at')
    search_fields = ('user__username', 'code', 'created_at', 'updated_at')
    list_filter = ('created_at',)