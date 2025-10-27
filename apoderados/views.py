from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from .models import Apoderado
from estudiantes.models import Estudiante, Inscripcion

def registrar_apoderado(request):
    if request.method == 'POST':
        # 1) Traer inscripcion_id explícito (preferido)
        inscripcion_id = request.POST.get('inscripcion_id') or request.GET.get('inscripcion_id')
        inscripcion = None
        if inscripcion_id:
            inscripcion = Inscripcion.objects.filter(id=inscripcion_id).select_related('estudiante').first()

        dni = request.POST.get('dni')
        nombres = request.POST.get('nombres')
        apellidos = request.POST.get('apellidos')
        telefono = request.POST.get('telefono')
        correo = request.POST.get('correo')
        direccion = request.POST.get('direccion')

        # Validaciones
        if Apoderado.objects.filter(dni=dni).exists():
            messages.error(request, "Ya existe un apoderado con ese DNI.")
        elif Apoderado.objects.filter(telefono=telefono).exists():
            messages.error(request, "Ya existe un apoderado con ese número de teléfono.")
        else:
            apoderado = Apoderado.objects.create(
                dni=dni, nombres=nombres, apellidos=apellidos,
                telefono=telefono, correo=correo, direccion=direccion
            )

            if not inscripcion:
                est_id = request.session.get('estudiante_id')
                estudiante = get_object_or_404(Estudiante, id=est_id) if est_id else None
                inscripcion = (Inscripcion.objects
                               .filter(estudiante=estudiante)
                               .order_by('-id').first()) if estudiante else None
            else:
                estudiante = inscripcion.estudiante

            if estudiante and inscripcion:
                estudiante.apoderado = apoderado
                estudiante.save(update_fields=['apoderado'])

                messages.success(request, "Apoderado registrado y asociado. Continúa con el pago.")
                return redirect(reverse('registrar_pago') + f'?inscripcion_id={inscripcion.id}')
            else:
                messages.warning(request, "Apoderado registrado, pero no se pudo ubicar la inscripción del estudiante.")

    apoderados = Apoderado.objects.all().order_by('-id')
    return render(request, 'apoderados/registrar_apoderado.html', {'apoderados': apoderados})
