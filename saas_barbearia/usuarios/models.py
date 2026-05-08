from django.contrib.auth.models import AbstractUser
from django.db import models

class Usuario(AbstractUser):
    class Tipo(models.TextChoices):
        ADMIN = 'ADMIN', 'Administrador'
        BARBEIRO = 'BARBEIRO', 'Barbeiro'
        CLIENTE = 'CLIENTE', 'Cliente'

    tipo = models.CharField(
        max_length=20,
        choices=Tipo.choices,
        default=Tipo.CLIENTE
    )
    telefone = models.CharField(max_length=15, blank=True, null=True)

    def __str__(self):
        return f"{self.username} ({self.get_tipo_display()})"

    @property
    def total_ganhos(self):
        if self.tipo == 'BARBEIRO':
            # Soma o preço de todos os serviços dos agendamentos finalizados
            return sum(ag.servico.preco for ag in self.agendamentos_barbeiro.filter(finalizado=True))
        return 0