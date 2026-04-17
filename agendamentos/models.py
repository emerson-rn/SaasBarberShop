from django.db import models
from django.conf import settings
from django.forms import ValidationError
from core.models import Servico

class Agendamento(models.Model):
    cliente = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,  # Corrigido aqui
        related_name='agendamentos_cliente'
    )
    barbeiro = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,  # Corrigido aqui
        related_name='agendamentos_barbeiro'
    )
    servico = models.ForeignKey(
        Servico, 
        on_delete=models.CASCADE   # Corrigido aqui
    )
    data_hora = models.DateTimeField()
    finalizado = models.BooleanField(default=False)

    def clean(self):
        # Verifica se o barbeiro já tem compromisso nesse exato momento
        conflitos = Agendamento.objects.filter(
            barbeiro=self.barbeiro,
            data_hora=self.data_hora
        ).exclude(pk=self.pk) # Exclui o próprio agendamento em caso de edição

        if conflitos.exists():
            raise ValidationError(f"O barbeiro {self.barbeiro} já possui um agendamento para este horário.")

    def save(self, *args, **kwargs):
        self.full_clean() # Força a execução do método clean antes de salvar
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.data_hora} - {self.cliente.username} com {self.barbeiro.username}"
