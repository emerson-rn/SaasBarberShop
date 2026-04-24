from django.contrib import admin
from .models import Servico, Produto

@admin.register(Servico)
class ServicoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'preco', 'duracao_minutos')
    list_filter = ('duracao_minutos',)
    search_fields = ('nome', 'descricao')
    ordering = ('nome',)

@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'preco_custo', 'quantidade')
    list_filter = ('quantidade',)
    search_fields = ('nome',)
    ordering = ('nome',)