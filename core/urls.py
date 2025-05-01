from django.urls import path
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.admin.views.decorators import staff_member_required
from .views import *


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home_view, name='home'),

    # URL для лекций
    path('lectures/', LectureListView.as_view(), name='lectures_list'),
    path('lectures/add/', staff_member_required(AddLectureView.as_view()), name='add_lecture'),
    path('lectures/<int:pk>/', LectureDetailView.as_view(), name='lecture_detail'),

    # URL для тестов
    path('tests/', test_list, name='test_list'),
    path('tests/add/', add_test, name='add_test'),
    path('tests/<int:pk>/', test_detail, name='test_detail'),  # Добавлен этот маршрут
    path('tests/<int:test_id>/add-question/', add_question, name='add_question'),
    path('tests/<int:pk>/questions/', test_questions, name='test_questions'),  # Рекомендую добавить
    path('tests/<int:pk>/take/', take_test, name='take_test'),
    path('tests/<int:pk>/results/<int:score>/', test_results, name='test_results'),
    path('tests/<int:pk>/delete/', staff_member_required(delete_test), name='delete_test'),

    # Аутентификация
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', custom_logout, name='logout'),

    # Профиль
    path('profile/', profile_view, name='profile'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)