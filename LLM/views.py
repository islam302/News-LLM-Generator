from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from django.urls import reverse
from .models import NewsArticle, NewsTemplate
from .serializers import NewsArticleCreateSerializer, NewsArticleSerializer, NewsTemplateSerializer
from rest_framework.generics import RetrieveUpdateDestroyAPIView
import openai
import random
from dotenv import load_dotenv
from rest_framework.viewsets import ModelViewSet
import os



class OpenaiAPIView(APIView):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        load_dotenv()
        openai.api_key = os.getenv('OPENAI_API_KEY')

    def generate_news_content(self, news_type, place, source, event, date, participants, event_details, creation_type):
        try:
            template_obj = NewsTemplate.objects.filter(news_type=news_type).first()
            if creation_type == "template_only":
                if template_obj and template_obj.templates:
                    template = random.choice(template_obj.templates)
                    content = template.format(
                        news_type=news_type,
                        place=place,
                        source=source,
                        event=event,
                        date=date,
                        participants=participants,
                        event_details=event_details
                    )
                    return content
                else:
                    return "No templates available for this news type."

            elif creation_type == "openai_only":
                # فقط استخدام OpenAI
                prompt = f"""
                أريدك أن تساعدني في تحرير خبر.
                وافق قواعد الصياغة الصحفية للأخبار
                تأكد من أن النص يكون واضحًا، موجزًا، ويستخدم لغة إعلامية دقيقة بدون التأثير علي المعلومات الموجودة.

                تصنيف الخبر: '{news_type}'
                - المكان: '{place}'
                - المصدر: '{source}'
                - الحدث: '{event}'
                - اليوم والتاريخ: '{date}'
                - المشاركون: '{participants}'
                - تفاصيل الحدث المتوفرة: '{event_details}'
                """
                response = openai.ChatCompletion.create(
                    model="gpt-4",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=1000,
                    temperature=0.7
                )
                return response.choices[0].message['content'].strip()

            elif creation_type == "hybrid":
                # الدمج بين الاثنين
                if template_obj and template_obj.templates:
                    template = random.choice(template_obj.templates)
                    formatted_content = template.format(
                        news_type=news_type,
                        place=place,
                        source=source,
                        event=event,
                        date=date,
                        participants=participants,
                        event_details=event_details
                    )
                    # إضافة النص الناتج من OpenAI
                    prompt = f"""
                    أريدك أن تساعدني في تحرير خبر بناءً على هذا النص المبدئي:
                    {formatted_content}

                    وافق قواعد الصياغة الصحفية للأخبار
                    تأكد من أن النص يكون واضحًا، موجزًا، ويستخدم لغة إعلامية دقيقة.
                    """
                    response = openai.ChatCompletion.create(
                        model="gpt-4",
                        messages=[{"role": "user", "content": prompt}],
                        max_tokens=1000,
                        temperature=0.7
                    )
                    return response.choices[0].message['content'].strip()
                else:
                    return self.generate_news_content(
                        news_type, place, source, event, date, participants, event_details, "openai_only"
                    )

        except Exception as e:
            print(f"Error generating news content: {e}")
            return "Error generating content."

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
            creation_type = serializer.validated_data.get('creation_type', 'template_only')  # Default to "template_only"

            generated_content = self.generate_news_content(
                news_type, place, source, event, date, participants, event_details, creation_type
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


# class OpenaiAPIView(APIView):
#
#     def __init__(self, **kwargs):
#         super().__init__(**kwargs)
#         load_dotenv()
#         openai.api_key = os.getenv('OPENAI_API_KEY')
#
#     # def generate_news_content(self, news_type, place, source, event, date, participants, event_details):
#     #
#     #     NEWS_TEMPLATES = {
#     #         "زيارة": [
#     #             """
#     #             اليوم في {place}، قام {participants} بزيارة هامة لمناقشة {event}.
#     #             تم التأكيد على أهمية {event_details} خلال اللقاء الذي جرى بتاريخ {date}.
#     #             وأكد المصدر {source} أن هذا الحدث يمثل نقطة تحول في {news_type}.
#     #             """,
#     #             """
#     #             في حدث بارز بتاريخ {date}، استضاف {place} زيارة {participants}.
#     #             وركز النقاش حول {event}، مما يعكس أهمية {event_details}.
#     #             وفقًا لـ {source}، فإن هذا الحدث يشكل أهمية كبيرة لنوع الخبر: {news_type}.
#     #             """
#     #         ],
#     #         "عقد مؤتمر": [
#     #             """
#     #             في مؤتمر هام عقد في {place} بتاريخ {date}، اجتمع {participants} لمناقشة {event}.
#     #             وأكدت المصادر {source} أن {event_details} كانت محور النقاش، مع التركيز على تعزيز التعاون الدولي.
#     #             """,
#     #             """
#     #             تم عقد مؤتمر مميز في {place} بتاريخ {date}، بمشاركة {participants}.
#     #             ركز المؤتمر على {event}، حيث أشار المصدر {source} إلى أهمية {event_details} للمستقبل.
#     #             """
#     #         ],
#     #         "عقد ورشة عمل": [
#     #             """
#     #             تم عقد ورشة عمل في {place} بتاريخ {date}، شارك فيها {participants}.
#     #             ركزت الورشة على {event}، وأبرزت {event_details} كأحد أهم مخرجات النقاش.
#     #             """,
#     #             """
#     #             في {place}، أقيمت ورشة عمل بتاريخ {date} بمشاركة {participants}.
#     #             تناولت الورشة {event} بالتفصيل، مع التأكيد على {event_details}.
#     #             """
#     #         ],
#     #         "افتتاح وتدشين": [
#     #             """
#     #             في {place}، شهد {participants} بتاريخ {date} افتتاحًا رسميًا لتدشين {event}.
#     #             ووفقًا للمصدر {source}، فإن {event_details} يعكس أهمية المشروع للمنطقة.
#     #             """,
#     #             """
#     #             بتاريخ {date}، تم افتتاح {event} في {place} بحضور {participants}.
#     #             وأكد المصدر {source} أن هذا الافتتاح يمثل تطورًا هامًا، حيث تم التركيز على {event_details}.
#     #             """
#     #         ],
#     #     }
#     #
#     #     templates = NEWS_TEMPLATES.get(news_type, None)
#     #
#     #     if templates:
#     #         template = random.choice(templates)
#     #
#     #         raw_content = template.format(
#     #             news_type=news_type,
#     #             place=place,
#     #             source=source,
#     #             event=event,
#     #             date=date,
#     #             participants=participants,
#     #             event_details=event_details
#     #         )
#     #
#     #         prompt = f"""
#     #         أريدك أن تعيد صياغة النص التالي باللغة العربية بطريقة محسنة ومهنية وتوافق قواعد الصياغة الصحفية للأخبار:
#     #
#     #         {raw_content}
#     #
#     #         تأكد من أن النص يكون واضحًا، موجزًا، ويستخدم لغة إعلامية دقيقة بدون التأثير علي المعلومات الموجودة.
#     #         """
#     #
#     #         try:
#     #             response = openai.ChatCompletion.create(
#     #                 model="gpt-4",
#     #                 messages=[{"role": "user", "content": prompt}],
#     #                 max_tokens=300,
#     #                 temperature=0.5
#     #             )
#     #             improved_content = response.choices[0].message['content'].strip()
#     #             return improved_content
#     #         except Exception as e:
#     #             print(f"Error with OpenAI: {e}")
#     #             return raw_content
#     #     else:
#     #         return "نوع الخبر غير مدعوم."
#
#     def generate_news_content(self, news_type, place, source, event, date, participants, event_details):
#
#         NEWS_TEMPLATES = {
#             "زيارة": [
#                 """
#                 اليوم في {place}، قام {participants} بزيارة هامة لمناقشة {event}.
#                 تم التأكيد على أهمية {event_details} خلال اللقاء الذي جرى بتاريخ {date}.
#                 وأكد المصدر {source} أن هذا الحدث يمثل نقطة تحول في {news_type}.
#                 """,
#                 """
#                 في حدث بارز بتاريخ {date}، استضاف {place} زيارة {participants}.
#                 وركز النقاش حول {event}، مما يعكس أهمية {event_details}.
#                 وفقًا لـ {source}، فإن هذا الحدث يشكل أهمية كبيرة لنوع الخبر: {news_type}.
#                 """
#             ],
#             "عقد مؤتمر": [
#                 """
#                 في مؤتمر هام عقد في {place} بتاريخ {date}، اجتمع {participants} لمناقشة {event}.
#                 وأكدت المصادر {source} أن {event_details} كانت محور النقاش، مع التركيز على تعزيز التعاون الدولي.
#                 """,
#                 """
#                 تم عقد مؤتمر مميز في {place} بتاريخ {date}، بمشاركة {participants}.
#                 ركز المؤتمر على {event}، حيث أشار المصدر {source} إلى أهمية {event_details} للمستقبل.
#                 """
#             ],
#             "عقد ورشة عمل": [
#                 """
#                 تم عقد ورشة عمل في {place} بتاريخ {date}، شارك فيها {participants}.
#                 ركزت الورشة على {event}، وأبرزت {event_details} كأحد أهم مخرجات النقاش.
#                 """,
#                 """
#                 في {place}، أقيمت ورشة عمل بتاريخ {date} بمشاركة {participants}.
#                 تناولت الورشة {event} بالتفصيل، مع التأكيد على {event_details}.
#                 """
#             ],
#             "افتتاح وتدشين": [
#                 """
#                 في {place}، شهد {participants} بتاريخ {date} افتتاحًا رسميًا لتدشين {event}.
#                 ووفقًا للمصدر {source}، فإن {event_details} يعكس أهمية المشروع للمنطقة.
#                 """,
#                 """
#                 بتاريخ {date}، تم افتتاح {event} في {place} بحضور {participants}.
#                 وأكد المصدر {source} أن هذا الافتتاح يمثل تطورًا هامًا، حيث تم التركيز على {event_details}.
#                 """
#             ],
#         }
#
#         templates = NEWS_TEMPLATES.get(news_type, None)
#
#         if templates:
#             template = random.choice(templates)
#
#             content = template.format(
#                 news_type=news_type,
#                 place=place,
#                 source=source,
#                 event=event,
#                 date=date,
#                 participants=participants,
#                 event_details=event_details
#             )
#             return content
#         else:
#             prompt = f"""
#             أريدك أن تساعدني في تحرير خبر.
#             وافق قواعد الصياغة الصحفية للأخبار
#             تأكد من أن النص يكون واضحًا، موجزًا، ويستخدم لغة إعلامية دقيقة بدون التأثير علي المعلومات الموجودة.
#
#             تصنيف الخبر: '{news_type}'
#             - المكان: '{place}'
#             - المصدر: '{source}'
#             - الحدث: '{event}'
#             - اليوم والتاريخ: '{date}'
#             - المشاركون: '{participants}'
#             - تفاصيل الحدث المتوفرة: '{event_details}'
#             """
#             response = openai.ChatCompletion.create(
#                 model="gpt-4",
#                 messages=[{"role": "user", "content": prompt}],
#                 max_tokens=1000,
#                 temperature=0.7
#             )
#
#             return response.choices[0].message['content'].strip()
#
#     def post(self, request):
#         serializer = NewsArticleCreateSerializer(data=request.data)
#         if serializer.is_valid():
#             news_type = serializer.validated_data['news_type']
#             place = serializer.validated_data['place']
#             source = serializer.validated_data['source']
#             event = serializer.validated_data['event']
#             date = serializer.validated_data['date']
#             participants = serializer.validated_data['participants']
#             event_details = serializer.validated_data['event_details']
#
#             generated_content = self.generate_news_content(
#                 news_type, place, source, event, date, participants, event_details
#             )
#
#             news_article = NewsArticle.objects.create(
#                 news_type=news_type,
#                 details=generated_content
#             )
#
#             response_serializer = NewsArticleSerializer(news_article)
#             return Response(response_serializer.data, status=status.HTTP_201_CREATED)
#
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
