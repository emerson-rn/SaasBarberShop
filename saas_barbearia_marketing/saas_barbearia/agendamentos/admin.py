from django.contrib import admin
from .models import Agendamento, Avaliacao
admin.site.register(Agendamento)

@admin.register(Avaliacao)
class AvaliacaoAdmin(admin.ModelAdmin):
    list_display = ('cliente', 'barbeiro', 'nota', 'criado_em')
    list_filter = ('nota', 'criado_em')
    search_fields = ('cliente__username', 'barbeiro__username', 'comentario')
