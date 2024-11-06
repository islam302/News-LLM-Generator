from django.urls import path
from .views import OpenaiAPIView, NewsDetailAPIView, AskOpenaiView

urlpatterns = [
    path('create/', OpenaiAPIView.as_view(), name='create_news'),
    path('create/<int:pk>/', NewsDetailAPIView.as_view(), name='news_detail'),
    path('ask_una/', AskOpenaiView.as_view({'post': 'question'}), name='ask_una')
]
