from django.shortcuts import render, redirect
from django.contrib.auth.views import LoginView
from django.http import HttpResponse
from .forms import RegisterForm
from django.contrib.auth import login, authenticate
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required


class UserLoginView(LoginView):
    template_name = 'users/login.html'

@login_required
def profile_view(request):
    return render(request, "users/profile.html")

def home(request):
    return HttpResponse("Это главная страница")

from django.contrib import messages

def register(request):
    if request.method == "POST":
        print("Получен POST-запрос") 
        form = RegisterForm(request.POST)
        if form.is_valid():
            print("Форма валидна")  
            user = form.save()
            login(request, user)
            messages.success(request, "Регистрация успешна!")
            return redirect("home") 
        else:
            print("Ошибки формы:", form.errors)
            messages.error(request, "Исправьте ошибки в форме.")

    else:
        form = RegisterForm()

    return render(request, "users/register.html", {"form": form})


def user_login(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            print(f"Успешный вход: {user}")  # Проверка
            return redirect("home")
        else:
            print("Ошибка входа")  # Проверка

    return render(request, "users/login.html")



def logout_view(request):
    logout(request)
    return redirect("login")



def login_view(request):
    if request.user.is_authenticated:
        return redirect("home")  # Если пользователь уже вошел, переадресуем на главную

    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("home")  # Перенаправляем после успешного входа

    else:
        form = AuthenticationForm()

    return render(request, "users/login.html", {"form": form})