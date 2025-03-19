from django.shortcuts import render
from django.shortcuts import render, get_object_or_404
from .models import *
from django.http import JsonResponse
from .models import Classroom, Question, Answer, TestResult

def home_view(request):
    return render(request, "home.html")



def get_test(request, classroom_id):
    classroom = get_object_or_404(Classroom, id=classroom_id)
    questions = Question.objects.filter(classroom=classroom).prefetch_related('answers')
    data = {
        "classroom": classroom.name,
        "questions": [
            {
                "id": q.id,
                "text": q.text,
                "answers": [{"id": a.id, "text": a.text} for a in q.answers.all()]
            }
            for q in questions
        ]
    }
    return JsonResponse(data)

def submit_test(request, classroom_id):
    if request.method == "POST":
        correct_answers = 0
        total_questions = Question.objects.filter(classroom_id=classroom_id).count()

        for question in Question.objects.filter(classroom_id=classroom_id):
            selected_answer_id = request.POST.get(f'question_{question.id}')
            if selected_answer_id:
                selected_answer = get_object_or_404(Answer, id=selected_answer_id)
                if selected_answer.is_correct:
                    correct_answers += 1

        score = round((correct_answers / total_questions) * 100, 2) if total_questions > 0 else 0

        return JsonResponse({
            "message": "Test submitted",
            "score": score,
            "correct_answers": correct_answers,
            "total_questions": total_questions
        })

def first_page(request, classroom_id):
    classroom_id = 1
    questions = Question.objects.filter(classroom_id=classroom_id).prefetch_related('answers')
    return render(request, 'first.html', {'questions': questions, 'classroom_id': classroom_id})

def second_class_view(request):
    classroom_id = 2
    questions = Question.objects.filter(classroom_id=classroom_id)
    return render(request, "second.html", {"questions": questions, "classroom_id": classroom_id})

def third_class_view(request):
    questions = Question.objects.filter(classroom_id=3)
    return render(request, "third.html", {"questions": questions})

def fourth_class_view(request):
    questions = Question.objects.filter(classroom_id=4)
    return render(request, "fourth.html", {"questions": questions})

def fifth_class_view(request):
    questions = Question.objects.filter(classroom_id=5)
    return render(request, "fifth.html", {"questions": questions})

def sixth_class_view(request):
    questions = Question.objects.filter(classroom_id=6)
    return render(request, "sixth.html", {"questions": questions})

