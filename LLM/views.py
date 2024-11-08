from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from .models import NewsArticle
from .serializers import NewsArticleSerializer
import openai
import os
from dotenv import load_dotenv


class OpenaiAPIView(APIView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        load_dotenv()
        openai.api_key = os.getenv('OPENAI_API_KEY')

    def generate_news_content(self, news_type, what=None, who=None, where=None, when=None, how=None, why=None):
        prompt = f"""
        أريدك أن تساعدني في تحرير خبر
        ونوعية الخبر هي '{news_type}'

        هذه بعض المعلومات الأساسية التي يجب تضمينها في الخبر لضمان اكتماله:

        - ماذا حدث؟ '{what}' (وصف الحدث)
        - من شارك في الحدث؟ '{who}' (الشخصيات أو الجهات المشاركة)
        - أين وقع الحدث؟ '{where}' (المكان)
        - متى وقع الحدث؟ '{when}' (الزمان)
        - كيف وقع الحدث؟ '{how}' (الطريقة - إذا كانت متوفرة)
        - لماذا وقع الحدث؟ '{why}' (السبب أو الخلفية - إذا كانت متوفرة)

        يرجى كتابة خبر يشمل مقدمة واضحة، تفاصيل دقيقة حول الخبر، أهمية الموضوع، وآثار التعاون بين الأطراف المعنية. يجب أن يكون المحتوى غنيًا وشاملاً ويجيب على الأسئلة الأساسية على الأقل (ماذا، من، متى، أين) لضمان كمال الخبر.
        """

        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=7000,
            temperature=0.7
        )

        content = response.choices[0].message['content'].strip()
        return content

    def post(self, request):
        serializer = NewsArticleSerializer(data=request.data)
        if serializer.is_valid():
            news_type = serializer.validated_data['news_type']
            what = serializer.validated_data.get('what')
            who = serializer.validated_data.get('who')
            where = serializer.validated_data.get('where')
            when = serializer.validated_data.get('when')
            how = serializer.validated_data.get('how')
            why = serializer.validated_data.get('why')

            # Generate content using OpenAI API
            generated_content = self.generate_news_content(news_type, what, who, where, when, how, why)

            # Create NewsArticle instance
            news_article = NewsArticle.objects.create(
                news_type=news_type,
                details=generated_content
            )

            # Return URL to the created news article
            return Response(
                {'url': reverse('news_detail', kwargs={'pk': news_article.pk}, request=request)},
                status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class NewsDetailAPIView(viewsets.ModelViewSet):
    queryset = NewsArticle.objects.all()
    serializer_class = NewsArticleSerializer

    def list(self, request, *args, **kwargs):
        news_articles = NewsArticle.objects.all()
        serializer = NewsArticleSerializer(news_articles, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
