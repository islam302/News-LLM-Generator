from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import NewsTemplateViewSet, OpenaiAPIView, NewsDetailAPIView

router = DefaultRouter()
router.register(r'manage-templates', NewsTemplateViewSet, basename='news-template')
router.register('news', NewsDetailAPIView, basename='news-detail')

urlpatterns = [
    path('create/', OpenaiAPIView.as_view(), name='generate-news'),
    # path('news/<int:pk>/', NewsDetailAPIView.as_view(), name='news-detail'),
] + router.urls
