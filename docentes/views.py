from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.db.models import Count
from .models import Asignacion


def asignacion_detail(request, pk):
	asignacion = get_object_or_404(Asignacion.objects.select_related('plan', 'profesor', 'aula', 'horario'), pk=pk)
	# contar matrículas actuales
	ocupados = asignacion.matriculas.count()
	data = {
		'id': asignacion.id,
		'plan': str(asignacion.plan) if asignacion.plan else None,
		'profesor': str(asignacion.profesor),
		'aula': str(asignacion.aula),
		'horario': (', '.join([d.get_codigo_display() for d in asignacion.horario.dias.all()]) + ' ' + str(asignacion.horario.hora_inicio) + '–' + str(asignacion.horario.hora_fin)) if asignacion.horario else None,
		'fecha_inicio': asignacion.fecha_inicio.isoformat() if asignacion.fecha_inicio else None,
		'fecha_fin': asignacion.fecha_fin.isoformat() if asignacion.fecha_fin else None,
		'ocupados': ocupados,
		'cupo_maximo': getattr(asignacion, 'cupo_maximo', None),
	}
	return JsonResponse(data)


def asignaciones_by_grado(request):
	"""Devuelve JSON con las asignaciones filtradas por grado (query param ?grado=...)."""
	grado = request.GET.get('grado')
	qs = Asignacion.objects.select_related('plan', 'profesor', 'aula', 'horario')
	if grado:
		qs = qs.filter(grado=grado)
	asigns = qs.annotate(ocupados=Count('matriculas'))

	lista = []
	for a in asigns:
		ocupados = getattr(a, 'ocupados', a.matriculas.count() if hasattr(a, 'matriculas') else 0)
		lista.append({
			'id': a.id,
			'plan': str(a.plan) if a.plan else None,
			'profesor': str(a.profesor),
			'aula': str(a.aula),
			'horario': (', '.join([d.get_codigo_display() for d in a.horario.dias.all()]) + ' ' + str(a.horario.hora_inicio) + '–' + str(a.horario.hora_fin)) if a.horario else None,
			'ocupados': ocupados,
			'cupo_maximo': getattr(a, 'cupo_maximo', None),
		})

	return JsonResponse(lista, safe=False)
