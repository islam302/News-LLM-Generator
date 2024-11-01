import os
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from dotenv import load_dotenv
import openai
from .models import NewsArticle
from .serializers import NewsArticleSerializer


class OpenaiAPIView(APIView):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        load_dotenv()
        openai.api_key = os.getenv('OPENAI_API_KEY')

    def generate_news_content(self, news_type, details, what=None, who=None, where=None, when=None, how=None, why=None):
        prompt = f"""
        أريدك أن تساعدني في تحرير خبر'
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
            messages=[
                {"role": "user", "content": prompt}
            ],
            max_tokens=7000,
            temperature=0.7
        )

        content = response.choices[0].message['content'].strip()
        return content

    def post(self, request):

        serializer = NewsArticleSerializer(data=request.data)
        if serializer.is_valid():

            news_type = serializer.validated_data['news_type']
            details = serializer.validated_data['details']
            what = serializer.validated_data.get('what')
            who = serializer.validated_data.get('who')
            where = serializer.validated_data.get('where')
            when = serializer.validated_data.get('when')
            how = serializer.validated_data.get('how')
            why = serializer.validated_data.get('why')

            generated_content = self.generate_news_content(news_type, details, what, who, where, when, how, why)

            news_article = NewsArticle.objects.create(
                news_type=news_type,
                details=generated_content
            )

            return Response(
                {'url': reverse('news_detail', kwargs={'pk': news_article.pk})},
                status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class NewsDetailAPIView(APIView):
    def get(self, request, pk):
        try:
            news_article = NewsArticle.objects.get(pk=pk)
            serializer = NewsArticleSerializer(news_article)
            return Response(serializer.data)
        except NewsArticle.DoesNotExist:
            return Response({'error': 'News article not found'}, status=status.HTTP_404_NOT_FOUND)
