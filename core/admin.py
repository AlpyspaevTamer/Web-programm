from django.contrib import admin
from .models import Question, Answer, Test
from django.utils.html import format_html

class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 3
    fields = ['text', 'is_correct']

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    inlines = [AnswerInline]
    list_display = ('text', 'image_preview', 'test')  # убрал 'difficulty', если его нет
    list_filter = ('test',)
    readonly_fields = ('image_preview',)
    fields = ('test', 'text', 'image')

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 100px;"/>', obj.image.url)
        return "-"
    image_preview.short_description = "Превью"

@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ('text', 'question', 'is_correct')
    list_filter = ('is_correct',)

@admin.register(Test)
class TestAdmin(admin.ModelAdmin):
    list_display = ('title', 'author')
