from django.db import models
from django.contrib.auth.models import User

class Post(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, default='')
    youtube_url = models.URLField(blank=True, null=True)
    tags = models.CharField(max_length=200, blank=True, default='', help_text="Comma-separated tags")
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    def get_tags_list(self):
        return [tag.strip() for tag in self.tags.split(',') if tag.strip()]
