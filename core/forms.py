from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.forms import inlineformset_factory
from .models import User, Lecture, Question, Answer, Test, Category, Tag, VideoLecture

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
    class Meta:
        model = Test
        fields = ['title', 'description', 'time_limit', 'password']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Название теста'
            }),
            'password': forms.PasswordInput(attrs={
                'class': 'form-control',
                'placeholder': 'Пароль (Необязательно)'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Описание теста'
            }),
            'time_limit': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Время на прохождение (минуты)'
            })
        }
        labels = {
            'time_limit': 'Лимит времени (мин)'
        }

class TestPasswordForm(forms.Form):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите пароль'
        }),
        label="Пароль"
    )


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['text', 'image']
        widgets = {
            'text': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Текст вопроса'  # Убрали лишний атрибут accept
            }),
            'image': forms.FileInput(attrs={  # Добавили виджет для изображения
                'class': 'hidden',
                'accept': 'image/*'
            })
        }

    def __init__(self, *args, **kwargs):
        self.test = kwargs.pop('test', None)
        super().__init__(*args, **kwargs)
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.test:
            instance.test = self.test
        if commit:
            instance.save()
            self.save_m2m()
        return instance
from django import forms
from django.forms import inlineformset_factory
from .models import Answer, Question

class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ['text', 'image', 'is_correct']
        widgets = {
            'text': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Введите текст ответа'
            }),
            'image': forms.FileInput(attrs={
                'class': 'hidden',
                'accept': 'image/*'
            }),
            'is_correct': forms.CheckboxInput(attrs={
                'class': 'form-check-input h-5 w-5 rounded-full border-2 cursor-pointer',
            })
        }
        labels = {
            'is_correct': 'Правильный ответ'
        }

class BaseAnswerFormSet(forms.BaseInlineFormSet):
    def clean(self):
        super().clean()
        # Проверка наличия хотя бы одного правильного ответа
        if any(self.errors):
            return
            
        correct_answers = 0
        for form in self.forms:
            if form.cleaned_data.get('is_correct', False):
                correct_answers += 1
        
        question_type = self.instance.question_type if self.instance else 'single'
        
        if question_type == 'single' and correct_answers != 1:
            raise forms.ValidationError("Должен быть ровно один правильный ответ для этого типа вопроса")
            
        if question_type == 'multiple' and correct_answers < 1:
            raise forms.ValidationError("Должен быть хотя бы один правильный ответ")
            
        if question_type == 'text' and correct_answers > 0:
            raise forms.ValidationError("Для текстовых вопросов не должно быть помеченных ответов")

AnswerFormSet = inlineformset_factory(
    Question,
    Answer,
    form=AnswerForm,
    formset=BaseAnswerFormSet,
    extra=5,
    min_num=5,
    max_num=5,
    validate_min=True,
    validate_max=True,
    can_delete=False,
    labels={
        'DELETE': 'Удалить ответ'
    }
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