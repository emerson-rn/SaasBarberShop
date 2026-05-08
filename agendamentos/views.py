from django.shortcuts import render, redirect, get_object_or_404
from .models import Agendamento
from core.models import Produto, Servico 
from usuarios.models import Usuario
from django.contrib.auth.decorators import login_required
from django.db.models import F, Count, Sum
from django.http import JsonResponse
from django.utils import timezone
from datetime import datetime

@login_required
def dashboard_barbeiro(request):
    # DADOS ESTRUTURADOS: Busca a agenda ordenada
    # Removido o loop que forçava agendamento.save(), evitando que o status seja sobrescrito indevidamente
    agenda = Agendamento.objects.all().order_by('data_hora')
    
    # CONTROLE DE FLUXO: Cálculos para os indicadores da Dashboard
    total_agendamentos = agenda.count()
    
    # Proteção: verifica se o serviço existe antes de somar o preço
    faturamento = sum(item.servico.preco for item in agenda if item.finalizado and item.servico)
    alertas_estoque = Produto.objects.filter(quantidade__lte=5).count()
    
    # Adicionar tempo restante para exibição no template (sem salvar no banco)
    for agendamento in agenda:
        agendamento.tempo_restante_segundos = agendamento.tempo_restante()
    
    context = {
        'agenda': agenda,
        'total_agendamentos': total_agendamentos,
        'faturamento': faturamento,
        'alertas_estoque': alertas_estoque,
    }
    return render(request, 'dashboard.html', context)

def estoque_view(request):
    produtos = Produto.objects.all().order_by('nome')
    total_itens = produtos.count()
    itens_baixo_estoque = produtos.filter(quantidade__lte=5).count()
    
    context = {
        'produtos': produtos,
        'total_itens': total_itens,
        'itens_baixo_estoque': itens_baixo_estoque,
    }
    return render(request, 'estoque.html', context)

def lista_equipe(request):
    context = {
        'barbeiros': Usuario.objects.filter(tipo='BARBEIRO'),
        'clientes': Usuario.objects.filter(tipo='CLIENTE'),
        'administradores': Usuario.objects.filter(tipo='ADMIN'),
    }
    return render(request, 'equipe.html', context)

def novo_agendamento(request):
    erro_validacao = None
    
    if request.method == 'POST':
        try:
            # CONVERSÃO: Transforma a string do HTML em um objeto datetime ciente do fuso horário
            data_hora_str = request.POST.get('data_hora')
            data_hora_obj = datetime.strptime(data_hora_str, '%Y-%m-%dT%H:%M')
            data_hora_obj = timezone.make_aware(data_hora_obj)

            Agendamento.objects.create(
                cliente_id=request.POST.get('cliente'),
                servico_id=request.POST.get('servico'),
                barbeiro_id=request.POST.get('barbeiro'),
                data_hora=data_hora_obj
            )
            return redirect('dashboard')
        except Exception as e:
            erro_validacao = str(e)

    context = {
        'clientes': Usuario.objects.filter(tipo='CLIENTE'),
        'barbeiros': Usuario.objects.filter(tipo='BARBEIRO'),
        'servicos': Servico.objects.all(),
        'erro_validacao': erro_validacao,
    }
    return render(request, 'agendamento_form.html', context)

def editar_agendamento(request, pk):
    agendamento = get_object_or_404(Agendamento, pk=pk)
    erro_validacao = None
    
    if request.method == 'POST':
        try:
            # CONVERSÃO: Transforma a string do HTML em um objeto datetime ciente do fuso horário
            data_hora_str = request.POST.get('data_hora')
            data_hora_obj = datetime.strptime(data_hora_str, '%Y-%m-%dT%H:%M')
            data_hora_obj = timezone.make_aware(data_hora_obj)

            agendamento.cliente_id = request.POST.get('cliente')
            agendamento.servico_id = request.POST.get('servico')
            agendamento.barbeiro_id = request.POST.get('barbeiro')
            agendamento.data_hora = data_hora_obj
            
            # O status será validado pela lógica do model.save()
            agendamento.save()
            return redirect('dashboard')
        except Exception as e:
            erro_validacao = str(e)
            agendamento.refresh_from_db()

    context = {
        'agendamento': agendamento,
        'clientes': Usuario.objects.filter(tipo='CLIENTE'),
        'barbeiros': Usuario.objects.filter(tipo='BARBEIRO'),
        'servicos': Servico.objects.all(),
        'erro_validacao': erro_validacao,
    }
    return render(request, 'agendamento_form.html', context)

@login_required
def novo_produto(request):
    if request.method == 'POST':
        Produto.objects.create(
            nome=request.POST.get('nome'),
            quantidade=int(request.POST.get('quantidade', 0)),
            preco_custo=float(request.POST.get('preco', 0))
        )
        return redirect('estoque')
    return render(request, 'produto_form.html')

def editar_produto(request, pk):
    produto = get_object_or_404(Produto, pk=pk)
    if request.method == 'POST':
        produto.nome = request.POST.get('nome')
        produto.quantidade = request.POST.get('quantidade')
        produto.preco_custo = request.POST.get('preco')
        produto.save()
        return redirect('estoque')
    return render(request, 'produto_form.html', {'produto': produto})

def deletar_produto(request, pk):
    produto = get_object_or_404(Produto, pk=pk)
    if request.method == 'POST':
        produto.delete()
        return redirect('estoque')
    return render(request, 'confirmar_exclusao.html', {'item': produto, 'tipo': 'produto'})

def excluir_agendamento(request, pk):
    agendamento = get_object_or_404(Agendamento, pk=pk)
    if request.method == 'POST':
        agendamento.delete()
        return redirect('dashboard')
    return render(request, 'confirmar_exclusao.html', {'item': agendamento, 'tipo': 'agendamento'})

@login_required
def historico_agendamentos(request):
    if request.user.tipo == 'BARBEIRO':
        agendamentos = Agendamento.objects.filter(barbeiro=request.user)
    elif request.user.tipo == 'CLIENTE':
        agendamentos = Agendamento.objects.filter(cliente=request.user)
    else:
        agendamentos = Agendamento.objects.all()
    
    status_filter = request.GET.get('status')
    if status_filter:
        agendamentos = agendamentos.filter(status=status_filter)
    
    data_inicio = request.GET.get('data_inicio')
    data_fim = request.GET.get('data_fim')
    if data_inicio:
        agendamentos = agendamentos.filter(data_hora__gte=data_inicio)
    if data_fim:
        agendamentos = agendamentos.filter(data_hora__lte=data_fim)
    
    agendamentos = agendamentos.order_by('-data_hora')
    
    context = {
        'agendamentos': agendamentos,
        'status_choices': Agendamento.STATUS_CHOICES,
        'status_filter': status_filter,
    }
    return render(request, 'historico.html', context)

@login_required
def relatorios(request):
    from datetime import timedelta
    data_limite = timezone.now() - timedelta(days=30)
    
    agendamentos_periodo = Agendamento.objects.filter(data_hora__gte=data_limite)
    total_agendamentos = agendamentos_periodo.count()
    agendamentos_finalizados = agendamentos_periodo.filter(status='finalizado').count()
    
    faturamento_total = agendamentos_periodo.filter(status='finalizado').aggregate(total=Sum('servico__preco'))['total'] or 0
    por_status = agendamentos_periodo.values('status').annotate(count=Count('id'))
    por_servico = agendamentos_periodo.values('servico__nome').annotate(count=Count('id')).order_by('-count')[:5]
    
    por_barbeiro = agendamentos_periodo.values('barbeiro__username').annotate(
        count=Count('id'),
        faturamento=Sum('servico__preco')
    ).order_by('-count')[:5]
    
    produtos_falta = Produto.objects.filter(quantidade__lte=F('quantidade_minima')).order_by('quantidade')
    
    context = {
        'total_agendamentos': total_agendamentos,
        'agendamentos_finalizados': agendamentos_finalizados,
        'faturamento_total': faturamento_total,
        'por_status': por_status,
        'por_servico': por_servico,
        'por_barbeiro': por_barbeiro,
        'produtos_falta': produtos_falta,
    }
    return render(request, 'relatorios.html', context)

@login_required
def atualizar_status_agendamento(request, pk):
    if request.method == 'POST':
        agendamento = get_object_or_404(Agendamento, pk=pk)
        novo_status = request.POST.get('status')
        if novo_status in dict(Agendamento.STATUS_CHOICES):
            agendamento.status = novo_status
            if novo_status == 'finalizado':
                agendamento.finalizado = True
            agendamento.save()
            return JsonResponse({'success': True, 'status': novo_status})
    return JsonResponse({'success': False, 'error': 'Erro ao atualizar'}, status=400)

@login_required
def verificar_agendamentos_pendentes(request):
    from datetime import timedelta
    agora = timezone.now()
    agendamentos_pendentes = Agendamento.objects.filter(
        data_hora__gte=agora - timedelta(minutes=5),
        data_hora__lte=agora + timedelta(minutes=5),
        status__in=['agendado', 'confirmado']
    ).select_related('cliente', 'barbeiro', 'servico')
    
    return JsonResponse({
        'agendamentos': [{
            'id': a.id,
            'cliente': a.cliente.username,
            'barbeiro': a.barbeiro.username,
            'servico': a.servico.nome,
            'data_hora': a.data_hora.strftime('%H:%M'),
        } for a in agendamentos_pendentes]
    })

@login_required
def confirmar_chegada(request, pk):
    if request.method == 'POST':
        agendamento = get_object_or_404(Agendamento, pk=pk)
        if request.POST.get('acao') == 'confirmar':
            agendamento.status = 'confirmado'
            agendamento.save()
            return JsonResponse({'success': True})
    return JsonResponse({'success': False}, status=400)

@login_required
def portal_cliente(request):
    agendamentos = Agendamento.objects.filter(cliente=request.user).order_by('-data_hora')
    agora = timezone.now()
    context = {
        'agendamentos': agendamentos,
        'agendamentos_futuros': agendamentos.filter(data_hora__gte=agora),
        'agendamentos_passados': agendamentos.filter(data_hora__lt=agora),
    }
    return render(request, 'portal_cliente.html', context)

@login_required
def portal_barbeiro(request):
    agendamentos = Agendamento.objects.filter(barbeiro=request.user).order_by('-data_hora')
    agora = timezone.now()
    finalizados = agendamentos.filter(status='finalizado')
    
    context = {
        'agendamentos_hoje': agendamentos.filter(data_hora__date=agora.date()),
        'agendamentos_futuros': agendamentos.filter(data_hora__gte=agora),
        'agendamentos_passados': agendamentos.filter(data_hora__lt=agora),
        'total_servicos': finalizados.count(),
        'total_ganho': sum(a.servico.preco for a in finalizados if a.servico),
    }
    return render(request, 'portal_barbeiro.html', context)

@login_required
def painel_admin(request):
    if not (request.user.tipo == 'ADMIN' or request.user.is_staff):
        return redirect('dashboard')
    
    context = {
        'total_usuarios': Usuario.objects.count(),
        'total_barbeiros': Usuario.objects.filter(tipo='BARBEIRO').count(),
        'total_agendamentos': Agendamento.objects.count(),
        'agendamentos_hoje': Agendamento.objects.filter(data_hora__date=timezone.now().date()).count(),
        'total_produtos': Produto.objects.count(),
        'produtos_baixo_estoque': Produto.objects.filter(quantidade__lte=F('quantidade_minima')).count(),
        'agendamentos_recentes': Agendamento.objects.order_by('-data_hora')[:10],
        'usuarios_recentes': Usuario.objects.order_by('-date_joined')[:10],
    }
    return render(request, 'painel_admin.html', context)    