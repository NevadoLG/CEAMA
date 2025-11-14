# estudiantes/views.py
from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import JsonResponse
from planes.models import Plan
from .models import Estudiante, Inscripcion, Matricula

def registrar_estudiante(request):
    if request.method == 'POST':
        # Datos del formulario
        grado     = (request.POST.get('grado') or '').strip()
        nombres   = (request.POST.get('nombres') or '').strip()
        apellidos = (request.POST.get('apellidos') or '').strip()
        colegio   = (request.POST.get('colegio') or '').strip()
        edad      = request.POST.get('edad')
        plan_id   = request.POST.get('plan')  # lo rellena el JS

        # Validación simple
        if not (grado and nombres and apellidos and colegio and edad and plan_id):
            ctx = {
                'grados': Estudiante.GRADOS,
                'grado': grado,
                'form_error': 'Completa todos los campos y selecciona un plan.',
            }
            return render(request, 'estudiantes/registrar.html', ctx)

        try:
            plan = Plan.objects.get(pk=plan_id, activo=True)

            estudiante = Estudiante.objects.create(
                nombres=nombres,
                apellidos=apellidos,
                grado=grado,
                colegio=colegio,
                edad=int(edad),
                apoderado=None
            )

            inscripcion = Inscripcion.objects.create(
                estudiante=estudiante,
                plan=plan,
                estado='pendiente',
                estado_pago='pendiente',
                verificada=False
            )

            return redirect(f"{reverse('registrar_apoderado')}?inscripcion_id={inscripcion.id}")

        except Plan.DoesNotExist:
            ctx = {
                'grados': Estudiante.GRADOS,
                'grado': grado,
                'form_error': 'El plan seleccionado no existe o no está activo.',
            }
            return render(request, 'estudiantes/registrar.html', ctx)
        except Exception as e:
            ctx = {
                'grados': Estudiante.GRADOS,
                'grado': grado,
                'form_error': f'Error al registrar: {e}',
            }
            return render(request, 'estudiantes/registrar.html', ctx)

    return render(
        request,
        'estudiantes/registrar.html',
        {'grados': Estudiante.GRADOS, 'grado': request.GET.get('grado', '')}
    )
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


