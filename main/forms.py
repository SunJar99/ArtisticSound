from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Post, Project, JoinRequest, Message, Comment, DirectMessage, ChatRequest

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('This email is already registered.')
        return email

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('title', 'description', 'youtube_url', 'tags')
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Post Title'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Post Description',
                'rows': 5
            }),
            'youtube_url': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://youtu.be/... or https://www.youtube.com/watch?v=...'
            }),
            'tags': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'music, art, creative (comma-separated)'
            }),
        }

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ('title', 'description', 'category', 'budget', 'timeline', 'requirements', 'tags')
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Project Title'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Project Description',
                'rows': 3
            }),
            'category': forms.Select(attrs={
                'class': 'form-control',
            }),
            'budget': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., $500-$1000'
            }),
            'timeline': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., 2-4 weeks'
            }),
            'requirements': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Detailed project requirements',
                'rows': 5
            }),
            'tags': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'design, urgent, flexible (comma-separated)'
            }),
        }


class JoinRequestForm(forms.ModelForm):
    class Meta:
        model = JoinRequest
        fields = ('message',)
        widgets = {
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Tell the project creator why you want to join this project',
                'rows': 4
            }),
        }


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ('content',)
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Type your message here...',
                'rows': 3
            }),
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('content',)
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Write a comment...',
                'rows': 3
            }),
        }


class DirectMessageForm(forms.ModelForm):
    class Meta:
        model = DirectMessage
        fields = ('content',)
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Type your message...',
                'rows': 4
            }),
        }


class ChatRequestForm(forms.ModelForm):
    class Meta:
        model = ChatRequest
        fields = ('message',)
        widgets = {
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Tell the creator why you want to chat (optional)',
                'rows': 4
            }),
        }
