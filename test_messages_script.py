import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import RequestFactory
from main.views import unified_chat
from django.contrib.auth.models import User
from django.conf import settings
import re
import json

# Add testserver to ALLOWED_HOSTS
if 'testserver' not in settings.ALLOWED_HOSTS:
    settings.ALLOWED_HOSTS.append('testserver')

# Get Sunjar user
user = User.objects.get(username='Sunjar')

# Create a request
factory = RequestFactory()
request = factory.get('/chat/')
request.user = user

# Call the view directly
response = unified_chat(request)
html = response.content.decode('utf-8')

# Look for the messages-data script tag
if '<script id="messages-data"' in html:
    print('✓ messages-data script tag found')
    
    # Extract the script content using a simpler approach
    start = html.find('<script id="messages-data" type="application/json">')
    if start != -1:
        start += len('<script id="messages-data" type="application/json">')
        end = html.find('</script>', start)
        if end != -1:
            json_content = html[start:end].strip()
            print(f'✓ Script content extracted (length: {len(json_content)} chars)')
            print(f'  First 300 chars: {json_content[:300]}...')
            
            # Try to parse it
            try:
                data = json.loads(json_content)
                print(f'✓ Successfully parsed JSON')
                print(f'  Contains conversations for: {list(data.keys())}')
                
                # Show messages for first user
                for username, messages in data.items():
                    print(f'  {username} has {len(messages)} messages')
                    for msg in messages[:1]:
                        print(f'    - {msg["sender_username"]}: {msg["content"][:50]}')
                    break
            except json.JSONDecodeError as e:
                print(f'✗ Failed to parse JSON: {e}')
                print(f'  Content: {json_content[:500]}')
        else:
            print('✗ Could not find closing script tag')
    else:
        print('✗ Could not find script tag start')
else:
    print('✗ messages-data script tag NOT found')
    
# Check for conversation items
conv_count = html.count('conversation-item')
print(f'\n✓ Found {conv_count} conversation items')
