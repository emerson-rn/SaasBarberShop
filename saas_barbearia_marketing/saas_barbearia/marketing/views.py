from django.shortcuts import render, redirect
from .models import Campanha

def marketing(request):
    if request.method == 'POST':
        nome = request.POST.get('nome')
        mensagem = request.POST.get('mensagem')

        Campanha.objects.create(nome=nome, mensagem=mensagem)
        return redirect('marketing')

    campanhas = Campanha.objects.all()
    return render(request, 'marketing.html', {'campanhas': campanhas})
