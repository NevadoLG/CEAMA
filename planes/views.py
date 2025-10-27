from django.http import JsonResponse
from .models import Plan

def planes_por_nivel(request):
    nivel = request.GET.get('nivel')
    if nivel not in ('primaria', 'secundaria'):
        return JsonResponse([], safe=False)
    data = list(
        Plan.objects.filter(nivel=nivel, activo=True)
        .order_by('area', 'nombre')
        .values('id', 'nombre')
    )
    return JsonResponse(data, safe=False)
