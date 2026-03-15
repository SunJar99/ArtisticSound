import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import RequestFactory
from main.views import unified_chat
from django.contrib.auth.models import User
import json
import re

# Get Sunjar user  
user = User.objects.get(username='Sunjar')

# Create a request
factory = RequestFactory()
request = factory.get('/chat/')
request.user = user

# Call the view directly
response = unified_chat(request)
html = response.content.decode('utf-8')

# Extract the data-messages attribute value
match = re.search(r'data-messages="([^"]*)"', html)
if match:
    attr_value = match.group(1)
    print(f"Found data-messages attribute")
    print(f"Length: {len(attr_value)} chars")
    print(f"First 300 chars: {attr_value[:300]}")
    
    # The value is escaped by Django's escapejs
    # We need to unescape it. In HTML, \u0022 becomes " when parsed
    # But in our Python string, we have the literal \u0022
    # We need to properly decode it
    
    print("\nTrying to parse as JSON after unescaping:")
    try:
        # Decode the escaped JSON
        import codecs
        unescaped = codecs.decode(attr_value, 'unicode_escape')
        print(f"Unescaped: {unescaped[:300]}")
        
        # Now parse
        data = json.loads(unescaped)
        print(f"✓ Successfully parsed! Got {len(data)} messages")
        for i, msg in enumerate(data):
            print(f"  Message {i+1}: {msg['sender_username']} -> {msg['content'][:50]}")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    print("\nWhat JavaScript would receive:")
    # Simulate what JavaScript gets - the HTML entity is unescaped by browser
    # So \u0022 becomes the quote character
    print("HTML attribute value (as appears in source):", attr_value[:100])
    
else:
    print("✗ Could not find data-messages attribute")
