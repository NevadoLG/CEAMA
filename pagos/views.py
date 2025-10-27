# pagos/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponseBadRequest
from django.urls import reverse
from django.contrib import messages

from estudiantes.models import Inscripcion, Estudiante
from .forms import PagoForm, ComprobanteForm
from .services import registrar_pago_con_comprobante

def registrar_pago(request):
    """
    Paso 3 del flujo: registrar pago por Inscripcion.
    Preferencia: ?inscripcion_id=XX. Como fallback, usa estudiante_id en session y toma su última inscripción.
    """
    inscripcion = None

    inscripcion_id = request.GET.get('inscripcion_id') or request.POST.get('inscripcion_id')
    if inscripcion_id:
        inscripcion = get_object_or_404(Inscripcion, id=inscripcion_id)
    else:
        estudiante_id = request.session.get('estudiante_id')
        if estudiante_id:
            est = get_object_or_404(Estudiante, id=estudiante_id)
            inscripcion = Inscripcion.objects.filter(estudiante=est).order_by('-id').first()

    if not inscripcion:
        return HttpResponseBadRequest("Falta inscripcion_id o no se pudo derivar desde la sesión.")

    if request.method == 'GET':
        pago_form = PagoForm()
        comp_form = ComprobanteForm()
        return render(request, 'pagos/registrar_pago.html', {
            'inscripcion': inscripcion,
            'pago_form': pago_form,
            'comp_form': comp_form,
        })

    # POST
    pago_form = PagoForm(request.POST)
    comp_form = ComprobanteForm(request.POST, request.FILES)

    if pago_form.is_valid() and comp_form.is_valid():
        archivo = request.FILES.get('archivo')
        pago = registrar_pago_con_comprobante(inscripcion, pago_form.cleaned_data, archivo)

        # UX: notificación y redirección (ajusta a donde quieras volver)
        messages.success(request, "Pago registrado correctamente.")
        return redirect(reverse('registrar_pago') + f'?inscripcion_id={inscripcion.id}')
    else:
        # Responder igual que tus pantallas (JSON de error o recarga con errores)
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'status': 'error', 'errors': {
                'pago': pago_form.errors, 'comprobante': comp_form.errors
            }}, status=400)

        return render(request, 'pagos/registrar_pago.html', {
            'inscripcion': inscripcion,
            'pago_form': pago_form,
            'comp_form': comp_form,
        }, status=400)
