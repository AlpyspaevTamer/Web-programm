from django.contrib import admin
from .models import Question, Answer, TestResult

class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 4  # Показывать 4 поля для ответов по умолчанию

class QuestionAdmin(admin.ModelAdmin):
    inlines = [AnswerInline]

admin.site.register(Question, QuestionAdmin)
admin.site.register(TestResult)