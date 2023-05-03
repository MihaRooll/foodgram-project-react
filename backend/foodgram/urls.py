from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    # Маршрут для административной панели Django
    path('admin/', admin.site.urls),
    # Маршрут для API приложения
    path('api/', include('api.urls')),
]
