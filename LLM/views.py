from .serializers import NewsArticleCreateSerializer, NewsArticleSerializer, NewsTemplateSerializer
from rest_framework.generics import RetrieveUpdateDestroyAPIView
from rest_framework.viewsets import ModelViewSet
from .models import NewsArticle, NewsTemplate
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from dotenv import load_dotenv
from django.urls import reverse
import openai
import random
import json
import os
from rest_framework.decorators import action

class OpenaiAPIView(APIView):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        load_dotenv()
        openai.api_key = os.getenv('OPENAI_API_KEY')

    def generate_news_content(
            self,
            news_type,
            place=None,
            source=None,
            event=None,
            date=None,
            participants=None,
            event_details=None,
            additional_variables=None,
            creation_type="template_only",
            template_id=None  # Added template_id to select a specific template
    ):
        try:
            # Default variables
            variables = {
                "news_type": news_type,
                "place": place or "",
                "source": source or "",
                "event": event or "",
                "date": date or "",
                "participants": participants or "",
                "event_details": event_details or "",
            }

            # Process additional variables
            if additional_variables:
                if isinstance(additional_variables, str):
                    try:
                        additional_variables = json.loads(additional_variables)  # Convert string to dictionary
                    except json.JSONDecodeError:
                        return "المتغيرات الإضافية يجب أن تكون في شكل قاموس (Dictionary)."
                if isinstance(additional_variables, dict):
                    variables.update(additional_variables)
                else:
                    return "المتغيرات الإضافية يجب أن تكون في شكل قاموس (Dictionary)."

            if template_id:  # If template_id is provided, use it to fetch the specific template
                template_obj = NewsTemplate.objects.filter(id=template_id).first()
                if template_obj and template_obj.templates:
                    template = template_obj.templates  # احصل على القالب الصحيح
                    print(f"Using template: {template}")  # طباعة القالب

            if creation_type == "template_only":
                if template:

                    filtered_variables = {
                        key: value for key, value in variables.items() if f"{{{key}}}" in template
                    }

                    print(f"Filtered variables: {filtered_variables}")

                    try:
                        content = template.format(**filtered_variables)
                        print(f"Generated content: {content}")
                    except KeyError as e:
                        return f"هناك متغير مفقود في القالب: {e}"
                    return content

            # If creation_type is "openai_only"
            elif creation_type == "openai_only":
                # Construct OpenAI prompt
                prompt = f"""
                أريدك أن تساعدني في تحرير خبر.
                وافق قواعد الصياغة الصحفية للأخبار.
                تأكد من أن النص يكون واضحًا، موجزًا، ويستخدم لغة إعلامية دقيقة بدون التأثير على المعلومات الموجودة.
                تصنيف الخبر: '{news_type}'
                {f"- المكان: '{place}'" if place else ""}
                {f"- المصدر: '{source}'" if source else ""}
                {f"- الحدث: '{event}'" if event else ""}
                {f"- اليوم والتاريخ: '{date}'" if date else ""}
                {f"- المشاركون: '{participants}'" if participants else ""}
                {f"- تفاصيل الحدث المتوفرة: '{event_details}'" if event_details else ""}
                {''.join([f"- {key}: '{value}'" for key, value in additional_variables.items()]) if additional_variables else ""}
                محتاج الخبر يكون في حدود 100 كلمة.
                """
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=1000,
                    temperature=0.7
                )
                return response.choices[0].message['content'].strip()

            # If creation_type is "hybrid"
            elif creation_type == "hybrid":
                if template_obj and template_obj.templates:
                    # Use the specific template if template_id is provided or the first template otherwise
                    template = template_obj.templates[0]

                    # Filter variables to include only those present in the template
                    filtered_variables = {
                        key: value for key, value in variables.items() if f"{{{key}}}" in template
                    }

                    # Replace placeholders with values
                    try:
                        formatted_content = template.format(**filtered_variables)
                    except KeyError as e:
                        return f"هناك متغير مفقود في القالب: {e}"

                    # Construct OpenAI prompt with the formatted content
                    prompt = f"""
                    أريدك أن تساعدني في تحرير خبر بناءً على هذا النص المبدئي:
                    {formatted_content}
                    وافق قواعد الصياغة الصحفية للأخبار.
                    تأكد من أن النص يكون واضحًا، موجزًا، ويستخدم لغة إعلامية دقيقة.
                    محتاج الخبر يكون في حدود 100 كلمة.
                    """
                    response = openai.ChatCompletion.create(
                        model="gpt-3.5-turbo",
                        messages=[{"role": "user", "content": prompt}],
                        max_tokens=1000,
                        temperature=0.7
                    )
                    return response.choices[0].message['content'].strip()
                else:
                    # If no template is available, fall back to "openai_only"
                    return self.generate_news_content(
                        news_type, place, source, event, date, participants, event_details, additional_variables,
                        "openai_only"
                    )

        except Exception as e:
            print(f"Error generating news content: {e}")
            return "حدث خطأ أثناء إنشاء المحتوى."

    def post(self, request):
        print("Received request data:", request.data)  # Debugging log
        serializer = NewsArticleCreateSerializer(data=request.data)
        if serializer.is_valid():
            news_type = serializer.validated_data['news_type']
            place = serializer.validated_data['place']
            source = serializer.validated_data['source']
            event = serializer.validated_data['event']
            date = serializer.validated_data['date']
            participants = serializer.validated_data['participants']
            event_details = serializer.validated_data['event_details']
            additional_variables = serializer.validated_data.get('additional_variables', {})
            creation_type = serializer.validated_data.get('creation_type', 'template_only')
            template_id = request.data.get('template_id')  # استلام template_id من الطلب

            generated_content = self.generate_news_content(
                news_type, place, source, event, date, participants, event_details,
                additional_variables, creation_type, template_id=template_id
            )

            news_article = NewsArticle.objects.create(
                news_type=news_type,
                details=generated_content
            )

            response_serializer = NewsArticleSerializer(news_article)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class NewsDetailAPIView(ModelViewSet):
    queryset = NewsArticle.objects.all()
    serializer_class = NewsArticleSerializer


class NewsTemplateViewSet(ModelViewSet):
    queryset = NewsTemplate.objects.all()
    serializer_class = NewsTemplateSerializer

    @action(detail=True, methods=['get'])
    def fields(self, request, pk=None):
        """
        API للحصول على الحقول بناءً على رقم القالب
        """

        template = self.get_object()  # Fetch the template by ID
        return Response({
            "id": template.id,
            "news_type": template.news_type,
            "templates": template.templates,
        })
        return Response({"error": "Template not found"}, status=404)

