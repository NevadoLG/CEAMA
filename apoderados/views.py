from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Apoderado

def registrar_apoderado(request):
    if request.method == 'POST':
        nombres = request.POST.get('nombres')
        apellidos = request.POST.get('apellidos')
        telefono = request.POST.get('telefono')
        correo = request.POST.get('correo')
        direccion = request.POST.get('direccion')

        # Validar que no exista el teléfono
        if Apoderado.objects.filter(telefono=telefono).exists():
            messages.error(request, "Ya existe un apoderado con ese número de teléfono.")
        else:
            Apoderado.objects.create(
                nombres=nombres,
                apellidos=apellidos,
                telefono=telefono,
                correo=correo,
                direccion=direccion
            )
            messages.success(request, "Apoderado registrado exitosamente.")
            return redirect('registrar_apoderado')

    apoderados = Apoderado.objects.all().order_by('-id')
    return render(request, 'panel/registrar_apoderado.html', {'apoderados': apoderados})
