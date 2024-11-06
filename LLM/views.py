import os
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, viewsets
from dotenv import load_dotenv
import openai
from .models import NewsArticle
from .serializers import NewsArticleSerializer
import requests
from bs4 import BeautifulSoup
import urllib.parse
import json
from django.http import JsonResponse


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

class AskOpenaiView(viewsets.ViewSet):

    def __init__(self):
        load_dotenv()
        openai.api_key = os.getenv('OPENAI_API_KEY')

    def search_in_una(self, query):
        encoded_query = urllib.parse.quote(query)
        search_url = f'https://una-oic.org/?s={encoded_query}'
        try:
            response = requests.get(search_url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            articles = []
            for post_item in soup.find_all('li', class_='post-item'):
                title_tag = post_item.find('h2', class_='post-title')
                link_tag = title_tag.find('a') if title_tag else None
                excerpt_tag = post_item.find('p', class_='post-excerpt')
                image_tag = post_item.find('img')

                if link_tag and excerpt_tag:
                    title = link_tag.text.strip()
                    link = link_tag['href']
                    content = excerpt_tag.text.strip()
                    image_url = image_tag['src'] if image_tag else None
                    articles.append({
                        'title': title,
                        'link': link,
                        'content': content,
                        'image_url': image_url
                    })
                if len(articles) >= 5:
                    break
            return articles
        except Exception as e:
            print(f"Error fetching search results: {e}")
            return []

    def get_article_content(self, url):
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            title = soup.title.string if soup.title else "No title found"
            paragraphs = soup.find_all('p')
            content = ' '.join([p.get_text() for p in paragraphs if p.get_text()])
            return title, content
        except Exception as e:
            print(f"Error fetching content from {url}: {e}")
            return "No title found", "No content found"

    def contact_with_openai(self, question, search_results):
        search_links = "\n".join(search_results)
        prompt = f"ابحث عن اجابة دقيقة لهذا السؤال: \"{question}\". استخدم المعلومات التالية للاجابة: {search_links}"
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=300,
                temperature=0.0
            )
            message = response.choices[0].message['content'].strip()
            if "none" in message.lower() or not message:
                return "لم أستطع العثور على معلومات دقيقة."
            return message
        except openai.error.RateLimitError:
            print("حدث خطأ بسبب الحد الأقصى لعدد الطلبات. يرجى المحاولة لاحقًا.")
            return "خطأ في الحد الأقصى للطلب. يرجى المحاولة لاحقًا."
        except Exception as e:
            print(f"حدث خطأ: {e}")
            return str(e)

    def question(self, request):
        if request.method == 'OPTIONS':
            response = HttpResponse()
            response['Access-Control-Allow-Origin'] = '*'
            response['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
            response['Access-Control-Allow-Headers'] = 'Content-Type, X-CSRFToken'
            return response

        if request.method == 'POST':
            try:
                data = json.loads(request.body)
                question = data.get('question', '').strip()
                search_results = self.search_in_una(question)
                return JsonResponse({'question': question, 'answer': search_results}, status=200)
            except json.JSONDecodeError:
                return JsonResponse({'error': 'Invalid JSON format'}, status=400)
            except Exception as e:
                return JsonResponse({'error': str(e)}, status=500)
