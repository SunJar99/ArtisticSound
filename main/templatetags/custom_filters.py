import re
from django import template
from django.utils.html import escape

register = template.Library()


@register.filter
def linkify(text):
    if not text:
        return text
    
    # Regex to find URLs
    url_pattern = r'(https?://[^\s<>"\']+)'
    
    def make_link(match):
        url = match.group(1)
        return f'<a href="{escape(url)}" target="_blank" rel="noopener noreferrer">{escape(url)}</a>'
    
    text = escape(text)
    
    # Replace URLs with links
    text = re.sub(url_pattern, make_link, text, flags=re.IGNORECASE)
    
    return text
