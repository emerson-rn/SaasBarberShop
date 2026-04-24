from django.db import models

class Servico(models.Model):
    nome = models.CharField(max_length=100)
    descricao = models.TextField(blank=True, null=True)
    preco = models.DecimalField(max_digits=10, decimal_places=2)
    duracao_minutos = models.IntegerField(default=30)

    def __str__(self):
        return f"{self.nome} - R$ {self.preco}"

class Produto(models.Model):
    nome = models.CharField(max_length=100)
    quantidade = models.IntegerField(default=0)
    quantidade_minima = models.IntegerField(default=5)
    preco_custo = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.nome

    @property
    def precisa_repor(self):
        return self.quantidade <= self.quantidade_minima