from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
import datetime

from .models import Reuniao, Sala

def logar(request):
    if request.user.is_authenticated:
        return redirect('reunioes')
    
    if request.method == "GET":
        return render(request, 'login.html')
    else:
        # Verifica se o usuário é válido
        email_form = request.POST.get('email')
        senha_form = request.POST.get('senha')
        usuario = authenticate(request, username=email_form, password=senha_form)

        if usuario is not None: # Usuário válido
            login(request, usuario)
            return redirect('reunioes')
        else: # Usuário incorreto
            messages.error(request, "E-mail ou senha incorreta!")
            return render(request, 'login.html', {'email_form' : email_form})

def deslogar(request): # Desloga e redireciona para página inicial de login
    logout(request)
    return redirect('login')

def cadastrar(request):
    if request.user.is_authenticated:
        return redirect('reunioes')
    
    if request.method == "GET":
        return render(request, 'cadastro.html')
    else:
        # Validação para aceitar somente campos preenchidos(o strip garante que não será enganado com espaços antes e depois)
        nomeCompleto_form = request.POST.get('nomeCompleto', '').strip()
        email_form = request.POST.get('email', '').strip()
        senha_form = request.POST.get('senha', '').strip()

        if not nomeCompleto_form or not email_form or not senha_form:
            messages.error(request, "Preencha todos os campos corretamente!")
            return render(request, "cadastro.html", {"nomeCompleto_form" : nomeCompleto_form,
                                                     "email_form" : email_form, "senha_form" : senha_form})
        
        # Verifica se o email digitado já existe no banco, caso exista irá aparecer uma mensagem de erro
        if User.objects.filter(username=email_form).exists():
            messages.error(request, "Este e-mail já está em uso. Tente outro.")
            return render(request, "cadastro.html")
        
        # Caso os campos sejam preenchidos corretamente, o usuário será cadastrado no banco
        User.objects.create_user(
            first_name = nomeCompleto_form,
            username = email_form,
            password = senha_form
        )

        return redirect('login')
    
@login_required
def reunioes(request):
    hoje = datetime.date.today()

    #Filtra e ordena as reuniões
    organizando = Reuniao.objects.filter(
        organizador = request.user,
        status__in = ['agendada', 'em_andamento']
    ).order_by('data', 'hora_inicio')

    participando = Reuniao.objects.filter(
        participantes = request.user,
        status__in = ['agendada', 'em_andamento']
    ).order_by('data', 'hora_inicio')

    reunioes_hoje = Reuniao.objects.filter(
        data = hoje,
        status__in = ['agendada', 'em_andamento']
    ).filter(
        organizador = request.user
    ) | Reuniao.objects.filter(
        data = hoje,
        status__in = ['agendada', 'em_andamento'],
        participantes = request.user
    )

    reunioes_hoje = reunioes_hoje.distinct().order_by('hora_inicio')

    total_salas = Sala.objects.filter(ativa=True).count()
    total_agendadas = organizando.count()

    variaveis = {
        'organizando': organizando,
        'participando': participando,
        'reunioes_hoje': reunioes_hoje,
        'total_salas': total_salas,
        'total_agendadas': total_agendadas
    }

    return render(request, 'reunioes.html', variaveis)