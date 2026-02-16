from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import Post
from .forms import CustomUserCreationForm, PostForm

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

def jobs(request):
    return render(request, 'main/jobs.html')
