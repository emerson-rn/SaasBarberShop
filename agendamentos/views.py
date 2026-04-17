from django.shortcuts import render, redirect, get_object_or_404
from .models import Agendamento
from core.models import Produto, Servico 
from usuarios.models import Usuario
from django.contrib.auth.decorators import login_required
from django.db.models import F
from django.http import JsonResponse

@login_required
def dashboard_barbeiro(request):
    # DADOS ESTRUTURADOS: Busca a agenda ordenada
    agenda = Agendamento.objects.all().order_by('data_hora')
    
    # CONTROLE DE FLUXO: Cálculos para os indicadores da Dashboard
    total_agendamentos = agenda.count()
    faturamento = sum(item.servico.preco for item in agenda if item.finalizado)
    alertas_estoque = Produto.objects.filter(quantidade__lte=5).count()
    
    context = {
        'agenda': agenda,
        'total_agendamentos': total_agendamentos,
        'faturamento': faturamento,
        'alertas_estoque': alertas_estoque,
    }
    return render(request, 'dashboard.html', context)

def lista_estoque(request):
    # DADOS ESTRUTURADOS: Busca todos os produtos
    produtos = Produto.objects.all().order_by('nome')
    
    # Lógica para os cartões de resumo do estoque
    total_itens = produtos.count()
    itens_baixo_estoque = produtos.filter(quantidade__lte=5).count()
    
    context = {
        'produtos': produtos,
        'total_itens': total_itens,
        'itens_baixo_estoque': itens_baixo_estoque,
    }
    return render(request, 'estoque.html', context)

def lista_equipe(request):
    # DADOS ESTRUTURADOS: Segmentação para as abas do Frontend
    context = {
        'barbeiros': Usuario.objects.filter(tipo='BARBEIRO'),
        'clientes': Usuario.objects.filter(tipo='CLIENTE'),
        'administradores': Usuario.objects.filter(tipo='ADMIN'),
    }
    return render(request, 'equipe.html', context)

def novo_agendamento(request):
    if request.method == 'POST':
        # Captura e salva os dados no banco
        Agendamento.objects.create(
            cliente_id=request.POST.get('cliente'),
            servico_id=request.POST.get('servico'),
            barbeiro_id=request.POST.get('barbeiro'),
            data_hora=request.POST.get('data_hora')
        )
        return redirect('dashboard')

    context = {
        'clientes': Usuario.objects.filter(tipo='CLIENTE'),
        'barbeiros': Usuario.objects.filter(tipo='BARBEIRO'),
        'servicos': Servico.objects.all(),
    }
    return render(request, 'agendamento_form.html', context)

def editar_agendamento(request, pk):
    # Busca o agendamento específico ou retorna 404
    agendamento = get_object_or_404(Agendamento, pk=pk)
    
    if request.method == 'POST':
        # Atualização dos dados estruturados
        agendamento.cliente_id = request.POST.get('cliente')
        agendamento.servico_id = request.POST.get('servico')
        agendamento.barbeiro_id = request.POST.get('barbeiro')
        agendamento.data_hora = request.POST.get('data_hora')
        agendamento.save()
        return redirect('dashboard')

    context = {
        'agendamento': agendamento,
        'clientes': Usuario.objects.filter(tipo='CLIENTE'),
        'barbeiros': Usuario.objects.filter(tipo='BARBEIRO'),
        'servicos': Servico.objects.all(),
    }
    return render(request, 'agendamento_form.html', context)

# --- NOVA FUNÇÃO PARA CADASTRAR PRODUTO NO ESTOQUE ---
def novo_produto(request):
    if request.method == 'POST':
        nome = request.POST.get('nome')
        quantidade = request.POST.get('quantidade')
        preco_venda = request.POST.get('preco') # Vem do 'name' do input no HTML

        # Aqui usamos 'preco_custo' para bater com seu Model
        Produto.objects.create(
            nome=nome,
            quantidade=quantidade,
            preco_custo=preco_venda  
        )
        return redirect('estoque')

    return render(request, 'produto_form.html')

def editar_produto(request, pk):
    produto = get_object_or_404(Produto, pk=pk)
    
    if request.method == 'POST':
        produto.nome = request.POST.get('nome')
        produto.quantidade = request.POST.get('quantidade')
        produto.preco_custo = request.POST.get('preco') # Ajustado aqui também
        produto.save()
        return redirect('estoque')

    return render(request, 'produto_form.html', {'produto': produto})

def deletar_produto(request, pk):
    produto = get_object_or_404(Produto, pk=pk)
    if request.method == 'POST':
        produto.delete()
        return redirect('estoque')
    return render(request, 'confirmar_exclusao.html', {'item': produto, 'tipo': 'produto'})

# --- NOVAS FUNCIONALIDADES ---

@login_required
def historico_agendamentos(request):
    """View para histórico de agendamentos do usuário logado"""
    # Filtrar por tipo de usuário
    if request.user.tipo == 'BARBEIRO':
        agendamentos = Agendamento.objects.filter(barbeiro=request.user)
    elif request.user.tipo == 'CLIENTE':
        agendamentos = Agendamento.objects.filter(cliente=request.user)
    else:  # ADMIN vê todos
        agendamentos = Agendamento.objects.all()
    
    # Filtragem por status
    status_filter = request.GET.get('status')
    if status_filter:
        agendamentos = agendamentos.filter(status=status_filter)
    
    # Filtragem por data
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
    """View para relatórios e estatísticas"""
    from django.db.models import Count, Sum, Avg
    from django.utils import timezone
    from datetime import timedelta
    
    # Período padrão: últimos 30 dias
    data_limite = timezone.now() - timedelta(days=30)
    
    # Estatísticas de agendamentos
    total_agendamentos = Agendamento.objects.filter(data_hora__gte=data_limite).count()
    agendamentos_finalizados = Agendamento.objects.filter(
        data_hora__gte=data_limite, 
        status='finalizado'
    ).count()
    
    # Faturamento
    faturamento_total = Agendamento.objects.filter(
        data_hora__gte=data_limite,
        status='finalizado'
    ).aggregate(total=Sum('servico__preco'))['total'] or 0
    
    # Agendamentos por status
    por_status = Agendamento.objects.filter(
        data_hora__gte=data_limite
    ).values('status').annotate(count=Count('id'))
    
    # Agendamentos por serviço
    por_servico = Agendamento.objects.filter(
        data_hora__gte=data_limite
    ).values('servico__nome').annotate(count=Count('id')).order_by('-count')[:5]
    
    # Agendamentos por barbeiro
    por_barbeiro = Agendamento.objects.filter(
        data_hora__gte=data_limite
    ).values('barbeiro__username').annotate(
        count=Count('id'),
        faturamento=Sum('servico__preco')
    ).order_by('-count')[:5]
    
    # Produtos em falta
    produtos_falta = Produto.objects.filter(
        quantidade__lte=F('quantidade_minima')
    ).order_by('quantidade')
    
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
    """View para atualizar o status de um agendamento via AJAX"""
    if request.method == 'POST':
        agendamento = get_object_or_404(Agendamento, pk=pk)
        novo_status = request.POST.get('status')
        
        if novo_status in dict(Agendamento.STATUS_CHOICES):
            agendamento.status = novo_status
            if novo_status == 'finalizado':
                agendamento.finalizado = True
            agendamento.save()
            return JsonResponse({'success': True, 'status': novo_status})
        
        return JsonResponse({'success': False, 'error': 'Status inválido'}, status=400)
    
    return JsonResponse({'success': False, 'error': 'Método não permitido'}, status=405)