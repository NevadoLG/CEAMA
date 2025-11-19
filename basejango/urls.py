from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('estudiantes/', include('estudiantes.urls')),
    path('apoderados/', include('apoderados.urls')),
    path('docentes/', include('docentes.urls')),
    path('pagos/', include('pagos.urls')),
    path('planes/', include('planes.urls')),
    path('', include('landing.urls', namespace='landing_index')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
