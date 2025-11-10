from django.urls import path
from . import views

urlpatterns = [
    path("regularizar/", views.regularizar_lookup, name="pagos_regularizar_lookup"),
    path("seguimiento/<str:code>/", views.regularizar_seguimiento, name="pagos_regularizar_seguimiento"),
    path("reenviar-codigo/", views.reenviar_codigo, name="pagos_reenviar_codigo"),
    path("registrar/", views.registrar_pago, name="registrar_pago"),
]
