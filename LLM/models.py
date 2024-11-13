from django.db import models

class NewsArticle(models.Model):
    news_type = models.CharField(max_length=100)
    details = models.TextField()

    def __str__(self):
        return f"{self.news_type} - {self.details[:50]}"
