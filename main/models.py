from django.db import models
from django.contrib.auth.models import User

class Post(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, default='')
    youtube_url = models.CharField(max_length=500, blank=True, default='', help_text="YouTube URL")
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
    
    def get_youtube_video_id(self):
        """Extract YouTube video ID from URL with robust error handling"""
        if not self.youtube_url:
            return None
        
        try:
            # Strip whitespace from URL
            url = str(self.youtube_url).strip()
            
            if not url:
                return None
            
            video_id = None
            
            # Handle youtu.be short URLs first (most common)
            if 'youtu.be/' in url:
                # Format: https://youtu.be/VIDEO_ID or https://youtu.be/VIDEO_ID?t=10
                video_id = url.split('youtu.be/')[1]
                # Remove query parameters
                if '?' in video_id:
                    video_id = video_id.split('?')[0]
                if '&' in video_id:
                    video_id = video_id.split('&')[0]
            
            # Handle youtube.com/watch URLs
            elif 'youtube.com/watch' in url:
                # Format: https://www.youtube.com/watch?v=VIDEO_ID or with &t=10
                if 'v=' in url:
                    video_id = url.split('v=')[1]
                    # Remove additional parameters
                    if '&' in video_id:
                        video_id = video_id.split('&')[0]
            
            # Handle youtube.com/embed URLs
            elif 'youtube.com/embed/' in url:
                # Format: https://www.youtube.com/embed/VIDEO_ID
                video_id = url.split('embed/')[1]
                # Remove query parameters
                if '?' in video_id:
                    video_id = video_id.split('?')[0]
            
            # Validate and return video_id
            if video_id:
                video_id = video_id.strip()
                # YouTube video IDs are typically 10-11 characters of alphanumeric, dash, underscore
                # Be lenient with length to handle edge cases
                if (9 <= len(video_id) <= 12) and all(c.isalnum() or c in '-_' for c in video_id):
                    return video_id
            
            return None
            
        except Exception as e:
            return None


class Project(models.Model):
    CATEGORY_CHOICES = [
        ('design', 'Design'),
        ('development', 'Development'),
        ('music', 'Music'),
        ('animation', 'Animation'),
        ('art', 'Art'),
        ('singer', 'Singer'),
        ('writing', 'Writing'),
        ('other', 'Other'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    budget = models.CharField(max_length=100, help_text="e.g., $500-$1000")
    timeline = models.CharField(max_length=100, help_text="e.g., 2-4 weeks")
    requirements = models.TextField(help_text="Detailed project requirements")
    tags = models.CharField(max_length=200, blank=True, default='', help_text="Comma-separated tags")
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    is_open = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    def get_tags_list(self):
        return [tag.strip() for tag in self.tags.split(',') if tag.strip()]
