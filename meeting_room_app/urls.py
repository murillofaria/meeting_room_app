from django.urls import path
from . import views

urlpatterns = [
    path('inicio/', views.logar, name='login'),
    path('inicio/cadastro', views.cadastrar, name='cadastro'),
    path('reunioes/', views.reunioes, name='reunioes'),
    path('logout/', views.deslogar, name='logout'),
    path('reunioes/criar', views.criar_reuniao, name="criar_reuniao"),
    path('reunioes/alterar/<int:id>', views.alterar_reuniao, name="alterar_reuniao"),
    path('reuniao/excluir/<int:id>', views.excluir_reuniao, name="excluir_reuniao"),
    path('sala/criar', views.criar_sala, name="criar_sala")
]