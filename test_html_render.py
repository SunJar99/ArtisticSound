import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from django.conf import settings
import re

# Add testserver to ALLOWED_HOSTS for testing
if 'testserver' not in settings.ALLOWED_HOSTS:
    settings.ALLOWED_HOSTS.append('testserver')

# Create a test client
client = Client()

# Try to login with Sunjar - use a simpler password
user = User.objects.get(username='Sunjar')
print(f"Found user: {user.username}")

# Make request WITHOUT authentication first
response = client.get('/chat/')
print(f"Response status (no auth): {response.status_code}")

# If redirected to login, that's expected
if response.status_code == 302:
    print("✓ Correctly redirected to login (expected for unauthenticated)")
    # Manually simulate an authenticated request
    from django.test import RequestFactory
    from main.views import unified_chat
    from django.contrib.auth.models import AnonymousUser
    
    # Create a request
    factory = RequestFactory()
    request = factory.get('/chat/')
    request.user = user
    
    # Call the view directly
    response = unified_chat(request)
    if response.status_code == 200:
        html = response.content.decode('utf-8')
        print(f"Response status (with direct user): 200")
    else:
        print(f"Response status (with direct user): {response.status_code}")
else:
    html = response.content.decode('utf-8')

# Look for data-messages in the HTML
if 'data-messages' in html:
    print('✓ data-messages attribute found in HTML')
    # Extract using different patterns since Django escapejs modifies it
    matches = re.findall(r'data-messages="([^"]*)"', html)
    if matches:
        print(f'✓ Found {len(matches)} data-messages attributes (double quoted)')
        for i, match in enumerate(matches):
            print(f'  Attribute {i+1} length: {len(match)} chars')
            print(f'  First 200 chars: {match[:200]}...')
    else:
        matches = re.findall(r"data-messages='([^']*)'", html)
        print(f'✓ Found {len(matches)} data-messages attributes (single quoted)')
        if matches:
            for i, match in enumerate(matches):
                print(f'  Attribute {i+1} length: {len(match)} chars')
else:
    print('✗ data-messages attribute NOT found')

# Check for the conversation items
if 'conversation-item' in html:
    print('✓ conversation-item divs found')
    count = html.count('conversation-item')
    print(f'  Found {count} conversation items')

# Check conversation username
if 'Zhad' in html:
    print('✓ Conversation username (Zhad) found in HTML')
else:
    print('✗ Zhad not found in HTML')

# Check for current user ID
if 'data-current-user-id' in html:
    match = re.search(r'data-current-user-id="(\d+)"', html)
    if match:
        print(f'✓ Current user ID found: {match.group(1)}')

