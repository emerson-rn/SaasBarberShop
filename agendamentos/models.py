from django.db import models
from django.conf import settings
from django.forms import ValidationError
from core.models import Servico
from django.utils import timezone

class Agendamento(models.Model):
    STATUS_CHOICES = [
        ('agendado', 'Agendado'),
        ('confirmado', 'Confirmado'),
        ('aguardando', 'Aguardando'),
        ('em_atendimento', 'Em Atendimento'),
        ('finalizado', 'Finalizado'),
        ('cancelado', 'Cancelado'),
        ('atrasado', 'Atrasado'),
    ]
    
    cliente = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name='agendamentos_cliente'
    )
    barbeiro = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name='agendamentos_barbeiro'
    )
    servico = models.ForeignKey(
        Servico, 
        on_delete=models.CASCADE
    )
    data_hora = models.DateTimeField()
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='agendado'
    )
    observacoes = models.TextField(blank=True, null=True)
    finalizado = models.BooleanField(default=False)

    def is_atrasado(self):
        """Verifica se o agendamento está atrasado"""
        return self.data_hora < timezone.now() and self.status not in ['finalizado', 'cancelado', 'em_atendimento', 'aguardando']

    def tempo_restante(self):
        """Retorna o tempo restante em segundos até o agendamento"""
        if self.data_hora > timezone.now():
            return int((self.data_hora - timezone.now()).total_seconds())
        return 0

    def clean(self):
        # Verifica se o barbeiro já tem compromisso nesse exato momento
        conflitos = Agendamento.objects.filter(
            barbeiro=self.barbeiro,
            data_hora=self.data_hora
        ).exclude(pk=self.pk) # Exclui o próprio agendamento em caso de edição

        if conflitos.exists():
            raise ValidationError(f"O barbeiro {self.barbeiro} já possui um agendamento para este horário.")

    def save(self, *args, **kwargs):
        # Atualiza status automaticamente se estiver atrasado
        if self.is_atrasado() and self.status not in ['finalizado', 'cancelado', 'em_atendimento', 'aguardando']:
            self.status = 'atrasado'
        self.full_clean() # Força a execução do método clean antes de salvar
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.data_hora} - {self.cliente.username} com {self.barbeiro.username}"
