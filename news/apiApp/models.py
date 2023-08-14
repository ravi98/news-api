from django.db import models
from django.contrib.auth.models import AbstractUser
from news import settings

from datetime import datetime


class User(AbstractUser):
    is_banned=models.BooleanField(default=False)


class SearchTableManager(models.Manager):
    def get_or_none(self, **kwargs):
        try:
            return self.get(**kwargs)
        except self.model.DoesNotExist:
            return None


class SearchTable(models.Model):
    user=models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    keyword=models.TextField(blank=False)
    created_date=models.DateTimeField(auto_now_add=True)
    latest_article_date=models.DateTimeField()
    
    objects=SearchTableManager()
    

class Article(models.Model):
    keyword=models.ForeignKey(
        SearchTable,
        on_delete=models.CASCADE
    )
    user=models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    source_id=models.TextField(null=True)
    source_name=models.TextField(null=True)
    author=models.TextField(null=True)
    title=models.TextField(null=True)
    description=models.TextField(null=True)
    url=models.URLField(blank=False)
    urlToImage=models.URLField(null=True)
    publishedAt=models.DateTimeField(blank=False)
    content=models.TextField(null=True)
    
    def __str__(self):
        return self.title