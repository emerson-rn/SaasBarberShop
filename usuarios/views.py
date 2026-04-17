from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages

def cadastrar_usuario(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'Usuário {user.username} criado com sucesso!')
            return redirect('equipe')
    else:
        form = UserCreationForm()
    
    return render(request, 'cadastro_usuario.html', {'form': form})
