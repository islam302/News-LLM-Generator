from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import NewsTemplateViewSet, NewsDetailAPIView

router = DefaultRouter()
router.register(r'manage-templates', NewsTemplateViewSet, basename='news-template')
router.register('news', NewsDetailAPIView, basename='news-detail')

urlpatterns = [
    # path('news/<int:pk>/', NewsDetailAPIView.as_view(), name='news-detail'),
] + router.urls
