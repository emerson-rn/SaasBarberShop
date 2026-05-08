from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login
from .forms import UsuarioCreationForm


def cadastrar_usuario(request):
    """Cadastro seguro: visitante vira CLIENTE; somente admin pode criar barbeiro/admin."""
    allow_tipo = bool(request.user.is_authenticated and (request.user.tipo == 'ADMIN' or request.user.is_staff))
    if request.method == 'POST':
        form = UsuarioCreationForm(request.POST, allow_tipo=allow_tipo)
        if form.is_valid():
            user = form.save()
            if allow_tipo:
                messages.success(request, f'Usuário {user.username} criado com sucesso!')
                return redirect('equipe')
            login(request, user)
            messages.success(request, 'Conta criada com sucesso! Você entrou como cliente.')
            return redirect('portal_cliente')
    else:
        form = UsuarioCreationForm(allow_tipo=allow_tipo)
    return render(request, 'cadastro_usuario.html', {'form': form, 'allow_tipo': allow_tipo})
