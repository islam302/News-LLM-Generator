import os
from django.shortcuts import render, redirect
from django.views import View
from dotenv import load_dotenv
import openai
from .forms import NewsArticleForm
from .models import NewsArticle


class OpenaiView(View):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        load_dotenv()
        openai.api_key = os.getenv('OPENAI_API_KEY')

    def generate_news_content(self, news_type, title, details):
        prompt = f"""
        ????? ?? ??????? ?? ????? ??? ?????? '{title}'
        ?????? ????? ?? '{news_type}'
        ???? ??? ???????? ??? ??????? ???: '{details}'
        ???? ?????? ?????? ? ????? ????? ?????? ?????? ????? ??? ?????? ????? ???????.
        ???? ?????? ?? ?? ??????? ??? ?????? ?????? ??? ??????? ?????? ??? ???? ?????.
        """

        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "user", "content": prompt}
            ],
            max_tokens=7000,
            temperature=0.7
        )

        content = response['choices'][0]['message']['content'].strip()

        return content

    def create_news(self, request):
        if request.method == 'POST':
            form = NewsArticleForm(request.POST)
            if form.is_valid():
                news_article = form.save(commit=False)
                news_article.details = self.generate_news_content(
                    form.cleaned_data['news_type'],
                    form.cleaned_data['title'],
                    form.cleaned_data['details'],
                )
                news_article.save()
                return redirect('news_detail', pk=news_article.pk)
        else:
            form = NewsArticleForm()

        return render(request, 'create_news.html', {'form': form})

    def news_detail(self, request, pk):
        try:
            news_article = NewsArticle.objects.get(pk=pk)
            return render(request, 'news_detail.html', {'news_article': news_article})
        except NewsArticle.DoesNotExist:
            return render(request, '404.html', status=404)



def home(request):
    return render(request, 'home.html')
