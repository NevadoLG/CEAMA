from django.urls import path
from . import views

app_name = 'estudiantes'

urlpatterns = [
    path('registrar/', views.registrar_estudiante, name='registrar_estudiante'),
    path('matriculas/', views.listado_matriculas, name='listado_matriculas'),
]
