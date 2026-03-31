"""
Custom template filters for ArtisticSound
"""
import re
from django import template
from django.utils.html import escape

register = template.Library()


@register.filter
def linkify(text):
    """
    Convert URLs in text to clickable links
    Usage: {{ message.content|linkify|safe }}
    """
    if not text:
        return text
    
    # Regex to find URLs
    url_pattern = r'(https?://[^\s<>"\']+)'
    
    def make_link(match):
        url = match.group(1)
        return f'<a href="{escape(url)}" target="_blank" rel="noopener noreferrer">{escape(url)}</a>'
    
    # Escape HTML first to prevent injection
    text = escape(text)
    
    # Replace URLs with links
    text = re.sub(url_pattern, make_link, text, flags=re.IGNORECASE)
    
    return text
