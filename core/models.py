from django.db import models
from django.core.validators import FileExtensionValidator
from docx import Document
from django.core.exceptions import PermissionDenied
from django.contrib.auth.models import AbstractUser
from django.conf import settings

def lecture_file_path(instance, filename):
    return f'lectures/{instance.id}/{filename}'

class User(AbstractUser):
    bio = models.TextField(blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    
    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username

class Category(models.Model):
    name = models.CharField("Категория", max_length=100)
    icon = models.CharField("Иконка", max_length=50, blank=True)

    def __str__(self):
        return self.name

class Tag(models.Model):
    name = models.CharField("Тег", max_length=50)

    def __str__(self):
        return self.name

class Subject(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название предмета")
    
    def __str__(self):
        return self.name

class Lecture(models.Model):
    GRADE_CHOICES = [
        ('1-4', '1-4 класс'),
        ('5-6', '5-6 класс'),
        ('7-9', '7-9 класс'),
        ('10-11', '10-11 класс')
    ]

    is_published = models.BooleanField(default=True, verbose_name="Опубликовано")
    title = models.CharField("Название", max_length=200)
    description = models.TextField("Описание", default="Базовое описание")
    content = models.TextField("Контент", blank=True)
    image = models.ImageField("Обложка", upload_to='lectures/', null=True, blank=True)
    file = models.FileField(
        "Файл лекции",
        upload_to=lecture_file_path,
        validators=[FileExtensionValidator(['doc', 'docx'])],
        default='default.docx'
    )
    grade = models.CharField("Класс", max_length=5, choices=GRADE_CHOICES, default='5-6')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Автор")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    tags = models.ManyToManyField(Tag, blank=True)
    views = models.PositiveIntegerField("Просмотры", default=0)
    created_at = models.DateTimeField("Дата создания", auto_now_add=True)
    updated_at = models.DateTimeField("Дата обновления", auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Лекция"
        verbose_name_plural = "Лекции"
        ordering = ['-created_at']

class Test(models.Model):
    title = models.CharField(max_length=200, verbose_name="Название теста")
    created_at = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    time_limit = models.PositiveIntegerField("Лимит времени (мин)", default=30, null=True, blank=True)
    
    def __str__(self):
        return self.title

class Question(models.Model):
    test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField(verbose_name="Текст вопроса")
    
    def __str__(self):
        return f"Вопрос {self.id} для теста {self.test.title}"
    
    @property
    def correct_answers_count(self):
        return self.answers.filter(is_correct=True).count()

class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    text = models.CharField(max_length=200, verbose_name="Текст ответа")
    is_correct = models.BooleanField(default=False, verbose_name="Правильный ответ")
    
    def __str__(self):
        return f"Ответ {self.id} для вопроса {self.question.id}"
    


from django.contrib.auth.decorators import user_passes_test
def admin_required(view_func):
    return user_passes_test(
        lambda u: u.is_active and u.is_staff,
        login_url='/admin/login/'
    )(view_func)