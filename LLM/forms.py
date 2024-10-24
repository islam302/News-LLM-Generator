from django import forms
from .models import NewsArticle

class NewsArticleForm(forms.ModelForm):
    class Meta:
        model = NewsArticle
        fields = ['news_type', 'title', 'details']
        widgets = {
            'news_type': forms.Select(attrs={'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'details': forms.TextInput(attrs={'class': 'form-control'}),
        }
