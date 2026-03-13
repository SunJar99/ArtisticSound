from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.db.models import Q
from .models import Post, Project, JoinRequest, Message, Comment, DirectMessage, UserProfile
from .forms import CustomUserCreationForm, PostForm, ProjectForm, JoinRequestForm, MessageForm, CommentForm, DirectMessageForm

def home(request):
    return render(request, 'main/home.html')

def register(request):
    if request.user.is_authenticated:
        return redirect('main:post_list')
    
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('main:post_list')
    else:
        form = CustomUserCreationForm()
    return render(request, 'main/register.html', {'form': form})

def post_list(request):
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

def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    return render(request, 'main/post_detail.html', {'post': post})

def create_post(request):
    if not request.user.is_authenticated:
        return redirect('main:register')
    
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('main:post_detail', pk=post.pk)
    else:
        form = PostForm()
    return render(request, 'main/create_post.html', {'form': form})

def project_list(request):
    projects = Project.objects.filter(is_open=True)
    selected_categories = request.GET.getlist('category')  # Get multiple categories
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

def project_detail(request, pk):
    project = get_object_or_404(Project, pk=pk)
    return render(request, 'main/project_detail.html', {'project': project})

def create_project(request):
    if not request.user.is_authenticated:
        return redirect('main:register')
    
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.author = request.user
            project.save()
            return redirect('main:project_detail', pk=project.pk)
    else:
        form = ProjectForm()
    return render(request, 'main/create_project.html', {'form': form})

def jobs(request):
    return render(request, 'main/jobs.html')

def login_view(request):
    if request.user.is_authenticated:
        return redirect('main:post_list')
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('main:post_list')
    else:
        form = AuthenticationForm()
    return render(request, 'main/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('main:home')


@login_required(login_url='main:login')
def request_to_join(request, pk):
    project = get_object_or_404(Project, pk=pk)
    
    # Check if user already requested
    existing_request = JoinRequest.objects.filter(project=project, user=request.user).first()
    
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
        form = JoinRequestForm(request.POST)
        if form.is_valid():
            join_req = form.save(commit=False)
            join_req.project = project
            join_req.user = request.user
            join_req.save()
            return redirect('main:project_detail', pk=project.pk)
    else:
        form = JoinRequestForm()
    
    return render(request, 'main/join_project.html', {
        'project': project,
        'form': form
    })


@login_required(login_url='main:login')
def join_requests(request):
    # Get all pending join requests for projects created by this user
    pending_requests = JoinRequest.objects.filter(
        project__author=request.user,
        status='pending'
    ).order_by('-created_at')
    
    return render(request, 'main/join_requests.html', {
        'pending_requests': pending_requests
    })


@login_required(login_url='main:login')
def chat_view(request, request_id):
    join_request = get_object_or_404(JoinRequest, pk=request_id)
    
    # Check if user is either creator or applicant
    if request.user != join_request.project.author and request.user != join_request.user:
        return redirect('main:home')
    
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.join_request = join_request
            message.sender = request.user
            message.save()
            return redirect('main:chat', request_id=request_id)
    else:
        form = MessageForm()
    
    # Mark messages as read
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
def approve_request(request, request_id):
    join_req = get_object_or_404(JoinRequest, pk=request_id)
    
    if request.user != join_req.project.author:
        return redirect('main:home')
    
    join_req.status = 'approved'
    join_req.save()
    
    # Send approval message
    Message.objects.create(
        join_request=join_req,
        sender=request.user,
        content=f"Your request to join '{join_req.project.title}' has been approved!"
    )
    
    return redirect('main:chat', request_id=request_id)


@login_required(login_url='main:login')
def reject_request(request, request_id):
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


@login_required(login_url='main:login')
def get_notification_count(request):
    # Get count of unread messages for the user
    count = Message.objects.filter(
        join_request__project__author=request.user,
        is_read=False
    ).count()
    return {'unread_count': count}


@login_required(login_url='main:login')
def my_join_requests(request):
    # Get all join requests made by this user
    my_requests = JoinRequest.objects.filter(user=request.user).order_by('-created_at')
    
    return render(request, 'main/my_join_requests.html', {
        'my_requests': my_requests
    })


@login_required(login_url='main:login')
def inbox(request):
    # Get all conversations for the user (both sent requests and incoming requests)
    
    # Requests sent by user (as applicant)
    sent_requests = JoinRequest.objects.filter(user=request.user).order_by('-updated_at')
    
    # Requests received by user (as project creator)
    received_requests = JoinRequest.objects.filter(project__author=request.user).order_by('-updated_at')
    
    # Combine and get last message for each
    conversations = []
    
    for join_req in sent_requests:
        last_message = Message.objects.filter(join_request=join_req).order_by('-created_at').first()
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
        last_message = Message.objects.filter(join_request=join_req).order_by('-created_at').first()
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
    
    # Sort by most recent message
    conversations.sort(
        key=lambda x: x['last_message'].created_at if x['last_message'] else x['join_request'].updated_at,
        reverse=True
    )
    
    return render(request, 'main/inbox.html', {
        'conversations': conversations
    })