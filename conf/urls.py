from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/users/', include('avtarizatsiya.urls', namespace='avtarizatsiya')),
    #path('api/v1/admin/', include('admin_pages.urls', namespace='admin_pages')),
    #path('api/v1/shopping/', include('shopping.urls', namespace='shopping'))
]
