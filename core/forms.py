from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.forms import inlineformset_factory
from .models import User, Lecture, Question, Answer, Test, Category, Tag, TestVariant, VideoLecture

class LectureForm(forms.ModelForm):
    description = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'rows': 3,
            'class': 'form-control',
            'placeholder': 'Описание (необязательно)'
        }),
        label="Описание"
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['content'].required = False
        self.fields['category'].required = False
        self.fields['tags'].required = False
        self.fields['grade'].initial = '1'
        
        if self.instance and self.instance.pk:
            self.fields['file'].required = False

    def clean_file(self):
        uploaded_file = self.cleaned_data.get('file')
        
        if self.instance and self.instance.pk:
            if not uploaded_file and self.instance.file:
                return self.instance.file
        
        if uploaded_file:
            if not uploaded_file.name.lower().endswith(('.doc', '.docx')):
                raise ValidationError("Только файлы формата .doc или .docx разрешены!")
            return uploaded_file
        
        if not self.instance or not self.instance.pk:
            raise ValidationError("Необходимо загрузить файл лекции")
        
        return uploaded_file

    class Meta:
        model = Lecture
        fields = ['title', 'description', 'content', 'image', 'file', 'grade', 'category', 'tags']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите название лекции'
            }),
            'content': forms.Textarea(attrs={
                'rows': 10, 
                'class': 'form-control',
                'placeholder': 'Дополнительный контент лекции'
            }),
            'file': forms.FileInput(attrs={
                'accept': '.doc,.docx', 
                'class': 'form-control'
            }),
            'image': forms.FileInput(attrs={
                'accept': 'image/*', 
                'class': 'form-control'
            }),
            'grade': forms.Select(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'tags': forms.SelectMultiple(attrs={
                'class': 'form-control',
                'data-placeholder': 'Выберите теги'
            }),
        }
        labels = {
            'title': 'Название лекции',
            'grade': 'Курс',
            'file': 'Файл лекции (DOC/DOCX)',
            'image': 'Обложка лекции',
            'content': 'Дополнительный контент',
            'category': 'Категория',
            'tags': 'Теги'
        }

class TestForm(forms.ModelForm):
    has_variants = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
            'id': 'has-variants-checkbox'
        }),
        label="Тест с вариантами"
    )

    class Meta:
        model = Test
        fields = ['title', 'description', 'subject', 'has_variants', 'time_limit']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Название теста'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Описание теста'
            }),
            'subject': forms.Select(attrs={'class': 'form-control'}),
            'time_limit': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Время на прохождение (минуты)'
            })
        }
        labels = {
            'subject': 'Предмет',
            'time_limit': 'Лимит времени (мин)'
        }

class TestVariantForm(forms.ModelForm):
    class Meta:
        model = TestVariant
        fields = ['name', 'description', 'order']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Название варианта'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Описание варианта'
            }),
            'order': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Порядковый номер'
            })
        }

TestVariantFormSet = inlineformset_factory(
    Test,
    TestVariant,
    form=TestVariantForm,
    extra=1,
    can_delete=True,
    min_num=1,
    validate_min=True
)

class QuestionForm(forms.ModelForm):
    QUESTION_TYPES = [
        ('single', 'Один правильный ответ'),
        ('multiple', 'Несколько правильных ответов'),
        ('text', 'Текстовый ответ'),
    ]

    question_type = forms.ChoiceField(
        choices=QUESTION_TYPES,
        initial='single',
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Тип вопроса"
    )

    class Meta:
        model = Question
        fields = ['text', 'question_type', 'variant', 'points']
        widgets = {
            'text': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Текст вопроса'
            }),
            'variant': forms.Select(attrs={'class': 'form-control'}),
            'points': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Баллы за вопрос',
                'min': 1
            })
        }

    def __init__(self, *args, **kwargs):
        test_id = kwargs.pop('test_id', None)
        super().__init__(*args, **kwargs)
        
        if test_id:
            self.fields['variant'].queryset = TestVariant.objects.filter(test_id=test_id)
        else:
            self.fields['variant'].queryset = TestVariant.objects.none()

class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ['text', 'is_correct', 'points']
        widgets = {
            'text': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Текст ответа'
            }),
            'is_correct': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
                'data-answer-type': 'correct'
            }),
            'points': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Баллы за ответ',
                'min': 0
            })
        }
        labels = {
            'is_correct': 'Правильный ответ',
            'points': 'Баллы'
        }

AnswerFormSet = inlineformset_factory(
    Question,
    Answer,
    form=AnswerForm,
    extra=2,
    min_num=1,
    validate_min=True,
    can_delete=True
)

class RegisterForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email'
        }),
        label="Электронная почта"
    )
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Логин'
        }),
        label="Имя пользователя"
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Пароль'
        }),
        label="Пароль"
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Подтверждение пароля'
        }),
        label="Подтверждение пароля"
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("Этот email уже используется")
        return email

class LoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Логин'
        }),
        label="Имя пользователя"
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Пароль'
        }),
        label="Пароль"
    )

class VideoLectureForm(forms.ModelForm):
    class Meta:
        model = VideoLecture
        fields = ['title', 'description', 'youtube_url', 'tags']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Название видеолекции'
            }),
            'description': forms.Textarea(attrs={
                'rows': 3,
                'class': 'form-control',
                'placeholder': 'Подробное описание видеолекции'
            }),
            'youtube_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://www.youtube.com/watch?v=...'
            }),
            'tags': forms.SelectMultiple(attrs={
                'class': 'form-control',
                'data-placeholder': 'Выберите теги'
            })
        }
        labels = {
            'youtube_url': 'YouTube ссылка',
        }
    
    def clean_youtube_url(self):
        url = self.cleaned_data.get('youtube_url')
        if not ('youtube.com/watch?v=' in url or 'youtu.be/' in url):
            raise ValidationError("Пожалуйста, введите корректную ссылку на YouTube видео")
        return url