from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.db.models import Q
from .models import Post, Project
from .forms import CustomUserCreationForm, PostForm, ProjectForm

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

