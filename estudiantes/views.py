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

            # Crea Estudiante
            estudiante = Estudiante.objects.create(
                nombres=nombres,
                apellidos=apellidos,
                grado=grado,
                colegio=colegio,
                edad=int(edad),
                apoderado=None
            )

            # Crea Inscripción (los cupos sólo se validan cuando se verifique si así lo decides)
            inscripcion = Inscripcion.objects.create(
                estudiante=estudiante,
                plan=plan,
                estado='pendiente',
                estado_pago='pendiente',
                verificada=False
            )

            # Crea Matrícula (ajusta si tu modelo exige más campos)
            Matricula.objects.create(
                inscripcion=inscripcion,
                estudiante=estudiante
            )

            # Redirige al registro de apoderado
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

    # GET: sólo renderiza el form; el JS cargará los planes según el grado elegido
    return render(
        request,
        'estudiantes/registrar.html',
        {'grados': Estudiante.GRADOS, 'grado': request.GET.get('grado', '')}
    )
