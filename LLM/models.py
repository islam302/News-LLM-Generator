from django.db import models

class NewsArticle(models.Model):

    news_type = models.CharField(max_length=10)
    details = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.title
