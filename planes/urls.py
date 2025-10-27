from django.urls import path
from .views import planes_por_nivel

urlpatterns = [
    path('opciones/', planes_por_nivel, name='planes_opciones'),
]
