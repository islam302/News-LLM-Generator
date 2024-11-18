from rest_framework import serializers
from .models import NewsArticle, NewsTemplate


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
        fields = ['id', 'news_type', 'details']


class NewsTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsTemplate
        fields = ['id', 'news_type', 'templates']
