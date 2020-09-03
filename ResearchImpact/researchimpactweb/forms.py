from django import forms

from .models import *



class LoginForm(forms.ModelForm):
	class Meta:
		model = User
		fields = ('usuario','password',)

		widgets = {'password': forms.PasswordInput(),}

class AniosForm(forms.ModelForm):
	class Meta:
		model = Anios
		fields = ('aniosPublicacionesInicio','aniosPublicacionesFin','aniosCitacionesInicio','aniosPCitacionesFin',)

class PesosForm(forms.ModelForm):
	class Meta:
		model = Pesos
		fields = ('pesoPublicaciones','pesoCitaciones',)

		
		
