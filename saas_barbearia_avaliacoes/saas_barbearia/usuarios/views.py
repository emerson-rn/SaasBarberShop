from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import UsuarioCreationForm

def cadastrar_usuario(request):
    if request.method == 'POST':
        form = UsuarioCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'Usuário {user.username} criado com sucesso!')
            return redirect('equipe')
    else:
        form = UsuarioCreationForm()
    
    return render(request, 'cadastro_usuario.html', {'form': form})
