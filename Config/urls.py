from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from LLM import views  # Assuming you have a views.py in your LLM app

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', TemplateView.as_view(template_name='home.html'), name='home'),  # Home page
    path('create/', views.OpenaiView.as_view(), name='create_news'),  # Example for creating news
    path('llm/', include('LLM.urls')),  # Namespacing LLM URLs
]
