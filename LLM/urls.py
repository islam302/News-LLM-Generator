from django.urls import path
from .views import OpenaiAPIView, NewsDetailAPIView

urlpatterns = [
    path('create/', OpenaiAPIView.as_view(), name='create_news'),
    path('create/<int:pk>/', NewsDetailAPIView.as_view(), name='news_detail'),  # For GET requests
]
