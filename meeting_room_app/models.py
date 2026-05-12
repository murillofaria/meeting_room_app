from django.db import models
from django.contrib.auth.models import User

class Sala(models.Model):
    nome = models.CharField(max_length=100)
    capacidade = models.IntegerField()
    localizacao = models.CharField(max_length=200)
    descricao = models.TextField(blank=True)
    ativa = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.nome} (cap. {self.capacidade})"
    
class Reuniao(models.Model):
    STATUS_CHOICES = [
        ('agendada', 'Agendada'),
        ('em_andamento', 'Em Andamento'),
        ('concluida', 'Concluída'),
        ('cancelada', 'Cancelada')
    ]

    titulo = models.CharField(max_length=100)
    descricao = models.TextField(blank=True)
    organizador = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reunioes_organizadas')
    participantes = models.ManyToManyField(User, related_name='reunioes_participando', blank=True)
    sala = models.ForeignKey(Sala, on_delete=models.CASCADE, related_name='reunioes')
    data = models.DateField()
    hora_inicio = models.TimeField()
    hora_fim = models.TimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="agendada")

    def __str__(self):
        return f"{self.titulo} - {self.data} - {self.hora_inicio}"