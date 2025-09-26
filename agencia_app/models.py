from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.hashers import make_password, check_password
import base64
from datetime import datetime

class Usuario(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    contrasena = models.CharField(max_length=128)  # Se almacenará hasheada
    
    def save(self, *args, **kwargs):
        # Hashear la contraseña antes de guardar
        if not self.contrasena.startswith('pbkdf2_'):
            self.contrasena = make_password(self.contrasena)
        super().save(*args, **kwargs)
    
    def verificar_contrasena(self, contrasena):
        return check_password(contrasena, self.contrasena)
    
    def __str__(self):
        return self.nombre

class Dato(models.Model):
    imagen = models.TextField(blank=True, null=True)  # Almacenar base64
    texto = models.TextField()
    titulo = models.CharField(max_length=200)
    fecha = models.DateTimeField(auto_now_add=True)
    fecha_grupo = models.CharField(max_length=20)
    
    def __str__(self):
        return f"{self.titulo} - {self.fecha.strftime('%Y-%m-%d %H:%M:%S')}"

class PersonaRegistrada(models.Model):
    nombre = models.CharField(max_length=100)
    carnet = models.CharField(max_length=20)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.nombre} - {self.carnet}"