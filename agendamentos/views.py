from django.shortcuts import render, redirect, get_object_or_404
from .models import Agendamento
from core.models import Produto, Servico 
from usuarios.models import Usuario
from django.contrib.auth.decorators import login_required

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