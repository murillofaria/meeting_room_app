from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.http import HttpResponse

def logar(request):
    if request.method == "GET":
        return render(request, 'login.html')
    elif request.method == "POST":
        # Verifica se o usuário é válido
        email_form = request.POST.get('email')
        senha_form = request.POST.get('senha')
        usuario = authenticate(request, username=email_form, password=senha_form)

        if usuario is not None: # Usuário válido
            login(request, usuario)
            return HttpResponse("Logado com sucesso!") # Redirecionar para página de reservar salas
        else: # Usuário incorreto
            messages.error(request, "E-mail ou senha incorreta!")
            return render(request, 'login.html', {'email_form' : email_form})
        
def cadastrar(request):
    if request.method == "GET":
        return render(request, 'cadastro.html')
    elif request.method == 'POST':
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