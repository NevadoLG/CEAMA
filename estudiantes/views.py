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
        grados = Estudiante.GRADOS
        return render(request, 'estudiantes/registrar.html', {
            'apoderados': apoderados,
            'planes': planes,
            'grados': grados
        })

    elif request.method == 'POST':
        try:
            nombres = request.POST.get('nombres')
            apellidos = request.POST.get('apellidos')
            grado = request.POST.get('grado')
            colegio = request.POST.get('colegio')
            edad = request.POST.get('edad')
            plan_id = request.POST.get('plan')
            plan = Plan.objects.get(id=plan_id)

            # Por ahora, creamos el estudiante sin apoderado (se asociará después)
            estudiante = Estudiante.objects.create(
                nombres=nombres,
                apellidos=apellidos,
                grado=grado,
                colegio=colegio,
                edad=edad,
                apoderado=None
            )

            inscripcion = Inscripcion.objects.create(
                estudiante=estudiante,
                plan=plan,
                estado_pago='pendiente'
            )

            Matricula.objects.create(
                inscripcion=inscripcion,
                estudiante=estudiante
            )

            # Redirigir a la vista de registro de apoderado tras registrar estudiante
            from django.shortcuts import redirect
            return redirect('registrar_apoderado')
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
