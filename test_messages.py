import os
import django
import json
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from main.models import DirectMessage, ChatRequest
from django.contrib.auth.models import User

# Get Sunjar user
user = User.objects.get(username='Sunjar')

# Simulate the unified_chat view logic
received_messages = DirectMessage.objects.filter(recipient=user).order_by('-created_at')
sent_messages = DirectMessage.objects.filter(sender=user).order_by('-created_at')

conversations = {}

# Process received messages
for msg in received_messages:
    key = msg.sender.username
    if key not in conversations:
        conversations[key] = {
            'user': msg.sender,
            'last_message': msg,
            'unread_count': 0,
            'messages': []
        }
    conversations[key]['unread_count'] += 1 if not msg.is_read else 0
    conversations[key]['messages'].append(msg)

# Process sent messages
for msg in sent_messages:
    key = msg.recipient.username
    if key not in conversations:
        conversations[key] = {
            'user': msg.recipient,
            'last_message': msg,
            'unread_count': 0,
            'messages': []
        }
    conversations[key]['messages'].append(msg)

print(f'Total conversations: {len(conversations)}')

# Show what's in conversations
for username, conv in conversations.items():
    print(f'\n{username}:')
    print(f'  User: {conv["user"].username}')
    print(f'  Last message: {conv["last_message"].content if conv["last_message"] else "None"}')
    print(f'  Unread count: {conv["unread_count"]}')
    print(f'  Message count: {len(conv["messages"])}')
    
    # Check serialization
    messages_list = []
    for msg in conv['messages']:
        messages_list.append({
            'id': msg.id,
            'sender_id': msg.sender.id,
            'sender_username': msg.sender.username,
            'recipient_id': msg.recipient.id,
            'content': msg.content,
            'created_at': msg.created_at.isoformat(),
            'is_read': msg.is_read
        })
    messages_json = json.dumps(messages_list)
    print(f'  Serialized JSON length: {len(messages_json)} chars')
    print(f'  First 150 chars: {messages_json[:150]}...')
    
    # Verify parsing
    parsed = json.loads(messages_json)
    print(f'  Parsed back: {len(parsed)} messages')
