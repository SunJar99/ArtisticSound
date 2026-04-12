
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.db.models import Q
from django.http import JsonResponse
import json

from .models import (
    Post, Project, JoinRequest, Message, Comment, 
    DirectMessage, UserProfile, ChatRequest
)
from .forms import (
    ArtistSignupForm, CreationForm, CollaborationForm, PitchForm, 
    DialogueForm, FeedbackForm, DirectDialogueForm, ConversationInviteForm
)


#  AUTH VIEWS



def welcome_stage(request):
    """THE STAGE HAS BEEN OPENED FOR YOU, ARTISTS!"""
    return render(request, 'main/home.html')





def join_the_scene(request):
    """JOIN THE SCENE AND BECOME AN ARTIST!"""
    if request.user.is_authenticated:
        return redirect('main:post_list')
    
    if request.method == 'POST':
        form = ArtistSignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('main:post_list')
    else:
        form = ArtistSignupForm()
    return render(request, 'main/register.html', {'form': form})





def access_gateway(request):
    if request.user.is_authenticated:
        return redirect('main:post_list')
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            
            try:
                from django_otp.plugins.otp_totp.models import TOTP_DEVICE
                if TOTP_DEVICE.objects.filter(user=user, confirmed=True).exists():
                    # Store user info in session and redirect to 2FA
                    request.session['2fa_username'] = user.username
                    request.session['2fa_user_id'] = user.id
                    return redirect('main:login_2fa')
            except Exception as e:
                pass
            
            login(request, user)
            return redirect('main:post_list')
    else:
        form = AuthenticationForm()
    return render(request, 'main/login.html', {'form': form})





def exit_stage(request):
    """Leave the artistic stage lol"""
    logout(request)
    return redirect('main:home')






#  POSTING VIEWSS

def discover_creations(request):

    posts = Post.objects.all()
    query = request.GET.get('q', '')
    
    if query:
        posts = posts.filter(
            Q(title__icontains=query) | 
            Q(tags__icontains=query)
        )
    
    return render(request, 'main/post_list.html', {
        'posts': posts,
        'query': query
    })





def creation_spotlight(request, pk):

    post = get_object_or_404(Post, pk=pk)
    comments = post.comments.all()
    
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            return redirect('main:post_detail', pk=post.pk)
    else:
        form = FeedbackForm()
    
    return render(request, 'main/post_detail.html', {
        'post': post,
        'comments': comments,
        'form': form
    })




def craft_creation(request):
    if not request.user.is_authenticated:
        return redirect('main:register')
    
    if request.method == 'POST':
        form = CreationForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('main:post_detail', pk=post.pk)
    else:
        form = CreationForm()
    return render(request, 'main/create_post.html', {'form': form})




def share_feedback(request, pk):
    post = get_object_or_404(Post, pk=pk)
    
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            return redirect('main:post_detail', pk=post.pk)
    
    return redirect('main:post_detail', pk=post.pk)


# PROJCET VIEWS




def collab_quest(request):
    projects = Project.objects.filter(is_open=True)
    selected_categories = request.GET.getlist('category')
    query = request.GET.get('q', '')
    
    if selected_categories:
        projects = projects.filter(category__in=selected_categories)
    
    if query:
        projects = projects.filter(
            Q(title__icontains=query) | 
            Q(tags__icontains=query)
        )
    
    categories = Project.CATEGORY_CHOICES
    
    return render(request, 'main/project_list.html', {
        'projects': projects,
        'categories': categories,
        'selected_categories': selected_categories,
        'query': query
    })




def collaboration_space(request, pk):

    project = get_object_or_404(Project, pk=pk)
    return render(request, 'main/project_detail.html', {'project': project})





def launch_vision(request):

    if not request.user.is_authenticated:
        return redirect('main:register')
    
    if request.method == 'POST':
        form = CollaborationForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.author = request.user
            project.save()
            return redirect('main:project_detail', pk=project.pk)
    else:
        form = CollaborationForm()
    return render(request, 'main/create_project.html', {'form': form})





def opportunity_board(request):
    """ shall discover creative opportunities and gigs"""
    return render(request, 'main/jobs.html')




# JOIN REQUEST VIEWS



@login_required(login_url='main:login')
def pitch_for_collab(request, pk):
    project = get_object_or_404(Project, pk=pk)
    
    existing_request = JoinRequest.objects.filter(
        project=project, 
        user=request.user
    ).first()
    
    if existing_request:
        return render(request, 'main/project_detail.html', {
            'project': project,
            'error': 'You have already requested to join this project'
        })
    
    if request.user == project.author:
        return render(request, 'main/project_detail.html', {
            'project': project,
            'error': 'You cannot join your own project'
        })
    
    if request.method == 'POST':
        form = PitchForm(request.POST)
        if form.is_valid():
            join_req = form.save(commit=False)
            join_req.project = project
            join_req.user = request.user
            join_req.save()
            return redirect('main:project_detail', pk=project.pk)
    else:
        form = PitchForm()
    
    return render(request, 'main/join_project.html', {
        'project': project,
        'form': form
    })






@login_required(login_url='main:login')
def collab_applications(request):
    pending_requests = JoinRequest.objects.filter(
        project__author=request.user,
        status='pending'
    ).order_by('-created_at')
    
    return render(request, 'main/join_requests.html', {
        'pending_requests': pending_requests
    })
    
    
    
    


@login_required(login_url='main:login')
def my_pitches(request):
    my_requests = JoinRequest.objects.filter(
        user=request.user
    ).order_by('-created_at')
    
    return render(request, 'main/my_join_requests.html', {
        'my_requests': my_requests
    })





@login_required(login_url='main:login')
def greenlight_artist(request, request_id):
    join_req = get_object_or_404(JoinRequest, pk=request_id)
    
    if request.user != join_req.project.author:
        return redirect('main:home')
    
    join_req.status = 'approved'
    join_req.save()

    Message.objects.create(
        join_request=join_req,
        sender=request.user,
        content=f"Your request to join '{join_req.project.title}' has been approved!"
    )
    
    return redirect('main:chat', request_id=request_id)






@login_required(login_url='main:login')
def decline_application(request, request_id):
    join_req = get_object_or_404(JoinRequest, pk=request_id)
    
    if request.user != join_req.project.author:
        return redirect('main:home')
    
    join_req.status = 'rejected'
    join_req.save()
    
    # Send rejection message
    Message.objects.create(
        join_request=join_req,
        sender=request.user,
        content=f"Unfortunately, your request to join '{join_req.project.title}' was rejected."
    )
    
    return redirect('main:join_requests')




# CHATTING VIEWS lmoao



@login_required(login_url='main:login')
def collaboration_dialog(request, request_id):

    join_request = get_object_or_404(JoinRequest, pk=request_id)
    
    # Check if user is either creator or applicant
    if (request.user != join_request.project.author and 
        request.user != join_request.user):
        return redirect('main:home')
    
    if request.method == 'POST':
        form = DialogueForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.join_request = join_request
            message.sender = request.user
            message.save()
            return redirect('main:chat', request_id=request_id)
    else:
        form = DialogueForm()

    Message.objects.filter(
        join_request=join_request
    ).exclude(sender=request.user).update(is_read=True)
    
    messages = Message.objects.filter(join_request=join_request)
    
    return render(request, 'main/chat.html', {
        'join_request': join_request,
        'messages': messages,
        'form': form
    })






@login_required(login_url='main:login')
def conversation_hub(request):
    # Requests sent by user (as applicant)
    sent_requests = JoinRequest.objects.filter(
        user=request.user
    ).order_by('-updated_at')
    



    received_requests = JoinRequest.objects.filter(
        project__author=request.user
    ).order_by('-updated_at')
    
    conversations = []
    



    for join_req in sent_requests:
        last_message = Message.objects.filter(
            join_request=join_req
        ).order_by('-created_at').first()
        unread_count = Message.objects.filter(
            join_request=join_req, 
            is_read=False
        ).exclude(sender=request.user).count()
        
        conversations.append({
            'join_request': join_req,
            'last_message': last_message,
            'unread_count': unread_count,
            'type': 'sent',
            'conversation_type': 'applicant'
        })
    



    for join_req in received_requests:
        last_message = Message.objects.filter(
            join_request=join_req
        ).order_by('-created_at').first()
        unread_count = Message.objects.filter(
            join_request=join_req, 
            is_read=False
        ).exclude(sender=request.user).count()
        
        conversations.append({
            'join_request': join_req,
            'last_message': last_message,
            'unread_count': unread_count,
            'type': 'received',
            'conversation_type': 'creator'
        })
    

    conversations.sort(
        key=lambda x: (
            x['last_message'].created_at 
            if x['last_message'] 
            else x['join_request'].updated_at
        ),
        reverse=True
    )
    
    return render(request, 'main/inbox.html', {
        'conversations': conversations
    })






@login_required(login_url='main:login')
def pulse_check(request):
    """Get count of unread messages (AJAX endpoint)"""
    count = Message.objects.filter(
        join_request__project__author=request.user,
        is_read=False
    ).count()
    return {'unread_count': count}




# DIRECT NESSAGE VIEWS

@login_required(login_url='main:login')
def craft_message(request, username):
    recipient = get_object_or_404(User, username=username)
    
    # Prevent messaging yourself
    if request.user == recipient:
        return render(request, 'main/error.html', {
            'error': 'You cannot message yourself.'
        })




    try:
        profile = recipient.userprofile
        if not profile.allow_post_messages:
            return render(request, 'main/error.html', {
                'error': f'{username} is not accepting direct messages at the moment.'
            })
    except UserProfile.DoesNotExist:
        UserProfile.objects.create(user=recipient)
    
    
    post_id = request.GET.get('post_id')
    post = None
    if post_id:
        post = get_object_or_404(Post, pk=post_id)
    
    if request.method == 'POST':
        form = DirectDialogueForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = request.user
            message.recipient = recipient
            message.post = post
            message.save()
            

            return JsonResponse({
                'success': True,
                'message': {
                    'id': message.id,
                    'sender_username': message.sender.username,
                    'content': message.content,
                    'created_at': message.created_at.isoformat(),
                    'is_read': message.is_read
                }
            })
        else:
            return JsonResponse({
                'success': False,
                'error': 'Invalid message form'
            })
    else:
        form = DirectDialogueForm()
    
    return render(request, 'main/send_message.html', {
        'form': form,
        'recipient': recipient,
        'post': post
    })





@login_required(login_url='main:login')
def message_lounge(request):
    """View all direct message conversations"""
    received_messages = DirectMessage.objects.filter(
        recipient=request.user
    ).order_by('-created_at')
    sent_messages = DirectMessage.objects.filter(
        sender=request.user
    ).order_by('-created_at')
    
    conversations = {}
    
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
    
    DirectMessage.objects.filter(
        recipient=request.user, 
        is_read=False
    ).update(is_read=True)
    
    return render(request, 'main/messages_inbox.html', {
        'conversations': conversations
    })






@login_required(login_url='main:login')
def direct_connection(request, username):
    """View conversation thread with specific user"""
    user = get_object_or_404(User, username=username)
    
    messages = DirectMessage.objects.filter(
        Q(sender=request.user, recipient=user) |
        Q(sender=user, recipient=request.user)
    ).order_by('created_at')
    

    DirectMessage.objects.filter(
        sender=user, 
        recipient=request.user, 
        is_read=False
    ).update(is_read=True)
    
    if request.method == 'POST':
        form = DirectDialogueForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = request.user
            message.recipient = user
            message.save()
            return redirect('main:message_thread', username=username)
    else:
        form = DirectDialogueForm()
    
    return render(request, 'main/message_thread.html', {
        'user': user,
        'messages': messages,
        'form': form
    })


# USER SETTINGS VIEW 





@login_required(login_url='main:login')
def artist_studio(request):
    """User settings page"""
    try:
        profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=request.user)
    
    has_2fa = False
    try:
        from django_otp.plugins.otp_totp.models import TOTP_DEVICE
        has_2fa = TOTP_DEVICE.objects.filter(user=request.user, confirmed=True).exists()
    except Exception as e:
        pass
    
    # Calculate unread message count
    unread_total = 0
    try:
        unread_total = DirectMessage.objects.filter(receiver=request.user, is_read=False).count()
    except:
        pass
    
    if request.method == 'POST':
        allow_messages = request.POST.get('allow_post_messages') == 'on'
        profile.allow_post_messages = allow_messages
        profile.save()
        return redirect('main:settings')
    
    return render(request, 'main/settings.html', {
        'profile': profile,
        'has_2fa': has_2fa,
        'unread_total': unread_total
    })


# CHAT APPROVAL VIEWS  





@login_required(login_url='main:login')
def initiate_collab_chat(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    recipient = post.author
    
    # Prevent messaging yourself
    if request.user == recipient:
        return render(request, 'main/error.html', {
            'error': 'You cannot request to chat with yourself.'
        })
    
    # Check if already requested
    existing = ChatRequest.objects.filter(
        sender=request.user, 
        recipient=recipient, 
        post=post, 
        status='pending'
    ).first()
    
    if existing:
        return render(request, 'main/error.html', {
            'error': 'You already have a pending chat request with this user for this post.'
        })
    
    if request.method == 'POST':
        form = ConversationInviteForm(request.POST)
        if form.is_valid():
            chat_req = form.save(commit=False)
            chat_req.sender = request.user
            chat_req.recipient = recipient
            chat_req.post = post
            chat_req.save()
            return redirect('main:unified_chat')
    else:
        form = ConversationInviteForm()
    
    return render(request, 'main/request_to_chat.html', {
        'form': form,
        'post': post,
        'recipient': recipient
    })







@login_required(login_url='main:login')
def initiate_project_chat(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    recipient = project.author
    
    # Prevent messaging yourself
    if request.user == recipient:
        return render(request, 'main/error.html', {
            'error': 'You cannot request to chat with yourself.'
        })
    
    # Check if already requested
    existing = ChatRequest.objects.filter(
        sender=request.user, 
        recipient=recipient, 
        project=project, 
        status='pending'
    ).first()
    
    if existing:
        return render(request, 'main/error.html', {
            'error': 'You already have a pending chat request with this user for this project.'
        })
    
    if request.method == 'POST':
        form = ConversationInviteForm(request.POST)
        if form.is_valid():
            chat_req = form.save(commit=False)
            chat_req.sender = request.user
            chat_req.recipient = recipient
            chat_req.project = project
            chat_req.save()
            return redirect('main:unified_chat')
    else:
        form = ConversationInviteForm()
    
    return render(request, 'main/request_to_chat.html', {
        'form': form,
        'project': project,
        'recipient': recipient
    })






@login_required(login_url='main:login')
def collaboration_queue(request):
    chat_requests = ChatRequest.objects.filter(
        recipient=request.user, 
        status='pending'
    ).order_by('-created_at')
    
    return render(request, 'main/chat_requests_inbox.html', {
        'chat_requests': chat_requests
    })


@login_required(login_url='main:login')
def accept_collaboration(request, chat_request_id):
    chat_req = get_object_or_404(ChatRequest, pk=chat_request_id, recipient=request.user)
    chat_req.status = 'approved'
    chat_req.save()
    return redirect('main:unified_chat')


@login_required(login_url='main:login')
def decline_collaboration(request, chat_request_id):
    chat_req = get_object_or_404(ChatRequest, pk=chat_request_id, recipient=request.user)
    chat_req.status = 'rejected'
    chat_req.save()
    return redirect('main:unified_chat')


#  UNI CHAT VIEW





@login_required(login_url='main:login')
def conversation_lounge(request):
    if request.method == 'POST':
        if 'approve_chat_request' in request.POST:
            chat_request_id = request.POST.get('chat_request_id')
            chat_req = get_object_or_404(ChatRequest, pk=chat_request_id, recipient=request.user)
            chat_req.status = 'approved'
            chat_req.save()
            return redirect('main:unified_chat')
        
        if 'reject_chat_request' in request.POST:
            chat_request_id = request.POST.get('chat_request_id')
            chat_req = get_object_or_404(ChatRequest, pk=chat_request_id, recipient=request.user)
            chat_req.status = 'rejected'
            chat_req.save()
            return redirect('main:unified_chat')

    received_messages = DirectMessage.objects.filter(
        recipient=request.user
    ).order_by('-created_at')
    sent_messages = DirectMessage.objects.filter(
        sender=request.user
    ).order_by('-created_at')
    

    conversations = {}
    
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

    sent_chat_requests = ChatRequest.objects.filter(
        sender=request.user, 
        status='approved'
    ).order_by('-created_at')
    for chat_req in sent_chat_requests:
        key = chat_req.recipient.username
        if key not in conversations:
            conversations[key] = {
                'user': chat_req.recipient,
                'last_message': None,
                'unread_count': 0,
                'messages': []
            }
    
    received_chat_requests = ChatRequest.objects.filter(
        recipient=request.user, 
        status='approved'
    ).order_by('-created_at')
    for chat_req in received_chat_requests:
        key = chat_req.sender.username
        if key not in conversations:
            conversations[key] = {
                'user': chat_req.sender,
                'last_message': None,
                'unread_count': 0,
                'messages': []
            }
    
    for username, conv in conversations.items():
        messages = conv['messages']
        messages_json = json.dumps([{
            'id': msg.id,
            'sender_id': msg.sender.id,
            'sender_username': msg.sender.username,
            'recipient_id': msg.recipient.id,
            'content': msg.content,
            'created_at': msg.created_at.isoformat(),
            'is_read': msg.is_read
        } for msg in messages])
        conversations[username]['messages_json'] = messages_json
    

    chat_requests = ChatRequest.objects.filter(
        recipient=request.user, 
        status='pending'
    ).order_by('-created_at')
    
    # Mark direct messages as read
    DirectMessage.objects.filter(
        recipient=request.user, 
        is_read=False
    ).update(is_read=True)
    
    return render(request, 'main/unified_chat.html', {
        'conversations': conversations,
        'chat_requests': chat_requests,
        'current_user_id': request.user.id
    })
    
    
    
    

# AUTH VIEWS  




@login_required(login_url='main:login')
def fortify_account(request):
    from .auth_2fa import generate_totp_secret, get_totp_uri, generate_qr_code, setup_totp_for_user
    try:
        from django_otp.plugins.otp_totp.models import TOTP_DEVICE
        if TOTP_DEVICE.objects.filter(user=request.user, confirmed=True).exists():
            return redirect('main:settings')
    except Exception as e:

        pass
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'generate':
            secret = generate_totp_secret()
            request.session['totp_secret'] = secret
            request.session['totp_step'] = 'verify'
            uri = get_totp_uri(request.user, secret)
            qr_code = generate_qr_code(uri)
            
            return render(request, 'main/setup_2fa.html', {
                'secret': secret,
                'qr_code': qr_code,
                'step': 'verify',
                'manual_entry_key': secret
            })
        
        elif action == 'verify':
            secret = request.session.get('totp_secret')
            otp_code = request.POST.get('otp_code', '').replace(' ', '')
            
            if not secret:
                return redirect('main:setup_2fa')
            
            import pyotp
            totp = pyotp.TOTP(secret)
            if totp.verify(otp_code, valid_window=1):
                # Setup the device
                setup_totp_for_user(request.user, secret)
                from .auth_2fa import confirm_totp_device
                confirm_totp_device(request.user)
                

                request.session.pop('totp_secret', None)
                request.session.pop('totp_step', None)
                
                return render(request, 'main/setup_2fa.html', {
                    'success': True,
                    'message': '2FA has been successfully enabled!'
                })
            else:
                return render(request, 'main/setup_2fa.html', {
                    'error': 'Invalid code. Please try again.',
                    'step': 'verify',
                    'secret': secret,
                    'manual_entry_key': secret
                })
    
    return render(request, 'main/setup_2fa.html', {'step': 'start'})







@login_required(login_url='main:login')
def unlock_vault(request):
    from .auth_2fa import disable_totp
    
    try:
        from django_otp.plugins.otp_totp.models import TOTP_DEVICE
        if not TOTP_DEVICE.objects.filter(user=request.user, confirmed=True).exists():
            return redirect('main:settings')
    except Exception as e:
        return redirect('main:settings')
    
    if request.method == 'POST':
        password = request.POST.get('password', '')
        

        from django.contrib.auth import authenticate
        if authenticate(username=request.user.username, password=password):
            disable_totp(request.user)
            return render(request, 'main/disable_2fa.html', {
                'success': True,
                'message': '2FA has been successfully disabled.'
            })
        else:
            return render(request, 'main/disable_2fa.html', {
                'error': 'Invalid password. Please try again.'
            })
    
    return render(request, 'main/disable_2fa.html')







def vault_entry(request):
    username = request.session.get('2fa_username')
    user_id = request.session.get('2fa_user_id')
    
    if not username or not user_id:
        return redirect('main:login')
    
    if request.method == 'POST':
        otp_code = request.POST.get('otp_code', '').replace(' ', '')
        
        try:
            user = User.objects.get(id=user_id, username=username)
        except User.DoesNotExist:
            return render(request, 'main/login_2fa.html', {
                'error': 'User not found.'
            })
        
        from .auth_2fa import verify_totp
        if verify_totp(user, otp_code):
            login(request, user)
            request.session.pop('2fa_username', None)
            request.session.pop('2fa_user_id', None)
            
            return redirect('main:post_list')
        else:
            return render(request, 'main/login_2fa.html', {
                'error': 'Invalid authentication code. Please try again.',
                'username': username
            })
    
    return render(request, 'main/login_2fa.html', {
        'username': username
    })
