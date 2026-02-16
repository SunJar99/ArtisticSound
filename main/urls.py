from django.urls import path
from . import views

app_name = 'main'

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('home/', views.post_list, name='post_list'),
    path('post/<int:pk>/', views.post_detail, name='post_detail'),
    path('create/', views.create_post, name='create_post'),
    path('jobs/', views.jobs, name='jobs'),
]
