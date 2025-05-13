from django.db import models
from django.core.validators import FileExtensionValidator
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.core.validators import MinValueValidator

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
        ('1', '1 курс'),
        ('2', '2 курс'),
    ]

    is_published = models.BooleanField(default=True, verbose_name="Опубликовано")
    title = models.CharField("Название", max_length=200)
    description = models.TextField("Описание", blank=True, default="")
    content = models.TextField("Контент", blank=True)
    image = models.ImageField("Обложка", upload_to='lectures/', null=True, blank=True)
    file = models.FileField(
        "Файл лекции",
        upload_to=lecture_file_path,
        validators=[FileExtensionValidator(['doc', 'docx'])],
        default='default.docx'
    )
    grade = models.CharField("Класс", max_length=5, choices=GRADE_CHOICES, default='1')
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
    description = models.TextField(verbose_name="Описание", blank=True)
    password = models.CharField(
        max_length=100, 
        blank=True, 
        null=True, 
        verbose_name="Пароль для доступа"
    )
    time_limit = models.PositiveIntegerField(
        verbose_name="Лимит времени (мин)", 
        default=30,
        null=True,
        blank=True
    )
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_published = models.BooleanField(default=True, verbose_name="Опубликован")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Тест"
        verbose_name_plural = "Тесты"
        ordering = ['-created_at']

class Question(models.Model):
    QUESTION_TYPES = [
        ('single', 'Один правильный ответ'),
        ('multiple', 'Несколько правильных ответов'),
        ('text', 'Текстовый ответ'),
    ]

    test = models.ForeignKey(
        Test,
        on_delete=models.CASCADE,
        related_name='questions',
        verbose_name="Тест"
    )
    text = models.TextField(verbose_name="Текст вопроса")
    image = models.ImageField(
        upload_to='questions/images/',
        blank=True,
        null=True,
        verbose_name="Изображение"
    )
    question_type = models.CharField(
        max_length=10,
        choices=QUESTION_TYPES,
        default='single',
        verbose_name="Тип вопроса"
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name="Порядок",
        help_text="Порядок отображения (0 - первый)"
    )
    points = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        verbose_name="Баллы",
        blank=True
    )
    explanation = models.TextField(
        verbose_name="Объяснение",
        blank=True
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания"
    )

    def __str__(self):
        return f"Вопрос {self.id} ({self.test.title})"

    @property
    def correct_answers_count(self):
        return self.answers.filter(is_correct=True).count()

    class Meta:
        verbose_name = "Вопрос"
        verbose_name_plural = "Вопросы"
        ordering = ['order']
        indexes = [
            models.Index(fields=['order', 'test']),
        ]
    
    image = models.ImageField(upload_to='questions/', blank=True, null=True)

class Answer(models.Model):
    question = models.ForeignKey(
        Question, 
        on_delete=models.CASCADE, 
        related_name='answers',
        verbose_name="Вопрос"
    )
    text = models.CharField(
        max_length=500, 
        verbose_name="Текст ответа"
    )
    image = models.ImageField(
        upload_to='answers/images/',
        blank=True,
        null=True,
        verbose_name="Изображение"
    )
    is_correct = models.BooleanField(
        default=False, 
        verbose_name="Правильный ответ"
    )
    order = models.PositiveIntegerField(
        default=0, 
        verbose_name="Порядок"
    )

    def __str__(self):
        return f"Ответ {self.id} (вопрос {self.question.id})"

    class Meta:
        verbose_name = "Ответ"
        verbose_name_plural = "Ответы"
        ordering = ['order']

    image = models.ImageField(upload_to='answers/', blank=True, null=True)

class TestResult(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    test = models.ForeignKey(Test, on_delete=models.CASCADE)
    score = models.PositiveIntegerField(verbose_name="Баллы")
    max_score = models.PositiveIntegerField(verbose_name="Максимальный балл")
    completed_at = models.DateTimeField(auto_now_add=True)
    details = models.JSONField(verbose_name="Детали результатов", default=dict)

    def __str__(self):
        return f"Результат {self.user} по тесту {self.test}"

    class Meta:
        verbose_name = "Результат теста"
        verbose_name_plural = "Результаты тестов"
        ordering = ['-completed_at']

class VideoLecture(models.Model):
    title = models.CharField("Название", max_length=200)
    description = models.TextField("Описание", blank=True)
    youtube_url = models.URLField("Ссылка на YouTube")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField("Дата создания", auto_now_add=True)
    updated_at = models.DateTimeField("Дата обновления", auto_now=True)
    views = models.PositiveIntegerField("Просмотры", default=0)
    duration = models.PositiveIntegerField("Длительность (сек)", default=0)
    is_published = models.BooleanField("Опубликовано", default=True)
    tags = models.ManyToManyField(Tag, blank=True)

    def __str__(self):
        return self.title
    
    def extract_youtube_id(self):
        """Извлекает ID видео из YouTube URL"""
        url = self.youtube_url
        if 'youtube.com/watch?v=' in url:
            return url.split('v=')[1].split('&')[0]
        elif 'youtu.be/' in url:
            return url.split('youtu.be/')[1]
        return None
    
    class Meta:
        verbose_name = "Видеолекция"
        verbose_name_plural = "Видеолекции"
        ordering = ['-created_at']

from django.contrib.auth.decorators import user_passes_test

def admin_required(view_func):
    """Декоратор для проверки прав администратора"""
    return user_passes_test(
        lambda u: u.is_active and u.is_staff,
        login_url='/admin/login/'
    )(view_func)