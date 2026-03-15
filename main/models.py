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
            import re
            # Strip whitespace from URL
            url = str(self.youtube_url).strip()
            
            if not url:
                return None
            
            video_id = None
            
            # Try to find 11-character video ID using regex first (catches all formats)
            # YouTube video IDs are exactly 11 chars: alphanumeric, dash, underscore
            match = re.search(r'([a-zA-Z0-9_-]{11})', url)
            if match:
                candidate = match.group(1)
                # Additional validation to avoid matching random 11-char strings
                # YouTube IDs typically have mixed case or common patterns
                if all(c.isalnum() or c in '-_' for c in candidate):
                    return candidate
            
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


class JoinRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='join_requests')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='join_requests')
    message = models.TextField(blank=True, default='', help_text="Message from the applicant")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('project', 'user')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} requested to join {self.project.title}"


class Message(models.Model):
    join_request = models.ForeignKey(JoinRequest, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"Message from {self.sender.username} in {self.join_request}"


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='userprofile')
    allow_post_messages = models.BooleanField(default=True, help_text="Allow other users to send you direct messages")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Profile of {self.user.username}"


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Comment by {self.author.username} on {self.post.title}"


class DirectMessage(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_direct_messages')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_direct_messages')
    post = models.ForeignKey(Post, on_delete=models.SET_NULL, null=True, blank=True, related_name='direct_messages')
    content = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Message from {self.sender.username} to {self.recipient.username}"


class ChatRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_requests_sent')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_requests_received')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='chat_requests', null=True, blank=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='chat_requests', null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    message = models.TextField(blank=True, default='', help_text="Optional message with chat request")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        context = self.post.title if self.post else self.project.title
        return f"Chat request from {self.sender.username} to {self.recipient.username} on {context}"
