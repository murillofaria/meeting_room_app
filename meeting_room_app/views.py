from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
import datetime

from .models import Reuniao, Sala

def logar(request):
    if request.user.is_authenticated:
        return redirect('reunioes')
    
    if request.method == "GET":
        return render(request, 'login.html')
    elif request.method == "POST":
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
    elif request.method == "POST":
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
        status__in = ['agendada', 'em_andamento'] # Busca no banco onde status seja agendada ou em_andamento
    ).order_by('data', 'hora_inicio') # Organiza as reuniões pela data e depois pela hora

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

    reunioes_hoje = reunioes_hoje.distinct().order_by('hora_inicio') # Removendo duplicatas

    total_salas = Sala.objects.filter(ocupada=False).count()

    contexto = {
        'organizando': organizando,
        'participando': participando,
        'reunioes_hoje': reunioes_hoje,
        'total_salas': total_salas
    }

    reunioes = Reuniao.objects.filter( # Mostrar reuniões onde o usuário é participante ou organizador
        participantes = request.user
    ) | Reuniao.objects.filter(
        organizador = request.user
    )

    reunioes = reunioes.distinct().order_by('data', 'hora_inicio')

    return render(request, 'reunioes.html', {'contexto': contexto, 'reunioes': reunioes})

@login_required
def criar_reuniao(request):
    usuarios = User.objects.all()
    salas = Sala.objects.all()
    reuniao_status = Reuniao.STATUS_CHOICES
    if request.method == "GET":
        return render(request, 'reuniao.html', {'usuarios':usuarios, "salas":salas, "reuniao_status":reuniao_status})
    elif request.method == "POST":
        titulo_form = request.POST.get('titulo', '').strip()
        descricao_form = request.POST.get('descricao') # não é necessário verificação, pois descrição é um campo opcional
        organizador_form = request.POST.get('organizador', '').strip()
        sala_form = request.POST.get('sala', '').strip()
        data_form = request.POST.get('data', '').strip()
        hr_ini_form = request.POST.get('hora_inicio', '').strip()
        hr_fim_form = request.POST.get('hora_fim', '').strip()
        status_form = request.POST.get('status', '').strip()

        participantes_form = request.POST.getlist('participante')

        if not titulo_form or not organizador_form or not sala_form or not data_form or not hr_ini_form or not hr_fim_form or not participantes_form or not status_form:
            messages.error(request, "Preencha todos os campos corretamente.")
            return redirect('criar_reuniao')

        organizador_obj = User.objects.get(id=organizador_form)
        sala_obj = Sala.objects.get(id=sala_form)

        nova_reuniao = Reuniao.objects.create(
            titulo=titulo_form,
            descricao=descricao_form,
            data=data_form,
            hora_inicio=hr_ini_form,
            hora_fim=hr_fim_form,
            status=status_form,
            organizador=organizador_obj,
            sala=sala_obj
        )

        if participantes_form:
            nova_reuniao.participantes.set(participantes_form)

        return redirect('reunioes')
    
@login_required
def alterar_reuniao(request, id):
    usuarios = User.objects.all()
    salas = Sala.objects.all()
    reuniao_status = Reuniao.STATUS_CHOICES

    reuniao_obj = Reuniao.objects.get(id=id)

    if request.method == "GET":
        return render(request, 'reuniao.html', {"reuniao_obj": reuniao_obj, 'usuarios':usuarios, "salas":salas, "reuniao_status":reuniao_status})
    elif request.method == "POST":
        titulo_form = request.POST.get('titulo', '').strip()
        descricao_form = request.POST.get('descricao')
        organizador_form = request.POST.get('organizador', '').strip()
        sala_form = request.POST.get('sala', '').strip()
        data_form = request.POST.get('data', '').strip()
        hr_ini_form = request.POST.get('hora_inicio', '').strip()
        hr_fim_form = request.POST.get('hora_fim', '').strip()
        status_form = request.POST.get('status', '').strip()

        participantes_form = request.POST.getlist('participante')

        if not titulo_form or not organizador_form or not sala_form or not data_form or not hr_ini_form or not hr_fim_form or not participantes_form or not status_form:
            messages.error(request, "Preencha todos os campos corretamente.")
            return redirect('criar_reuniao')

        organizador_obj = User.objects.get(id=organizador_form)
        sala_obj = Sala.objects.get(id=sala_form)

        reuniao_obj.titulo = titulo_form
        reuniao_obj.descricao = descricao_form
        reuniao_obj.organizador = organizador_obj
        reuniao_obj.sala = sala_obj
        reuniao_obj.data = data_form
        reuniao_obj.hora_inicio = hr_ini_form
        reuniao_obj.hora_fim = hr_fim_form
        reuniao_obj.status = status_form

        reuniao_obj.save()

        reuniao_obj.participantes.set(participantes_form)

        messages.success(request, "Reunião atualizada", extra_tags=f"reuniao_{reuniao_obj.id}") #Passando id para filtrar no HTML
        return redirect('reunioes')
    
@login_required
def excluir_reuniao(request, id):
    if request.method == "POST":
        reuniao_obj = Reuniao.objects.get(id=id)

        reuniao_obj.delete() # Deletando a reunião do banco

        return redirect('reunioes')
    
    return redirect('reunioes') #Caso tente entrar por GET, vai para tela de reunioes