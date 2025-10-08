from django.urls import path
from . import views

urlpatterns = [
    path('registrar/', views.registrar_estudiante, name='registrar_estudiante'),
]
