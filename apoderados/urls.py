from django.urls import path
from .views import registrar_apoderado

urlpatterns = [
	path('registrar/', registrar_apoderado, name='registrar_apoderado'),
]
