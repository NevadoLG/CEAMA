from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import JsonResponse
from django.db.models import Count

from apoderados.models import Apoderado
from django.utils import timezone
from planes.models import Plan
from docentes.models import Asignacion
from .models import Estudiante, Inscripcion, Matricula


def registrar_estudiante(request):
    if request.method == 'GET':
        apoderados = Apoderado.objects.all()
        planes = Plan.objects.all()
        asignaciones = []
        grados = Estudiante.GRADOS
        return render(request, 'estudiantes/registrar.html', {
            'apoderados': apoderados,
            'planes': planes,
            'grados': grados,
            'asignaciones': asignaciones,
        })

    if request.method == 'POST':
        grado = (request.POST.get('grado') or '').strip()
        nombres = (request.POST.get('nombres') or '').strip()
        apellidos = (request.POST.get('apellidos') or '').strip()
        colegio = (request.POST.get('colegio') or '').strip()
        edad = request.POST.get('edad')
        plan_id = request.POST.get('plan')
        asignacion_id = request.POST.get('asignacion')

        form_error = None
        if not grado:
            form_error = 'Selecciona un grado.'
        elif not nombres or not apellidos or not colegio or not edad:
            form_error = 'Completa todos los campos.'
        elif len(nombres) > 30 or len(apellidos) > 30 or len(colegio) > 30:
            form_error = 'Nombres, apellidos y colegio deben tener como máximo 30 caracteres.'
        else:
            try:
                if len(str(edad)) > 2:
                    form_error = 'La edad no puede tener más de 2 dígitos.'
                else:
                    edad_int = int(edad)
                    if edad_int < 5 or edad_int > 20:
                        form_error = 'La edad debe estar entre 5 y 20.'
            except Exception:
                form_error = 'La edad debe ser un número válido.'

        if form_error:
            apoderados = Apoderado.objects.all()
            planes = Plan.objects.all()
            if grado:
                asignaciones = (
                    Asignacion.objects
                    .filter(grado=grado)
                        .select_related('plan', 'aula', 'horario')
                        .prefetch_related('profesores')
                        .annotate(num_matriculas=Count('matriculas'))
                )
            else:
                asignaciones = []
            return render(request, 'estudiantes/registrar.html', {
                'apoderados': apoderados,
                'planes': planes,
                'grados': Estudiante.GRADOS,
                'asignaciones': asignaciones,
                'form_error': form_error,
                'nombres': nombres,
                'apellidos': apellidos,
                'colegio': colegio,
                'edad': edad,
                'grado': grado,
            })

        ins_data = {
            'grado': grado,
            'nombres': nombres,
            'apellidos': apellidos,
            'colegio': colegio,
            'edad': int(edad),
            'plan_id': int(plan_id) if plan_id else None,
            'asignacion_id': int(asignacion_id) if asignacion_id else None,
            'created_at': timezone.now().timestamp(),
        }
        request.session['ceama_inscripcion'] = ins_data
        request.session.modified = True

        return redirect(reverse('registrar_apoderado'))


def listado_matriculas(request):
    """Listado simple de matrículas con sus asignaciones."""
    matriculas = (
        Matricula.objects
        .select_related('estudiante', 'inscripcion')
        .prefetch_related('asignaciones')
        .order_by('-fecha_creada')
    )

    contexto = {
        'matriculas': matriculas,
    }
    return render(request, 'estudiantes/listado_matriculas.html', contexto)



