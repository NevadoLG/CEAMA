from django.urls import path
from .views import asignacion_detail, asignaciones_by_grado

urlpatterns = [
    path('asignacion/<int:pk>/json/', asignacion_detail, name='asignacion_detail_json'),
    path('asignaciones/json/', asignaciones_by_grado, name='asignaciones_by_grado_json'),
]
