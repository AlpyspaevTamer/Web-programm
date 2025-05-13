from django.views.generic import DetailView, CreateView, UpdateView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django_filters.views import FilterView
from .filters import LectureFilter
from .utils import docx_to_html  
from django.contrib.auth import login, logout
from .forms import (RegisterForm, LoginForm, LectureForm, TestForm, 
                   QuestionForm, AnswerFormSet, VideoLectureForm,
                   )
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, get_object_or_404, redirect
from .models import (Lecture, Category, Tag, Test, Question, 
                    Answer, VideoLecture, Subject)
from django.contrib import messages
from django.db import models
from django.contrib.admin.views.decorators import staff_member_required

# Лекции
class LectureListView(LoginRequiredMixin, FilterView):
    model = Lecture
    filterset_class = LectureFilter
    template_name = 'lectures/lectures.html'
    context_object_name = 'lectures'
    paginate_by = 12
    login_url = '/login/'

    def get_queryset(self):
        return super().get_queryset().filter(is_published=True).order_by('-created_at')
    
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
    template_name = 'lectures/lecture_detail.html'
    
    def get(self, request, *args, **kwargs):
        obj = self.get_object()
        obj.views += 1
        obj.save()
        return super().get(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        lecture = self.object
        
        if lecture.file:
            try:
                context['lecture_content'] = docx_to_html(lecture.file.path)
            except Exception as e:
                context['lecture_content'] = f"<p>Ошибка загрузки содержимого: {str(e)}</p>"
        
        context['request'] = self.request
        return context

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
        messages.success(self.request, 'Лекция успешно создана!')
        return super().form_valid(form)

class LectureUpdateView(LoginRequiredMixin, UpdateView):
    model = Lecture
    form_class = LectureForm
    template_name = 'lectures/add.html'
    success_url = reverse_lazy('lectures_list')
    login_url = '/login/'

    def test_func(self):
        return self.request.user.is_staff

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['editing'] = True
        return context

    def form_valid(self, form):
        form.instance.author = self.request.user
        messages.success(self.request, 'Лекция успешно обновлена!')
        return super().form_valid(form)

@staff_member_required
def delete_lecture(request, pk):
    lecture = get_object_or_404(Lecture, pk=pk)
    if request.method == 'POST':
        lecture.delete()
        messages.success(request, 'Лекция успешно удалена')
    return redirect('lectures_list')

# Аутентификация
def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = RegisterForm()
    return render(request, 'user/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
    else:
        form = LoginForm()
    return render(request, 'user/login.html', {'form': form})

def custom_logout(request):
    logout(request)
    return redirect('home')

@login_required(login_url='/login/')
def home_view(request):
    return render(request, 'base/home.html')

@login_required(login_url='/login/')
def profile_view(request):
    return render(request, 'user/profile.html')

# Тесты
def is_teacher(user):
    return user.groups.filter(name='Teachers').exists() or user.is_staff

class TestListView(ListView):
    model = Test
    template_name = 'test/index.html'
    context_object_name = 'tests'
    
    def get_queryset(self):
        queryset = super().get_queryset().annotate(
            questions_count=models.Count('questions')
        )
        if 'search' in self.request.GET:
            queryset = queryset.filter(title__icontains=self.request.GET['search'])
        return queryset

class TestCreateView(LoginRequiredMixin, CreateView):
    model = Test
    form_class = TestForm
    template_name = 'test/add_test.html'
    success_url = reverse_lazy('test_list')

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.author = self.request.user
        self.object.save()
        messages.success(self.request, 'Тест успешно создан!')
        return redirect('add_question', test_id=self.object.id)

class TestUpdateView(LoginRequiredMixin, UpdateView):
    model = Test
    form_class = TestForm
    template_name = 'test/add_test.html'
    success_url = reverse_lazy('test_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['variant_formset'] = TestVariantFormSet(
                self.request.POST, 
                instance=self.object
            )
        else:
            context['variant_formset'] = TestVariantFormSet(instance=self.object)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        variant_formset = context['variant_formset']
        
        if form.cleaned_data['has_variants']:
            if not variant_formset.is_valid():
                return self.render_to_response(self.get_context_data(form=form))
            
            self.object = form.save()
            variant_formset.instance = self.object
            variant_formset.save()
        else:
            # Удаляем все варианты, если галочка снята
            self.object.variants.all().delete()
            self.object = form.save()
        
        messages.success(self.request, 'Тест успешно обновлен!')
        return super().form_valid(form)

@login_required
def add_question(request, test_id):
    test = get_object_or_404(Test, id=test_id)
    
    if request.method == 'POST':
        question_form = QuestionForm(request.POST, request.FILES)
        formset = AnswerFormSet(request.POST, request.FILES)

        if question_form.is_valid() and formset.is_valid():
            question = question_form.save(commit=False)
            question.test = test
            question.save()
            
            # Проверка правильных ответов
            has_correct = any(form.cleaned_data.get('is_correct') for form in formset)
            
            if not has_correct:
                messages.error(request, 'Отметьте хотя бы один правильный ответ!')
                return render(request, 'test/add_question.html', {
                    'test': test,
                    'question_form': question_form,
                    'formset': formset,
                })

            # Сохраняем все 5 ответов
            for form in formset:
                answer = form.save(commit=False)
                answer.question = question
                answer.save()

            messages.success(request, 'Вопрос успешно сохранён!')
            
            if 'add_another' in request.POST:
                return redirect('add_question', test_id=test.id)
            return redirect('test_detail', pk=test.id)
    else:
        question_form = QuestionForm()
        formset = AnswerFormSet(queryset=Answer.objects.none())
    
    return render(request, 'test/add_question.html', {
        'test': test,
        'question_form': question_form,
        'formset': formset,
    })


@login_required
def test_detail(request, pk):
    test = get_object_or_404(Test, pk=pk)
    
    if is_teacher(request.user):
        questions = test.questions.prefetch_related('answers')
        for question in questions:
            question.correct_count = question.answers.filter(is_correct=True).count()
        
        return render(request, 'test/test_detail.html', {
            'test': test,
            'questions': questions,
            'show_answers': True,
            'is_teacher': True
        })
    return redirect('take_test', pk=test.id)

@login_required
def select_variant(request, test_id):
    test = get_object_or_404(Test, pk=test_id)
    if not test.has_variants:
        return redirect('take_test', pk=test_id)
    
    if request.method == 'POST':
        variant_id = request.POST.get('variant')
        if variant_id:
            return redirect('take_test_variant', pk=test_id, variant_id=variant_id)
    
    return render(request, 'test/select_variant.html', {
        'test': test,
        'variants': test.variants.all()
    })

@login_required
def take_test(request, pk):
    if is_teacher(request.user):
        return redirect('test_detail', pk=pk)
    
    test = get_object_or_404(Test, pk=pk)
    
    # Проверка пароля
    if test.password and not request.session.get(f'test_{test.id}_unlocked'):
        return redirect('enter_test_password', pk=test.id)
    
    questions = test.questions.all()
    
    if request.method == 'POST':
        score = 0
        total_questions = questions.count()
        
        for question in questions:
            answer_id = request.POST.get(f'question_{question.id}')
            if answer_id:
                try:
                    answer = Answer.objects.get(id=answer_id, question=question)
                    if answer.is_correct:
                        score += 1
                except Answer.DoesNotExist:
                    pass
        
        messages.success(request, f'Вы набрали {score} из {total_questions} баллов!')
        return redirect('test_results', pk=test.id, score=score)
    
    return render(request, 'test/take_test.html', {
        'test': test,
        'questions': questions
    })

def enter_test_password(request, pk):
    test = get_object_or_404(Test, pk=pk)
    if request.method == 'POST':
        entered_password = request.POST.get('password')
        if entered_password == test.password:
            request.session[f'test_{test.id}_unlocked'] = True
            return redirect('take_test', pk=pk)
        else:
            messages.error(request, 'Неверный пароль!')
    return render(request, 'test/enter_password.html', {'test': test})

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

@staff_member_required
def delete_test(request, pk):
    test = get_object_or_404(Test, pk=pk)
    test.delete()
    messages.success(request, 'Тест успешно удален')
    return redirect('test_list')

# Видеолекции
def video_lecture_view(request):
    lectures = VideoLecture.objects.all().order_by('-created_at')
    return render(request, 'video/videolecture.html', {'lectures': lectures})

@login_required
def add_video_lecture_view(request):
    if request.method == 'POST':
        form = VideoLectureForm(request.POST)
        if form.is_valid():
            lecture = form.save(commit=False)
            lecture.author = request.user
            lecture.save()
            form.save_m2m()  # Для сохранения тегов
            messages.success(request, 'Видеолекция успешно добавлена!')
            return redirect('video_lectures')
    else:
        form = VideoLectureForm()
    
    return render(request, 'video/add_video_lecture.html', {'form': form})

@login_required
def test_questions(request, pk):
    test = get_object_or_404(Test, pk=pk)
    questions = test.questions.all()
    return render(request, 'test/questions.html', {
        'test': test,
        'questions': questions,
    })


from django.forms import inlineformset_factory
from .models import Test, Question, Answer
from .forms import TestForm, AnswerForm
@staff_member_required
def edit_test(request, pk):
    test = get_object_or_404(Test, pk=pk)
    
    # Проверка авторства
    if not (request.user.is_staff or request.user == test.author):
        raise PermissionDenied

    # Создаем формсеты
    QuestionFormSet = inlineformset_factory(
        Test,
        Question,
        fields=('text', 'image', 'question_type', 'points'),
        extra=0,
        can_delete=True
    )
    
    AnswerFormSet = inlineformset_factory(
        Question,
        Answer,
        form=AnswerForm,
        extra=0,
        min_num=5,
        max_num=5,
        can_delete=False
    )

    if request.method == 'POST':
        test_form = TestForm(request.POST, instance=test)
        question_formset = QuestionFormSet(
            request.POST, 
            request.FILES, 
            instance=test,
            prefix='questions'
        )
        
        if test_form.is_valid() and question_formset.is_valid():
            test_form.save()
            questions = question_formset.save(commit=False)
            
            # Сохраняем вопросы и ответы
            for question in questions:
                question.save()
                answer_formset = AnswerFormSet(
                    request.POST,
                    request.FILES,
                    instance=question,
                    prefix=f'answers_{question.id}'
                )
                if answer_formset.is_valid():
                    answer_formset.save()
            
            messages.success(request, 'Тест успешно обновлен!')
            return redirect('test_detail', pk=test.pk)
    
    else:
        test_form = TestForm(instance=test)
        question_formset = QuestionFormSet(instance=test, prefix='questions')
        
        # Инициализация формсетов ответов
        for question in test.questions.all():
            question.answer_formset = AnswerFormSet(
                instance=question,
                prefix=f'answers_{question.id}'
            )

    return render(request, 'test/edit_test.html', {
        'test': test,
        'test_form': test_form,
        'question_formset': question_formset,
    })