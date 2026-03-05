from django.contrib import admin
from .models import Post, Project

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('title', 'author')
    ordering = ('-created_at',)

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'budget', 'is_open', 'author', 'created_at')
    list_filter = ('category', 'is_open', 'created_at')
    search_fields = ('title', 'author')
    ordering = ('-created_at',)
