from rest_framework import serializers
from .models import NewsArticle

class NewsArticleCreateSerializer(serializers.Serializer):
    news_type = serializers.CharField(max_length=100)
    place = serializers.CharField(max_length=100)
    source = serializers.CharField(max_length=100)
    event = serializers.CharField(max_length=100)
    date = serializers.CharField(max_length=50)
    participants = serializers.CharField(max_length=200)
    event_details = serializers.CharField()

class NewsArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsArticle
        fields = ['id', 'news_type', 'details']  # Only model fields needed for display
