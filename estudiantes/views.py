# estudiantes/views.py
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from apoderados.models import Apoderado
from planes.models import Plan
from .models import Estudiante, Inscripcion, Matricula
from usuarios.models import Usuario
import json

@csrf_exempt
def registrar_estudiante(request):
    if request.method == 'GET':
        apoderados = Apoderado.objects.all()
        planes = Plan.objects.all()
        usuarios = Usuario.objects.all()
        return render(request, 'estudiantes/registrar.html', {
            'apoderados': apoderados,
            'planes': planes,
            'usuarios': usuarios
        })

    elif request.method == 'POST':
        try:
            nombres = request.POST.get('nombres')
            apellidos = request.POST.get('apellidos')
            grado = request.POST.get('grado')
            colegio = request.POST.get('colegio')
            edad = request.POST.get('edad')
            apoderado_id = request.POST.get('apoderado')
            plan_id = request.POST.get('plan')
            usuario_id = request.POST.get('usuario')

            apoderado = Apoderado.objects.get(id=apoderado_id)
            plan = Plan.objects.get(id=plan_id)
            usuario = Usuario.objects.get(id=usuario_id)

            estudiante = Estudiante.objects.create(
                nombres=nombres,
                apellidos=apellidos,
                grado=grado,
                colegio=colegio,
                edad=edad,
                apoderado=apoderado
            )

            inscripcion = Inscripcion.objects.create(
                estudiante=estudiante,
                plan=plan,
                usuario_registra=usuario,
                estado_pago='pendiente'
            )

            Matricula.objects.create(
                inscripcion=inscripcion,
                estudiante=estudiante
            )

            return JsonResponse({'status': 'ok', 'message': 'Inscripción registrada correctamente.'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
