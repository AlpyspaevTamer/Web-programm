from django.views.generic import  DetailView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django_filters.views import FilterView
from .filters import LectureFilter
from .utils import docx_to_html  
from django.contrib.auth import login, logout
from .forms import RegisterForm, LoginForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from .models import Test, Subject, Tag
from .models import Lecture, Category, Tag, Test, Question, Answer
from .forms import LectureForm, TestForm, QuestionForm, AnswerForm, AnswerFormSet
from django.contrib import messages
from django.db import models

class LectureListView(LoginRequiredMixin, FilterView):
    model = Lecture  # Указываем модель
    filterset_class = LectureFilter  # Используем ваш фильтр
    template_name = 'lectures.html'
    context_object_name = 'lectures'
    paginate_by = 12
    login_url = '/login/'

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(is_published=True).order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'categories': Category.objects.all(),
            'tags': Tag.objects.all(),
            'search_query': self.request.GET.get('search', '')
        })
        return context

class LectureDetailView(DetailView):
    model = Lecture
    template_name = 'lectures/detail.html'
    
    def get(self, request, *args, **kwargs):
        obj = self.get_object()
        obj.views += 1
        obj.save()
        return super().get(request, *args, **kwargs)

class AddLectureView(LoginRequiredMixin, CreateView):
    model = Lecture
    form_class = LectureForm
    template_name = 'lectures/add.html'
    success_url = reverse_lazy('lectures_list')
    login_url = '/login/'

    def test_func(self):
        return self.request.user.is_staff
    
    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)
    
    def grade_selection(request):
        context = {
            'grade_range': range(1, 12),
            'recommended_grade': 6,
        }
        return render(request, 'grade_selection.html', context)
    
    def post(self, request, *args, **kwargs):
        print("POST data:", request.POST)  # Проверяем текстовые поля
        print("FILES data:", request.FILES)  # Проверяем файлы
        return super().post(request, *args, **kwargs)

class LectureDetailView(DetailView):
    model = Lecture
    template_name = 'lectures/lecture_detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        lecture = self.object
        
        if lecture.file:  # Если есть DOCX файл
            try:
                # Конвертируем DOCX в HTML с сохранением форматирования
                context['lecture_content'] = docx_to_html(lecture.file.path)
            except Exception as e:
                context['lecture_content'] = f"<p>Ошибка загрузки содержимого: {str(e)}</p>"
        
        return context
    


def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = RegisterForm()
    return render(request, 'register.html', {'form': form})  # Прямой путь

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})  # Прямой путь

def home_view(request):
    return render(request, 'home.html')

def custom_logout(request):
    logout(request)
    return redirect('home')

@login_required(login_url='/login/')
def home_view(request):
    return render(request, 'home.html')

@login_required(login_url='/login/')
def profile_view(request):
    return render(request, 'profile.html')








# -----------------------------------------------------------Тут я делаю тестирование--------------------------------------------------------


from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Test, Subject, Tag, Question, Answer
from .forms import TestForm, QuestionForm, AnswerFormSet

def test_list(request):
    tests = Test.objects.annotate(questions_count=models.Count('questions'))
    subjects = Subject.objects.all()
    
    # Фильтрация
    if 'search' in request.GET:
        tests = tests.filter(title__icontains=request.GET['search'])
    
    if 'subject' in request.GET and request.GET['subject']:
        tests = tests.filter(subject_id=request.GET['subject'])
    
    context = {
        'tests': tests,
        'subjects': subjects,
    }
    return render(request, 'test/index.html', context)

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import TestForm, QuestionForm, AnswerFormSet
from .models import Test

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import TestForm, QuestionForm, AnswerFormSet

@login_required
def add_test(request):
    if request.method == 'POST':
        test_form = TestForm(request.POST)
        question_form = QuestionForm(request.POST)
        formset = AnswerFormSet(request.POST)
        
        if all([
            test_form.is_valid(),
            question_form.is_valid(),
            formset.is_valid()
        ]):
            test = test_form.save(commit=False)
            test.author = request.user
            test.save()
            
            question = question_form.save(commit=False)
            question.test = test
            question.save()
            
            for form in formset:
                answer = form.save(commit=False)
                answer.question = question
                answer.save()
            
            messages.success(request, 'Тест создан!')
            return redirect('add_question', test_id=test.id)
    
    else:
        test_form = TestForm()
        question_form = QuestionForm()
        formset = AnswerFormSet()
    
    return render(request, 'test/add_test.html', {
        'test_form': test_form,
        'question_form': question_form,
        'formset': formset
    })

from django.shortcuts import redirect

def add_question(request, test_id):
    test = get_object_or_404(Test, id=test_id)
    
    if request.method == 'POST':
        question_form = QuestionForm(request.POST)
        formset = AnswerFormSet(request.POST)
        
        if question_form.is_valid() and formset.is_valid():
            question = question_form.save(commit=False)
            question.test = test
            question.save()
            
            # Сохраняем ответы
            instances = formset.save(commit=False)
            for instance in instances:
                instance.question = question
                instance.save()
            
            # Проверяем, какая кнопка была нажата
            if 'add_another' in request.POST:
                return redirect('add_question', test_id=test.id)
            else:
                return redirect('test_detail', pk=test.id)  # Или другой URL
            
    else:
        question_form = QuestionForm()
        formset = AnswerFormSet()
    
    return render(request, 'test/add_question.html', {
        'test': test,
        'question_form': question_form,
        'formset': formset,
    })

from django.contrib.auth.decorators import login_required, user_passes_test

def is_teacher(user):
    return user.groups.filter(name='Teachers').exists() or user.is_staff

@login_required
def test_detail(request, pk):
    test = get_object_or_404(Test, pk=pk)
    
    if is_teacher(request.user):
        # Для учителей показываем детали с правильными ответами
        questions = test.questions.prefetch_related('answers').all()
        for question in questions:
            question.correct_count = question.answers.filter(is_correct=True).count()
        
        return render(request, 'test/test_detail.html', {
            'test': test,
            'questions': questions,
            'show_answers': True,
            'is_teacher': True
        })
    else:
        # Для студентов перенаправляем на страницу прохождения теста
        return redirect('take_test', pk=test.id)

def test_questions(request, pk):
    test = get_object_or_404(Test, pk=pk)
    return render(request, 'test/questions.html', {'test': test})


@login_required
def take_test(request, pk):
    if is_teacher(request.user):
        return redirect('test_detail', pk=pk)
    test = get_object_or_404(Test, pk=pk)
    
    if request.method == 'POST':
        score = 0
        total_questions = test.questions.count()
        
        # Проверяем каждый вопрос
        for question in test.questions.all():
            answer_id = request.POST.get(f'question_{question.id}')
            if answer_id:
                try:
                    answer = Answer.objects.get(id=answer_id, question=question)
                    if answer.is_correct:
                        score += 1
                except Answer.DoesNotExist:
                    pass
        
        # Сохраняем результаты (можно добавить модель TestResult для хранения)
        messages.success(request, f'Вы набрали {score} из {total_questions} баллов!')
        return redirect('test_results', pk=test.id, score=score)
    
    return render(request, 'test/take_test.html', {'test': test})

@login_required
def test_results(request, pk, score):
    test = get_object_or_404(Test, pk=pk)
    score = int(score)
    total = test.questions.count()
    percentage = int((score / total) * 100) if total > 0 else 0
    
    return render(request, 'test/results.html', {
        'test': test,
        'score': score,
        'percentage': percentage
    })

from .models import *
@admin_required
def delete_test(request, pk):
    test = get_object_or_404(Test, pk=pk)
    test.delete()
    messages.success(request, 'Тест успешно удален')
    return redirect('test_list')