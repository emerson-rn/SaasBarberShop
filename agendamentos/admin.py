from django.contrib import admin
from .models import Agendamento

@admin.register(Agendamento)
class AgendamentoAdmin(admin.ModelAdmin):
    list_display = ('cliente', 'barbeiro', 'servico', 'data_hora', 'status', 'finalizado')
    list_filter = ('status', 'finalizado', 'data_hora', 'barbeiro')
    search_fields = ('cliente__username', 'barbeiro__username', 'servico__nome', 'observacoes')
    ordering = ('-data_hora',)
    date_hierarchy = 'data_hora'

    fieldsets = (
        ('Informações do Agendamento', {
            'fields': ('cliente', 'barbeiro', 'servico', 'data_hora')
        }),
        ('Status e Observações', {
            'fields': ('status', 'observacoes', 'finalizado')
        }),
    )