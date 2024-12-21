from rest_framework import serializers
from .models import NewsArticle, NewsTemplate


class NewsArticleCreateSerializer(serializers.Serializer):
    news_type = serializers.CharField(max_length=255)
    place = serializers.CharField(max_length=255, required=False)
    source = serializers.CharField(max_length=255, required=False)
    event = serializers.CharField(max_length=255, required=False)
    date = serializers.DateField(required=False)
    participants = serializers.CharField(max_length=255, required=False)
    event_details = serializers.CharField(max_length=1000, required=False)
    additional_variables = serializers.DictField(required=False)  # Must be DictField
    creation_type = serializers.ChoiceField(choices=["template_only", "openai_only", "hybrid"], default="template_only")
    template_id = serializers.IntegerField(required=False)  # ????? template_id ???? ???????


class NewsArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsArticle
        fields = ['id', 'news_type', 'details']


class NewsTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsTemplate
        fields = ['id', 'news_type', 'templates']
