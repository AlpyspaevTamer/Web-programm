from django.shortcuts import render, redirect
from django.contrib.auth.views import LoginView
from django.http import HttpResponse
from .forms import RegisterForm
from django.contrib.auth import login

class UserLoginView(LoginView):
    template_name = 'users/login.html'

def home(request):
    return HttpResponse("Это главная страница")

def register(request):
    if request.method == "POST":
        print("Получен POST-запрос")  # Проверка
        form = RegisterForm(request.POST)
        if form.is_valid():
            print("Форма валидна")  # Проверяем, проходит ли валидация
            user = form.save()
            login(request, user)
            return redirect("home")  # Перенаправление на главную
        else:
            print("Ошибки формы:", form.errors)  # Вывод ошибок

    else:
        form = RegisterForm()

    return render(request, "users/register.html", {"form": form})
