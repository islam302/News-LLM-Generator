from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from LLM import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('llm/', include('LLM.urls')),
]
