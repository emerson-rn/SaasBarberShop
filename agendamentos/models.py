from django.db import models
from django.conf import settings
from django.forms import ValidationError
from core.models import Servico

class Agendamento(models.Model):
    STATUS_CHOICES = [
        ('agendado', 'Agendado'),
        ('confirmado', 'Confirmado'),
        ('em_andamento', 'Em Andamento'),
        ('finalizado', 'Finalizado'),
        ('cancelado', 'Cancelado'),
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

    def clean(self):
        from datetime import timedelta
        
        # Verifica se o barbeiro já tem compromisso nesse exato momento
        conflitos = Agendamento.objects.filter(
            barbeiro=self.barbeiro,
            data_hora=self.data_hora
        ).exclude(pk=self.pk)

        if conflitos.exists():
            raise ValidationError(f"O barbeiro {self.barbeiro} já possui um agendamento para este horário.")
        
        # Verifica se o cliente já tem agendamento no mesmo dia
        if self.data_hora and self.cliente:
            dia_agendamento = self.data_hora.date()
            conflitos_cliente = Agendamento.objects.filter(
                cliente=self.cliente,
                data_hora__date=dia_agendamento
            ).exclude(pk=self.pk).exclude(status='cancelado')
            
            if conflitos_cliente.exists():
                raise ValidationError(f"O cliente {self.cliente.username} já possui um agendamento neste dia.")
        
        # Verifica intervalo mínimo de 30 minutos entre agendamentos do mesmo barbeiro
        if self.data_hora and self.barbeiro and self.servico:
            duracao = self.servico.duracao_minutos or 30
            inicio = self.data_hora
            fim = self.data_hora + timedelta(minutes=duracao)
            
            # Verifica se há agendamento que se sobrepõe no intervalo do barbeiro
            conflitos_intervalo = Agendamento.objects.filter(
                barbeiro=self.barbeiro,
                data_hora__lt=fim,
                data_hora__gte=inicio - timedelta(minutes=30)
            ).exclude(pk=self.pk).exclude(status='cancelado')
            
            if conflitos_intervalo.exists():
                raise ValidationError(f"O barbeiro {self.barbeiro.username} já possui um agendamento neste horário ou próximo. O próximo horário disponível é a partir de {fim.strftime('%H:%M')}.")

    def save(self, *args, **kwargs):
        self.full_clean() # Força a execução do método clean antes de salvar
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.data_hora} - {self.cliente.username} com {self.barbeiro.username}"
