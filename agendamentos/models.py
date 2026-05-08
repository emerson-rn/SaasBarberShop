from django.db import models
from django.conf import settings
from django.forms import ValidationError
from core.models import Servico
from django.utils import timezone
from datetime import timedelta

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
        """
        Verifica se o agendamento está atrasado.
        Lógica: A hora passou E o status ainda é 'agendado'.
        Se o barbeiro já confirmou ou o cliente está aguardando, NÃO conta como atrasado.
        """
        agora = timezone.now()
        return self.data_hora < agora and self.status == 'agendado'

    def tempo_restante(self):
        """Retorna o tempo restante em segundos até o agendamento"""
        agora = timezone.now()
        if self.data_hora > agora:
            return int((self.data_hora - agora).total_seconds())
        return 0

    def clean(self):
        """Validações de negócio antes de salvar"""
        if not self.data_hora:
            return

        # 1. Verifica se o barbeiro já tem compromisso nesse exato momento
        conflitos = Agendamento.objects.filter(
            barbeiro=self.barbeiro,
            data_hora=self.data_hora
        ).exclude(pk=self.pk)

        if conflitos.exists():
            raise ValidationError(f"O barbeiro {self.barbeiro} já possui um agendamento para este horário.")
        
        # 2. Verifica se o cliente já tem agendamento no mesmo dia (evita spam)
        dia_agendamento = self.data_hora.date()
        conflitos_cliente = Agendamento.objects.filter(
            cliente=self.cliente,
            data_hora__date=dia_agendamento
        ).exclude(pk=self.pk).exclude(status='cancelado')
        
        if conflitos_cliente.exists():
            raise ValidationError(f"O cliente {self.cliente.username} já possui um agendamento neste dia.")
        
        # 3. Verifica intervalo de duração do serviço para evitar sobreposição
        duracao = self.servico.duracao_minutos or 30
        inicio = self.data_hora
        fim = self.data_hora + timedelta(minutes=duracao)
        
        # Busca agendamentos que terminariam depois do início deste ou começariam antes do fim deste
        conflitos_intervalo = Agendamento.objects.filter(
            barbeiro=self.barbeiro,
            data_hora__lt=fim,
            data_hora__gt=inicio - timedelta(minutes=duracao)
        ).exclude(pk=self.pk).exclude(status='cancelado')
        
        if conflitos_intervalo.exists():
            raise ValidationError(f"Conflito de horário! O barbeiro já tem um serviço que ocupa este período.")

    def save(self, *args, **kwargs):
        # Se a função is_atrasado retornar True, força o status para atrasado
        if self.is_atrasado():
            self.status = 'atrasado'
            
        # Garante que agendamentos finalizados marquem o booleano finalizado como True
        if self.status == 'finalizado':
            self.finalizado = True
            
        # Executa as validações do método clean()
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        # Formata a data para ficar legível: 24/04 10:30 - Emerson com Ninja
        data_formatada = timezone.localtime(self.data_hora).strftime('%d/%m %H:%M')
        return f"{data_formatada} - {self.cliente.username} com {self.barbeiro.username}"