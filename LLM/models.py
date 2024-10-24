from django.db import models

class NewsArticle(models.Model):

    NEWS_TYPE_CHOICES = [
        ('conference', 'مؤتمر'),
        ('event', 'زيارة'),
        ('urgent', 'حدث'),
    ]

    title = models.CharField(max_length=200)
    news_type = models.CharField(max_length=50, choices=NEWS_TYPE_CHOICES)
    details = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
