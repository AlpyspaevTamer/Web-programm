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
    path('lectures/<int:pk>/delete/', staff_member_required(delete_lecture), name='delete_lecture'),
    path('lectures/<int:pk>/edit/', staff_member_required(LectureUpdateView.as_view()), name='edit_lecture'),

    # URL для тестов
    path('tests/', TestListView.as_view(), name='test_list'),
    path('tests/add/', TestCreateView.as_view(), name='add_test'),
    path('tests/<int:pk>/', test_detail, name='test_detail'),
    path('tests/<int:test_id>/add-question/', add_question, name='add_question'),
    path('tests/<int:pk>/questions/', test_questions, name='test_questions'),
    path('tests/<int:pk>/take/', take_test, name='take_test'),
    path('tests/<int:pk>/results/<int:score>/', test_results, name='test_results'),
    path('tests/<int:pk>/delete/', staff_member_required(delete_test), name='delete_test'),
    path('tests/<int:pk>/enter-password/', enter_test_password, name='enter_test_password'),
    path('tests/<int:pk>/edit/', staff_member_required(edit_test), name='edit_test'),


    # Аутентификация
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', custom_logout, name='logout'),

    # Профиль
    path('profile/', profile_view, name='profile'),

    # Видеолекции
    path('video-lectures/', video_lecture_view, name='video_lectures'),
    path('video-lectures/add/', add_video_lecture_view, name='add_video_lecture'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)