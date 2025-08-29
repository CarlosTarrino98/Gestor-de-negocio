from django.contrib.auth.decorators import login_required
from django.shortcuts import render

@login_required  # Asegúrate de que solo los usuarios autenticados puedan ver esta vista
def home(request):
    return render(request, 'home/home.html', {'usuario': request.user.username})