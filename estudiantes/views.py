# estudiantes/views.py
# estudiantes/views.py
from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import JsonResponse
from django.db.models import Count

from apoderados.models import Apoderado
from planes.models import Plan
from docentes.models import Asignacion
from .models import Estudiante, Inscripcion, Matricula


def registrar_estudiante(request):
    if request.method == 'GET':
        apoderados = Apoderado.objects.all()
        planes = Plan.objects.all()
        asignaciones = (
            Asignacion.objects
            .select_related('curso', 'profesor', 'aula', 'horario')
            .annotate(num_matriculas=Count('matriculas'))
            .all()
        )
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

        # Validación básica (plan puede deducirse desde asignacion)
        if not (grado and nombres and apellidos and colegio and edad):
            return render(request, 'estudiantes/registrar.html', {
                'grados': Estudiante.GRADOS,
                'form_error': 'Completa todos los campos.'
            })

        try:
            plan = None
            if plan_id:
                plan = Plan.objects.filter(pk=plan_id).first()
            if not plan and asignacion_id:
                try:
                    asig_tmp = Asignacion.objects.select_related('curso').get(pk=asignacion_id)
                    curso = asig_tmp.curso
                    # buscar plan que coincida con nivel y area
                    plan = Plan.objects.filter(nivel=curso.nivel, area=curso.plan).first()
                    if not plan:
                        plan = Plan.objects.filter(nivel=curso.nivel).first()
                except Asignacion.DoesNotExist:
                    plan = None
            # si aún no hay plan, usar el plan por defecto
            if not plan:
                plan = Plan.objects.first()

            estudiante = Estudiante.objects.create(
                nombres=nombres,
                apellidos=apellidos,
                grado=grado,
                colegio=colegio,
                edad=int(edad),
                apoderado=None,
            )

            inscripcion = Inscripcion.objects.create(
                estudiante=estudiante,
                plan=plan,
            )

            matricula = Matricula.objects.create(
                inscripcion=inscripcion,
                estudiante=estudiante,
            )

            # store the selected asignacion on the inscripcion as provisional
            if asignacion_id:
                try:
                    asignacion = Asignacion.objects.get(pk=asignacion_id)
                    inscripcion.asignacion = asignacion
                    inscripcion.save(update_fields=['asignacion'])
                except Asignacion.DoesNotExist:
                    pass

            return redirect(f"{reverse('registrar_apoderado')}?inscripcion_id={inscripcion.id}")

        except Exception as e:
            return render(request, 'estudiantes/registrar.html', {
                'grados': Estudiante.GRADOS,
                'form_error': f'Error al registrar: {e}'
            })


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



