# urls.py
from django.urls import path
from .views import NewsDetailAPIView, OpenaiAPIView

urlpatterns = [
    # URL pattern for creating news articles using OpenAI
    path('create/', OpenaiAPIView.as_view(), name='openai_create'),

    # URL patterns for News Detail View
    path('news/', NewsDetailAPIView.as_view({'get': 'list', 'post': 'create'}), name='news_list'),
    path('news/<int:pk>/', NewsDetailAPIView.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}),
         name='news_detail'),
]
