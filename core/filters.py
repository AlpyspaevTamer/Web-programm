from django.db.models import Q
import django_filters
from .models import Lecture

class LectureFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method='filter_search')
    
    class Meta:
        model = Lecture
        fields = ['category', 'tags', 'grade']

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(title__icontains=value) | 
            Q(description__icontains=value) |
            Q(content__icontains=value)
        )