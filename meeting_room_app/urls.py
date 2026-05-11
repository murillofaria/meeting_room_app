from django.urls import path
from . import views

urlpatterns = [
    path('inicio/', views.logar, name='login'),
    path('inicio/cadastro', views.cadastrar, name='cadastro')
]