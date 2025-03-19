from django.urls import path, include
from django.contrib.auth.decorators import login_required
from django.contrib import admin
from .views import *
from django.shortcuts import redirect


urlpatterns = [
    path("", login_required(home_view), name="home"), #Главная страница
    path("users/", include("users.urls")),  #страница связанная с Регой и Логином
    path("admin/", admin.site.urls), #страница админки
    path('first/<int:classroom_id>/', first_page, name='first'),
    path('second/', second_class_view, name='second'),
    path('third/', third_class_view, name='third'),
    path('fourth/', fourth_class_view, name='fourth'),
    path('fifth/', fifth_class_view, name='fifth'),
    path('sixth/', sixth_class_view, name='sixth'),
    path('test/<int:classroom_id>/', get_test, name='get_test'),
    path('test/<int:classroom_id>/submit/', submit_test, name='submit_test'),
    path('first/<int:classroom_id>/', first_page, name='first_page'),
]