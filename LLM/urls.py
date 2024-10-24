from django.urls import path
from . import views

news = views.OpenaiView()
urlpatterns = [
    path('create/', news.create_news, name='create_news'),
    path('<int:pk>/', news.news_detail, name='news_detail'),
]
