from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseBadRequest
from django.urls import reverse
from django.contrib import messages

from estudiantes.models import Inscripcion, Estudiante
from .forms import PagoForm
from .services import registrar_pago_con_comprobantes

MAX_FILES = 3  # límite de comprobantes por pago

def registrar_pago(request):
    """
    Paso 3 del flujo: registrar pago por Inscripcion.
    GET: muestra formulario (o modo lectura si ?ok=1).
    POST: valida y registra pago + comprobantes (1..MAX_FILES).
    """
    # --- localizar inscripcion ---
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

    # pagos previos / último pago
    pagos_previos = inscripcion.pago_set.select_related().order_by('-id')
    last_pago = pagos_previos.first()

    # --- GET: pintar formulario ---
    if request.method == 'GET':
        pagado = request.GET.get('ok') == '1'
        ctx = {
            'inscripcion': inscripcion,
            'pago_form': PagoForm(),
            'pagado': pagado,
            'last_pago': last_pago,
            'MAX_FILES': MAX_FILES,
        }
        return render(request, 'pagos/registrar_pago.html', ctx)

    # --- POST: validar y guardar ---
    pago_form = PagoForm(request.POST)

    # Leer SIEMPRE los archivos directo del request (nombre: "archivos")
    archivos = request.FILES.getlist('archivos')  # [] si no subieron nada

    if pago_form.is_valid():
        # Requerir al menos un archivo
        if len(archivos) == 0:
            pago_form.add_error(None, "Debes adjuntar al menos un comprobante (PDF o imagen).")
        # Límite back-end de archivos
        elif len(archivos) > MAX_FILES:
            pago_form.add_error(None, f"Solo se permiten {MAX_FILES} comprobantes por pago.")
        else:
            registrar_pago_con_comprobantes(inscripcion, pago_form.cleaned_data, archivos)
            messages.success(request, "Pago registrado. Queda pendiente de confirmación por administración.")
            return redirect(f"{reverse('registrar_pago')}?inscripcion_id={inscripcion.id}&ok=1")

    # --- errores: re-render ---
    return render(request, 'pagos/registrar_pago.html', {
        'inscripcion': inscripcion,
        'pago_form': pago_form,
        'pagado': False,
        'last_pago': last_pago,
        'MAX_FILES': MAX_FILES,
    }, status=400)
