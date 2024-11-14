from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from django.urls import reverse
from .models import NewsArticle
from .serializers import NewsArticleCreateSerializer, NewsArticleSerializer
import openai
import os
from dotenv import load_dotenv

class OpenaiAPIView(APIView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        load_dotenv()
        openai.api_key = os.getenv('OPENAI_API_KEY')

    def generate_news_content(self, news_type, place, source, event, date, participants, event_details):
        prompt = f"""
        أريدك أن تساعدني في تحرير خبر.

        تصنيف الخبر: '{news_type}'
        - المكان: '{place}'
        - المصدر: '{source}'
        - الحدث: '{event}'
        - اليوم والتاريخ: '{date}'
        - المشاركون: '{participants}'
        - تفاصيل الحدث المتوفرة: '{event_details}'

        يرجى كتابة خبر يشمل مقدمة واضحة، تفاصيل دقيقة حول الخبر، أهمية الموضوع، وآثار التعاون بين الأطراف المعنية. يجب أن يكون المحتوى غنيًا وشاملاً ويجيب على الأسئلة الأساسية لضمان كمال الخبر.
        """

        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300,
            temperature=0.7
        )

        content = response.choices[0].message['content'].strip()
        return content

    def post(self, request):
        serializer = NewsArticleCreateSerializer(data=request.data)
        if serializer.is_valid():
            news_type = serializer.validated_data['news_type']
            place = serializer.validated_data['place']
            source = serializer.validated_data['source']
            event = serializer.validated_data['event']
            date = serializer.validated_data['date']
            participants = serializer.validated_data['participants']
            event_details = serializer.validated_data['event_details']

            # Generate the content using OpenAI
            generated_content = self.generate_news_content(
                news_type, place, source, event, date, participants, event_details
            )

            # Save to the database
            news_article = NewsArticle.objects.create(
                news_type=news_type,
                details=generated_content
            )

            # Return the response with the created news article's details
            response_serializer = NewsArticleSerializer(news_article)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class NewsDetailAPIView(APIView):
    def get(self, request, pk):
        try:
            news_article = NewsArticle.objects.get(pk=pk)
            serializer = NewsArticleSerializer(news_article)
            return Response(serializer.data)
        except NewsArticle.DoesNotExist:
            return Response({'error': 'News article not found'}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, pk):
        try:
            news_article = NewsArticle.objects.get(pk=pk)
            news_article.delete()
            return Response({'message': 'News article deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
        except NewsArticle.DoesNotExist:
            return Response({'error': 'News article not found'}, status=status.HTTP_404_NOT_FOUND)