from django.shortcuts import render, get_object_or_404

from django.http import JsonResponse
from django.db.models import Count
from .models import Asignacion


def fmt_time(t):
    try:
        s = t.strftime('%I:%M %p')
        return s.lstrip('0')
    except Exception:
        return str(t)


def asignacion_detail(request, pk):
	asignacion = get_object_or_404(Asignacion.objects.select_related('plan', 'aula', 'horario').prefetch_related('profesores'), pk=pk)
	# contar matrículas actuales
	ocupados = asignacion.matriculas.count()

	# formato horario: lista de días y rango horario en formato legible
	dias_list = [d.get_codigo_display() for d in asignacion.horario.dias.all()] if asignacion.horario else []
	hora_inicio = fmt_time(asignacion.horario.hora_inicio) if asignacion.horario else None
	hora_fin = fmt_time(asignacion.horario.hora_fin) if asignacion.horario else None

	data = {
		'id': asignacion.id,
		'plan': str(asignacion.plan) if asignacion.plan else None,
		'profesores': [str(p) for p in asignacion.profesores.all()],
		'profesor': ' / '.join(str(p) for p in asignacion.profesores.all()),
		'aula': str(asignacion.aula),
		'horario': {
			'dias': dias_list,
			'hora_inicio': hora_inicio,
			'hora_fin': hora_fin,
			'hora_range': (f"{hora_inicio} – {hora_fin}" if hora_inicio and hora_fin else None),
			'dias_text': ', '.join(dias_list) if dias_list else None,
		} if asignacion.horario else None,
		'fecha_inicio': asignacion.fecha_inicio.isoformat() if asignacion.fecha_inicio else None,
		'fecha_fin': asignacion.fecha_fin.isoformat() if asignacion.fecha_fin else None,
		'ocupados': ocupados,
		'cupo_maximo': getattr(asignacion, 'cupo_maximo', None),
		'precio': float(asignacion.precio) if hasattr(asignacion, 'precio') and asignacion.precio else 0,
	}
	return JsonResponse(data)


def asignaciones_by_grado(request):
	"""Devuelve JSON con las asignaciones filtradas por grado (query param ?grado=...)."""
	grado = request.GET.get('grado')
	qs = Asignacion.objects.select_related('plan', 'aula', 'horario').prefetch_related('profesores')
	if grado:
		qs = qs.filter(grado=grado)
	asigns = qs.annotate(ocupados=Count('matriculas'))

	lista = []
	for a in asigns:
		ocupados = getattr(a, 'ocupados', a.matriculas.count() if hasattr(a, 'matriculas') else 0)
		dias_list = [d.get_codigo_display() for d in a.horario.dias.all()] if a.horario else []
		hora_inicio = fmt_time(a.horario.hora_inicio) if a.horario else None
		hora_fin = fmt_time(a.horario.hora_fin) if a.horario else None
		lista.append({
			'id': a.id,
			'plan': str(a.plan) if a.plan else None,
			'profesores': [str(p) for p in a.profesores.all()],
			'profesor': ' / '.join(str(p) for p in a.profesores.all()),
			'aula': str(a.aula),
			'horario': {
				'dias': dias_list,
				'dias_text': ', '.join(dias_list) if dias_list else None,
				'hora_inicio': hora_inicio,
				'hora_fin': hora_fin,
				'hora_range': (f"{hora_inicio} – {hora_fin}" if hora_inicio and hora_fin else None),
			} if a.horario else None,
			'ocupados': ocupados,
			'cupo_maximo': getattr(a, 'cupo_maximo', None),
		})

	return JsonResponse(lista, safe=False)
