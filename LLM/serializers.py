from rest_framework import serializers
from .models import NewsArticle, NewsTemplate


class NewsArticleCreateSerializer(serializers.Serializer):
    news_type = serializers.CharField(max_length=255)
    place = serializers.CharField(max_length=255)
    source = serializers.CharField(max_length=255)
    event = serializers.CharField(max_length=255)
    date = serializers.CharField(max_length=255)
    participants = serializers.CharField(max_length=255)
    event_details = serializers.CharField(max_length=2000)
    creation_type = serializers.ChoiceField(choices=['template_only', 'openai_only', 'hybrid'], required=False)


class NewsArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsArticle
        fields = ['id', 'news_type', 'details']


class NewsTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsTemplate
        fields = ['id', 'news_type', 'templates']
