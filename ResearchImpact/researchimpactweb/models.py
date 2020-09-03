
from django.db import models
from django.utils import timezone




class User(models.Model):
    usuario = models.CharField(max_length=16)
    password = models.CharField(max_length=16)

class Anios(models.Model):
    aniosPublicacionesInicio = models.IntegerField()
    aniosPublicacionesFin = models.IntegerField()
    aniosCitacionesInicio = models.IntegerField()
    aniosPCitacionesFin = models.IntegerField()

class Pesos(models.Model):
    pesoPublicaciones = models.DecimalField(max_digits= 4, decimal_places = 2)
    pesoCitaciones = models.DecimalField(max_digits= 4, decimal_places = 2)