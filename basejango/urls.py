from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('estudiantes/', include('estudiantes.urls')),
    path('apoderados/', include('apoderados.urls')),
    path('pagos/', include('pagos.urls')),
    path('planes/', include('planes.urls')),
    path('', include('landing.urls')),
]
