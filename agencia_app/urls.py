from django.urls import path
from . import views

urlpatterns = [
    path('inicio_admin/', views.inicio_admin, name='inicio_admin'),
    path('inicio/', views.inicio, name='inicio'),
    path('agregar/', views.agregar_dato, name='agregar_dato'),
    path('eliminar/<int:id>/', views.eliminar_dato, name='eliminar_dato'),  # Cambiado: indice → id
    path('agregar_usuario/', views.agregar_usuario, name='agregar_usuario'),
    path('eliminar_usuario/<int:id>/', views.eliminar_usuario, name='eliminar_usuario'),  # Cambiado: indice → id
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
]